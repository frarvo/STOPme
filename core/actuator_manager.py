# actuator_manager.py
# Manages the lifecycle, initialization and control of actuator devices (LED, speaker, MetaMotionRL).
#
# Author: Francesco Urru
# GitHub: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

import threading
import time
from typing import Dict

from actuators.led_strip import scan_led_devices, LedThread
from actuators.metamotion import scan_metamotion_devices, MetaMotionThread
from actuators.speaker import scan_speaker_devices, SpeakerThread
from utils.logger import log_system
from utils.lock import bluetooth_scan_lock

class ActuatorManager:
    """
    Manages discovery, initialization, and control of actuator devices
    such as LED strips, MetaMotion haptics, and bluetooth speakers.

    Provides a unified interface for triggering action on any actuator.
    """

    def __init__(self):
        """
        Initializes the actuator manager with an empty actuator registry.
        """
        self.actuators: Dict[str, threading.Thread] = {}
        log_system("[ActuatorManager] Initialized")

    def scan_and_initialize(self):
        """
        Scans for available actuator devices (LED, MetaMotion, Speaker),
        creates their threads, and starts them.
        """
        log_system("[ActuatorManager] Starting actuator scan and initialization.")

        # Bluetooth scan protected by global lock
        with bluetooth_scan_lock:
            speaker_addresses = scan_speaker_devices(5)
            time.sleep(2)
            metamotion_addresses = scan_metamotion_devices(5)
            time.sleep(2)
            led_addresses = scan_led_devices(10)
            time.sleep(2)

        # Creates speaker threads
        for mac in speaker_addresses:
            actuator_id = f"speaker_{mac}"
            thread = SpeakerThread(mac)
            thread.start()
            self.actuators[actuator_id] = thread
            log_system(f"[ActuatorManager] Speaker initialized: {actuator_id}")
            time.sleep(2)

        # Creates metamotion threads
        for mac in metamotion_addresses:
            actuator_id = f"meta_{mac}"
            thread = MetaMotionThread(mac)
            thread.start()
            self.actuators[actuator_id] = thread
            log_system(f"[ActuatorManager] MetaMotion initialized: {actuator_id}")
            time.sleep(2)

        # Creates LED threads
        for ip in led_addresses:
            actuator_id = f"led_{ip}"
            thread = LedThread(ip)
            thread.start()
            self.actuators[actuator_id] = thread
            log_system(f"[ActuatorManager] LED initialized: {actuator_id}")
            time.sleep(2)

        log_system("[ActuatorManager] Actuators initialization complete")

    def trigger(self, actuator_id: str, action_type: str, **kwargs):
        """
        Triggers an action on the specified actuator.

        Args:
            actuator_id (str): ID of the actuator (e.g., 'led_192.168.1.100', 'meta_A1:B2:C3:D4:E5:F6')
            action_type (str): Type of action to perform (currently unused, reserved for future)
            **kwargs: Additional parameters for the action.
        """
        actuator = self.actuators.get(actuator_id)

        if not actuator:
            log_system(f"[ActuatorManager] Attempted to trigger unknown actuator: {actuator_id}", level="WARNING")
            return

        try:
            actuator.execute(**kwargs)
            log_system(f"[ActuatorManager] Triggered action on {actuator_id}: {kwargs}")
        except Exception as e:
            log_system(f"[ActuatorManager] Error triggering actuator {actuator_id}: {e}", level="ERROR")

    def stop_all(self):
        """
        Stops all actuator threads and clears the registry.
        """
        log_system("[ActuatorManager] Stopping all actuator threads...")

        for actuator_id, thread in self.actuators.items():
            try:
                thread.stop()
                log_system(f"[ActuatorManager] Stopped actuator: {actuator_id}")
            except Exception as e:
                log_system(f"[ActuatorManager] Error stopping actuator {actuator_id}: {e}", level="ERROR")

        self.actuators.clear()
        log_system("[ActuatorManager] All actuator threads stopped.")



