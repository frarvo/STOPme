import threading
import time

from mbientlab.metawear import MetaWear, libmetawear
from bluepy.btle import Scanner
from mbientlab.warble import WarbleException

from MyModules.BleLock import bluetooth_scan_lock


class MetaWearThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()
        self.event = threading.Event()
        self.disconnect_event = threading.Event()
        self.vibration_duty = 100
        self.vibration_time = 500
        self.meta_devices = []
        self.device = None
        self.scan_time = 5
        self.retries = 0
        self.MAX_RETRIES = 5
        self.RETRY_DELAY = 5
        self.RETRY_SLEEP = 60
    def start(self, timeout=5):
        self.scan_time = timeout
        super().start()

    def run(self):
        with bluetooth_scan_lock:
            self.scan_meta_devices()
        self.connect_meta_device()
        self.wait_for_event()

    def wait_for_event(self):
        while not self.stop_event.is_set():
            self.event.wait()  # Attende un evento

            if self.stop_event.is_set():
                if self.device.is_connected:
                    self.disconnect_device()
                break

            if self.disconnect_event.is_set():
                self.disconnect_event.clear()
                self.reconnection_attempts()

            if self.device.is_connected:
                self.process_vibration()
            self.event.clear()

    def scan_meta_devices(self):
        scanner = Scanner()
        metawear_devices = []

        while not metawear_devices: # Ripete tutto finchè non trova almeno un dispositivo MetaWear
            scanned_devices = scanner.scan(self.scan_time)

            for dev in scanned_devices: # Tra i dispositivi trovati tira fuori solo quelli MetaWear
                name = dev.getValueText(9)  # 9 = Complete Local Name
                if name == "MetaWear":
                    metawear_devices.append((name, dev.addr))

            if not metawear_devices: # Se non ci sono dispositivi MetaWear avverte. Il ciclo ricomincia
                print("No MetaWear devices found.")

        self.meta_devices = metawear_devices

    def connect_meta_device(self, address=None):
        # Se address è specificato, cerca quel dispositivo
        if address:
            device_info = next(((name, addr) for name, addr in self.meta_devices if addr == address), None)
            if not device_info:
                print(f"Device with address {address} not found. Connecting to first available device.")
                device_info = self.meta_devices[0]
        else:
            device_info = self.meta_devices[0]

        name, addr = device_info
        self.device = MetaWear(addr)
        self.device.on_disconnect = lambda status: self.on_disconnection(status)

        # Tenta di connettere fino a quando non ci riesce
        while not self.device.is_connected:
            try:
                self.device.connect()
                time.sleep(1)
            except WarbleException as e:
                print(f"Try failed for {addr}. Error: {e}. Retrying...")

        print(f"Connected successfully to {name} ({addr})")
        self._connection_feedback()


    def _connection_feedback(self):
        libmetawear.mbl_mw_haptic_start_motor(self.device.board, 100, 200)
        time.sleep(0.250)
        libmetawear.mbl_mw_haptic_start_motor(self.device.board, 100, 200)
        time.sleep(0.250)

    def process_vibration(self):
        if self.device.is_connected:
            print(f"Vibrating for {self.vibration_time/1000} seconds at {self.vibration_duty}% intensity")
            libmetawear.mbl_mw_haptic_start_motor(self.device.board, self.vibration_duty, self.vibration_time)

    def set_vibration(self, duty_cycle, time_ms):
        self.vibration_duty = duty_cycle
        self.vibration_time = time_ms
        self.event.set()

    def reconnection_attempts(self):
        print("Attempting reconnection to MetaMotion device")
        try:
            self.connect_meta_device()
            print("Reconnected successfully!")
        except Exception as e:
            print(f"Reconnection failed: {e}")

    def stop(self):
        self.stop_event.set()
        self.event.set()
        self.join()

    def disconnect_device(self):
        try:
            if self.device.is_connected:
                self.device.disconnect()
        except Exception as e:
            print(f"Error during manual disconnection: {e}")


    def on_disconnection(self, status):
        if status != 0:
            self.disconnect_event.set()
            self.event.set()
        else:
            print("Disconnection...")