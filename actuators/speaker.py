# speaker.py
# Actuator module for Bluetooth speaker control and audio playback.
#
# Author: Francesco Urru
# GitHub: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

import threading
import subprocess
import time
from playsound import playsound
from actuators.logger import log_system
from utils.config import get_speaker_config


class SpeakerThread(threading.Thread):
    """
    Thread for managing Bluetooth speaker connection and audio playback.

    This thread:
    - Maintains a persistent Bluetooth connection with a known device
    - Auto-reconnects if the speaker becomes unavailable
    - Waits for external commands to play local audio files
    - Can be stopped gracefully from external code

    Attributes:
        mac_address (str): MAC address of the Bluetooth speaker
    """

    def __init__(self, mac_address: str):
        """
        Initializes the speaker thread and its synchronization primitives.
        :param mac_address: (str) MAC address of the Bluetooth speaker
        """
        super().__init__(daemon=True)
        self.mac_address = mac_address
        self.event = threading.Event()
        self.stop_event = threading.Event()
        self.file = None
        self.connected = False

        speaker_config = get_speaker_config()
        self.timeout = speaker_config.get("timeout", 5)
        self.fast_retry_attempts = speaker_config.get("fast_retry_attempts", 5)
        self.retry_interval = speaker_config.get("retry_interval", 5)
        self.retry_sleep = speaker_config.get("retry_sleep", 60)

    def run(self):
        """
        Main loop that ensures connection is maintained and audio playback is triggered when requested.
        """
        log_system(f"[Speaker: {self.mac_address}] Thread started")

        self._reconnection_attempts()

        while not self.stop_event.is_set():
            if not self._is_connected():
                self._reconnection_attempts()

            if self.event.is_set() and self.connected:
                try:
                    log_system(f"[Speaker: {self.mac_address}] Playing audio: {self.file}")
                    playsound(self.file)
                except Exception as e:
                    log_system(f"[Speaker: {self.mac_address}] Error during audio playback: {e}", level="ERROR")
                finally:
                    self.event.clear()

            time.sleep(1)

        self._disconnect()

    def execute(self, **kwargs):
        """
        Triggers playback of a local audio file on the connected speaker.

        Keyword Args:
            file (str): Path to the audio file to play
        """
        file = kwargs.get("file")
        if not file:
            log_system(f"[Speaker: {self.mac_address}] No audio file provided", level="WARNING")
            return
        self.file = file
        self.event.set()

    def stop(self):
        """
        Stops the thread and disconnects from the speaker.
        """
        self.stop_event.set()
        self.event.set()
        self.join()
        log_system(f"[Speaker: {self.mac_address}] Thread stopped")

    def _connect(self):
        """
        Attempts to connect to the Bluetooth speaker.
        """
        try:
            result = subprocess.run(
                ["bluetoothctl", "connect", self.mac_address],
                capture_output=True, text=True, timeout=self.timeout
            )
            if "Connection successful" in result.stdout:
                self.connected = True
                log_system(f"[Speaker: {self.mac_address}] Connected successfully")
            else:
                log_system(f"[Speaker: {self.mac_address}] Connection failed: {result.stdout}", level="WARNING")
                self.connected = False
        except Exception as e:
            log_system(f"[Speaker: {self.mac_address}] Exception during connection: {e}", level="ERROR")
            self.connected = False

    def _disconnect(self):
        """
        Disconnects from the Bluetooth speaker.
        """
        try:
            subprocess.run(
                ["bluetoothctl", "disconnect", self.mac_address],
                capture_output=True, text=True
            )
            self.connected = False
            log_system(f"[Speaker: {self.mac_address}] Disconnected")
        except Exception as e:
            log_system(f"[Speaker: {self.mac_address}] Exception during disconnection: {e}", level="ERROR")

    def _is_connected(self) -> bool:
        """
        Checks whether the speaker is currently connected.
        :return: True if connected, False otherwise
        """
        try:
            result = subprocess.run(
                ["bluetoothctl", "info", self.mac_address],
                capture_output=True, text=True
            )
            return "Connected: yes" in result.stdout
        except Exception as e:
            log_system(f"[Speaker: {self.mac_address}] Error checking status: {e}", level="ERROR")
            return False

    def _reconnection_attempts(self):
        """
        Attempts to reconnect to the speaker using fast and slow retry strategies.
        """
        log_system(f"[Speaker: {self.mac_address}] Starting reconnection procedure.")
        self._disconnect()

        # Fast retry attempts
        for attempt in range(self.fast_retry_attempts):
            if self.stop_event.is_set():
                return
            self._connect()
            if self.connected:
                log_system(f"[Speaker: {self.mac_address}] Reconnected successfully.")
                return
            else:
                log_system(f"[Speaker: {self.mac_address}] Retry {attempt + 1}/{self.fast_retry_attempts} failed", level="WARNING")
                time.sleep(self.retry_interval)

        # Slow retry loop
        log_system(f"[Speaker: {self.mac_address}] All fast retries failed. Retrying every {self.retry_sleep}s.")
        while not self.stop_event.is_set():
            self._connect()
            if self.connected:
                log_system(f"[Speaker: {self.mac_address}] Reconnected successfully.")
                return
            log_system(f"[Speaker: {self.mac_address}] Slow retry failed", level="WARNING")
            time.sleep(self.retry_sleep)
