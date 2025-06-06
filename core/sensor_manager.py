# sensor_manager.py
# Manager for initializing and coordinating BlueCoin sensor threads
#
# Author: Francesco Urru
# Github: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

from blue_st_sdk.features.feature_activity_recognition import FeatureActivityRecognition
from blue_st_sdk.features.feature_temperature import FeatureTemperature

from sensors.bluecoin import scan_bluecoin_devices, BlueCoinThread
from sensors.feature_listeners import TemperatureFeatureListener, ActivityFeatureListener
from recognizers.temperature import TemperatureRecognizer
from recognizers.activity import ActivityRecognizer
from utils.config import get_bluecoin_config
from utils.logger import log_system
from utils.lock import device_scan_lock, device_connection_lock


class SensorManager:
    """
    Manages initialization and coordination of BlueCoin sensor threads.

    This manager:
    - Loads configuration from config.yaml
    - Scans for available BlueCoin nodes (scan_sensors)
    - Initializes and starts sensor threads based on config (initialize_sensors)
    """

    def __init__(self):
        """Initializes the SensorManager and loads BlueCoin configuration."""
        self.threads = []
        self.config = get_bluecoin_config()
        self.nodes = []
        self.node_map = {}
        log_system("[SensorManager] Initialized")

    def scan_sensors(self):
        """Performs BLE scan for BlueCoin nodes and stores results internally."""
        log_system("[SensorManager] Starting BLE scan for BlueCoin nodes")
        with device_scan_lock:
            self.nodes = scan_bluecoin_devices(timeout=5)
        log_system(f"[SensorManager] Found {len(self.nodes)} node(s)")

        # Build device map: device_name -> node
        for node in self.nodes:
            try:
                name = node.get_name()
                if name:
                    self.node_map[name] = node
            except Exception as e:
                log_system(f"[SensorManager] Error retrieving name for scanned node: {e}", level="WARNING")

        # Check for mismatches between config names and node names
        config_names = {entry.get("name") for entry in self.config if entry.get("name")}
        discovered_names = set(self.node_map.keys())

        missing = config_names - discovered_names
        extra = discovered_names - config_names

        if missing:
            log_system(f"[SensorManager] Configured sensors not found during scan: {missing}", level= "WARNING")
        if extra:
            log_system(f"[SensorManager] Discovered nodes not in config will be ignored: {extra}", level= "WARNING")

    def initialize_sensors(self):
        """
        Initializes sensor threads using the scanned nodes and loaded configuration.
        Each thread corresponds to a feature and sensor ID defined in the config.
        """
        if not self.node_map:
            log_system("[SensorManager] No scanned nodes available. Run scan_sensors() first.", level="WARNING")
            return

        for sensor_cfg in self.config:
            sensor_id = sensor_cfg.get("id")
            expected_name = sensor_cfg.get("name")
            feature_type = sensor_cfg.get("feature")

            if expected_name is None:
                log_system(f"[SensorManager] Missing 'name' in configuration for sensor id '{sensor_id}'", level="ERROR")
                continue
            node = self.node_map.get(expected_name)
            if not node:
                log_system(f"[SensorManager] Node with name '{expected_name}' not found; Skipping sensor id '{sensor_id}'", level= "WARNING")
                continue

            # Select feature and recognizer
            if feature_type == "temperature":
                recognizer = TemperatureRecognizer(thresholds=sensor_cfg.get("thresholds", {}), source=sensor_id)
                feature_listener = TemperatureFeatureListener(recognizer, sensor_id)
                feature_choice = FeatureTemperature
            elif feature_type == "activity":
                recognizer = ActivityRecognizer(source=sensor_id)
                feature_listener = ActivityFeatureListener(recognizer, sensor_id)
                feature_choice = FeatureActivityRecognition
            else:
                log_system(f"[SensorManager] Unknown feature type: {feature_type}", level="ERROR")
                continue

            # Attempt to retrieve feature from node
            try:
                feature = node.get_feature(feature_choice)
            except Exception as e:
                log_system(f"[SensorManager] Error retrieving feature '{feature_type}' for node '{expected_name}'", level="ERROR")

            if not feature:
                log_system(f"[SensorManager] Feature '{feature_type}' not available on node {sensor_id}", level="WARNING")
                continue

            # Initialize and start the thread
            try:
                with device_connection_lock:
                    thread = BlueCoinThread(
                        node=node,
                        feature=feature,
                        feature_listener=feature_listener,
                        device_id=sensor_id
                    )
                    thread.start()
                    self.threads.append(thread)

                log_system(f"[SensorManager] Sensor initialized: {sensor_id}")
            except Exception as e:
                log_system(f"[SensorManager] Error initializing thread for sensor id '{sensor_id}', name: '{expected_name}'", level="ERROR")
                continue

        log_system("[SensorManager] All sensor threads initialized")

    def stop_all(self):
        """Stops all active sensor threads and clears the registry."""
        log_system("[SensorManager] Stopping all sensor threads...")
        for thread in self.threads:
            try:
                thread.stop()
            except Exception as e:
                log_system(f"[SensorManager] Error stopping thread for device '{thread.device_id}: {e}", level="ERROR")
        self.threads.clear()
        log_system("[SensorManager] All sensor threads stopped.")