# led_strip.py
# Actuator module for Wi-Fi LED strip control using flux_led
#
# Author: Francesco Urru
# GitHub: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

import threading
import time
from typing import Optional, Tuple, List

import flux_led
from flux_led import BulbScanner
from flux_led.pattern import PresetPattern

from utils.logger import log_system
from utils.config import get_led_strip_config

# Device scanning function

def scan_led_devices(timeout: int = 5) -> List[str]:
    """
    Scans for Wi-Fi LED devices using flux_led and returns their IP addresses.

    Args:
        timeout (int): Duration of the network scan in seconds.

    Returns:
        List[str]: A list of IP addresses corresponding to discovered LED devices.
    """
    log_system(f"[LED Scanner] Starting WiFi scan for {timeout} seconds...")
    ip_list: List[str] = []

    try:
        scanner = BulbScanner()
        devices = scanner.scan(timeout)

        for device in devices:
            ipaddr = device.get('ipaddr')
            model = device.get('model')
            if ipaddr:
                log_system(f"[LED Scanner] Found device: {ipaddr} (model: {model})")
                ip_list.append(ipaddr)

        if not ip_list:
            log_system("[LED Scanner] No LED devices found.", level="WARNING")

    except Exception as exc:
        log_system(f"[LED Scanner] Scan error: {exc}", level="ERROR")

    return ip_list

#LedStripThread

class LedThread(threading.Thread):
    """
    Thread for managing a Wi-Fi LED strip using flux_led.

    Args:
        ip_address (str): The IP address of the target LED strip.
    """

    def __init__(self, ip_address: str):
        super().__init__(daemon=True)
        self.ip_address = ip_address

        self._stop_event = threading.Event()
        self._event = threading.Event()
        self._disconnect_event = threading.Event()

        self._pattern: Optional[int] = None
        self._color: Optional[Tuple[int, int, int, int]] = None
        self._speed: int = 100
        self._intensity: int = 100

        self._bulb: Optional[flux_led.WifiLedBulb] = None

        config = get_led_strip_config()
        self._fast_retry_attempts: int = config.get("fast_retry_attempts", 5)
        self._retry_interval: int = config.get("retry_interval", 5)
        self._retry_sleep: int = config.get("retry_sleep", 60)

    def run(self) -> None:
        log_system(f"[LedStrip: {self.ip_address}] Thread started")
        self._connect()
        self._wait_for_event()

    def _wait_for_event(self) -> None:
        while not self._stop_event.is_set():
            self._event.wait()

            if self._stop_event.is_set():
                if self._bulb:
                    self._turn_off()
                break

            if self._disconnect_event.is_set():
                self._disconnect_event.clear()
                self._reconnection_attempts()

            if self._bulb:
                self._process_action()

            self._event.clear()

    def _connect(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._bulb = flux_led.WifiLedBulb(self.ip_address)
                self._bulb.refreshState()
                self._connection_feedback()
                log_system(f"[LedStrip: {self.ip_address}] Connected successfully")
                return
            except Exception as exc:
                log_system(f"[LedStrip: {self.ip_address}] Connection error: {exc}", level="ERROR")
                time.sleep(self._retry_interval)

    def _connection_feedback(self) -> None:
        try:
            self._bulb.setRgbw(255, 255, 255, 0, brightness=50)
            time.sleep(0.3)
            self._bulb.setRgbw(0, 0, 0, 0)
            time.sleep(0.2)
            self._bulb.setRgbw(255, 255, 255, 0, brightness=50)
            time.sleep(0.3)
            self._bulb.setRgbw(0, 0, 0, 0)
        except Exception:
            pass

    def _reconnection_attempts(self) -> None:
        log_system(f"[LedStrip: {self.ip_address}] Starting reconnection attempts...")

        for attempt in range(1, self._fast_retry_attempts + 1):
            if self._stop_event.is_set():
                return
            if self._try_reconnect():
                return
            log_system(f"[LedStrip: {self.ip_address}] Fast retry {attempt}/{self._fast_retry_attempts} failed", level="WARNING")
            time.sleep(self._retry_interval)

        log_system(f"[LedStrip: {self.ip_address}] Switching to slow retries every {self._retry_sleep}s", level="WARNING")
        while not self._stop_event.is_set():
            if self._try_reconnect():
                return
            log_system(f"[LedStrip: {self.ip_address}] Slow retry failed", level="WARNING")
            time.sleep(self._retry_sleep)

    def _try_reconnect(self) -> bool:
        try:
            self._bulb = flux_led.WifiLedBulb(self.ip_address)
            self._bulb.refreshState()
            self._connection_feedback()
            log_system(f"[LedStrip: {self.ip_address}] Reconnected successfully")
            return True
        except Exception:
            return False

    def execute(
        self,
        *,
        pattern: Optional[int] = None,
        color: Optional[Tuple[int, int, int, int]] = None,
        intensity: int = 100,
        speed: int = 100,
    ) -> None:
        """Trigger an effect or solid color on the LED strip."""
        self._pattern = pattern
        self._color = color
        self._intensity = max(0, min(intensity, 100))
        self._speed = max(1, min(speed, 100))
        self._event.set()

    def _process_action(self) -> None:
        try:
            if self._color:
                r, g, b, w = self._color
                log_system(f"[LedStrip: {self.ip_address}] Setting color ({r},{g},{b},{w}) intensity={self._intensity}%")
                self._bulb.setRgbw(r, g, b, w, brightness=self._intensity)
            elif self._pattern is not None:
                log_system(f"[LedStrip: {self.ip_address}] Setting pattern {self._pattern} speed={self._speed}% intensity={self._intensity}%")
                self._bulb.set_effect(effect=self._pattern, speed=self._speed, brightness=self._intensity)

        except Exception as exc:
            log_system(f"[LedStrip: {self.ip_address}] Action error: {exc}", level="ERROR")

    def _turn_off(self) -> None:
        try:
            if self._bulb:
                self._bulb.turnOff()
                self.execute(color=(0,0,0,0))
                log_system(f"[LedStrip: {self.ip_address}] Turned off")
        except Exception as exc:
            log_system(f"[LedStrip: {self.ip_address}] TurnOff error: {exc}", level="ERROR")

    def stop(self) -> None:
        self._stop_event.set()
        self._event.set()
        self.join()
        log_system(f"[LedStrip: {self.ip_address}] Thread stopped")
