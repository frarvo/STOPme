# metamotion.py
# Actuator module for vibration control using MetaMotionRL BLE device
#
# Author: Francesco Urru
# Github: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

######

import threading
import time
from mbientlab.metawear import MetaWear, libmetawear
from mbientlab.warble import WarbleException
from utils.config import get_metamotion_config
from actuators.logger import log_system
from bluepy.btle import Scanner

def scan_metamotion_devices(timeout: int = 5) -> list[str]:
    """
    Scans for nearby MetaMotion BLE devices and returns their MAC addresses.

    Args:
        timeout (int): Duration of the BLE scan in seconds.

    Returns:
        List[str]: A list of MAC addresses (strings) corresponding to MetaWear devices.
    """
    log_system(f"[MetaMotion Scanner] Starting BLE scan for {timeout} seconds...")
    mac_list = []

    scanner = Scanner()
    devices = scanner.scan(timeout)

    for dev in devices:
        name = dev.getValueText(9)  # 9 = Complete Local Name
        if name == "MetaWear":
            log_system(f"[MetaMotion Scanner] Found MetaWear at {dev.addr}")
            mac_list.append(dev.addr)

    if not mac_list:
        log_system("[MetaMotion Scanner] No MetaWear devices found.", level="WARNING")

    return mac_list

class MetaMotionThread(threading.Thread):
    """
    Thread for managing BLE connection and vibration control on a MetaMotion device.

    This thread:
    - Connects to a MetaMotion device using a known MAC address
    - Waits for external vibration commands
    - Handles automatic disconnection and reconnection
    - Executes motor vibration with configurable intensity and duration

    Attributes:
        mac_address (str): BLE MAC address of the target device
        vibration_duty (int): Intensity of the motor (0-100)
        vibration_time (int): Duration in milliseconds
    """

    def __init__(self, mac_address: str):
        """
        Initializes the MetaMotionThread with a specific BLE MAC address
        :param mac_address: (str) The BLE MAC address of the MetaMotion device
        """
        super().__init__(daemon=True)
        self.mac_address = mac_address
        self.stop_event = threading.Event()
        self.event = threading.Event()
        self.disconnect_event = threading.Event()
        self.vibration_duty = 100
        self.vibration_time = 500
        self.device = None
        meta_config = get_metamotion_config()
        self.fast_retry_attempts = meta_config.get("fast_retry_attempts", 10)
        self.retry_interval = meta_config.get("retry_interval", 5)
        self.retry_sleep = meta_config.get("retry_sleep", 60)

    def run(self):
        """
        Main thread entry point. Connects to the MetaMotion device and enters the main event loop.
        :return:
        """
        log_system(f"[MetaMotion: {self.mac_address}] Thread started")
        self._connect_meta_device()
        self._wait_for_event()

    def _connect_meta_device(self):
        """
        Attempts to establish a BLE connection to the MetaMotion device using the stored MAC address.
        On success, sets up a disconnection callback and performs connection feedback.
        :return:
        """
        addr = self.mac_address
        self.device = MetaWear(addr)
        self.device.on_disconnect = lambda status: self._on_disconnection(status)

        while not self.device.is_connected:
            try:
                self.device.connect()
                time.sleep(1)
            except WarbleException as e:
                log_system(f"[MetaMotion: {addr}] Connection failed: {e}", level="ERROR")

        log_system(f"[MetaMotion: {addr}] Connected successfully")
        self._connection_feedback()

    def _connection_feedback(self):
        """
        Executes a brief double vibration sequence to confirm successful connection to the device.
        :return:
        """
        libmetawear.mbl_mw_haptic_start_motor(self.device.board, 100, 200)
        time.sleep(0.250)
        libmetawear.mbl_mw_haptic_start_motor(self.device.board, 100, 200)
        time.sleep(1)

    def _wait_for_event(self):
        """
        Main loop that waits for external vibration commands or disconnection events.
        Processes vibration requests and handles reconnection when needed.
        :return:
        """
        while not self.stop_event.is_set():
            self.event.wait()

            if self.stop_event.is_set():
                if self.device and self.device.is_connected:
                    self._disconnect_device()
                break

            if self.disconnect_event.is_set():
                self.disconnect_event.clear()
                self._reconnection_attempts()

            if self.device.is_connected:
                self._process_vibration()

            self.event.clear()

    def _process_vibration(self):
        """
        Triggers the vibration motor using the current duty cycle and duration time.
        :return:
        """
        if self.device.is_connected:
            log_system(f"[MetaMotion: {self.mac_address}] Vibrating {self.vibration_time}ms at {self.vibration_duty}%")
            libmetawear.mbl_mw_haptic_start_motor(self.device.board, self.vibration_duty, self.vibration_time)

    def set_vibration(self, duty_cycle: int, time_ms: int):
        """
        Set the vibration parameters and signals the thread to process the request.
        :param duty_cycle: (int) Vibration intensity.
        :param time_ms: (int) Duration of the vibration in milliseconds.
        :return:
        """
        self.vibration_duty = duty_cycle
        self.vibration_time = time_ms
        self.event.set()

    def stop(self):
        """
        Stops the thread, disconnects the device if connected, and waits for termination.
        :return:
        """
        self.stop_event.set()
        self.event.set()
        self.join()
        log_system(f"[MetaMotion: {self.mac_address}] Thread stopped.")

    def _disconnect_device(self):
        """
        Safely disconnects the MetaMotion device if it is currently connected.
        :return:
        """
        try:
            if self.device and self.device.is_connected:
                self.device.disconnect()
                log_system(f"[MetaMotion: {self.mac_address}] Disconnected manually")
        except Exception as e:
            log_system(f"[MetaMotion: {self.mac_address}] Disconnection error: {e}", level="ERROR")

    def _on_disconnection(self, status):
        """
        Callback invoked by the MetaMotion API when the device disconnects.
        :param status:
        :return:
        """
        if status != 0:
            log_system(f"[MetaMotion: {self.mac_address}] Disconnected unexpectedly (status = {status})", level="WARNING")
            self.disconnect_event.set()
            self.event.set()
        else:
            log_system(f"[MetaMotion: {self.mac_address}] Disconnected successfully.")

    def execute(self, **kwargs):
        """
        Triggers the MetaMotion vibration motor with provided parameters.

        :param kwargs:
            duty (int): Motor intensity (default: 100)
            duration (int): Duration in milliseconds (default: 500)
        :return:
        """
        duty = kwargs.get("duty", 100)
        duration = kwargs.get("duration", 500)
        self.set_vibration(duty, duration)

    def _reconnection_attempts(self):
        """
        Attempts to reconnect to the MetaMotion device using a fast-retry strategy first, followed by
        a slower retry loop until reconnection succeeds or stop_event is set.
        :return:
        """
        log_system(f"[MetaMotion: {self.mac_address}] Starting reconnection procedure.")

        # Phase 1: fast retries
        for attempt in range(self.fast_retry_attempts):
            if self.stop_event.is_set():
                return
            try:
                self.device.connect()
                log_system(f"[MetaMotion: {self.mac_address}] Reconnected successfully.")
                return
            except Exception as e:
                log_system(f"[MetaMotion: {self.mac_address}] Retry {attempt + 1}/{self.fast_retry_attempts} failed: {e}", level="ERROR")
                time.sleep(self.retry_interval)

        # Phase 2: slow retries
        log_system(f"[MetaMotion: {self.mac_address}] All fast retries failed. Sleeping for {self.retry_sleep}s before retrying.")
        while not self.stop_event.is_set():
            try:
                self.device.connect()
                log_system(f"[MetaMotion: {self.mac_address}] Reconnected successfully.")
                return
            except Exception as e:
                log_system(f"[MetaMotion: {self.mac_address}] Slow retry failed: {e}", level="WARNING")
                time.sleep(self.retry_sleep)
