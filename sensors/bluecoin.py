# bluecoin.py
# BLE interface module for BlueCoin sensor devices (STMicroelectronics)
#
# Author: Francesco Urru
# Github: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

import time
import threading
from blue_st_sdk.manager import Manager, ManagerListener
from blue_st_sdk.node import NodeStatus, NodeListener
from bluepy.btle import BTLEDisconnectError

from utils.logger import log_system
from utils.lock import device_reconnection_lock


class BlueCoinManagerListener(ManagerListener):
    """ Custom listener for BlueCoin discovery. Logs events during BLE scan. """
    def on_discovery_change(self, manager, enabled):
        log_system(f"[BlueCoin Scanner] Discovery {'started' if enabled else 'stopped'}.")

    def on_node_discovered(self, manager, node):
        log_system(f"[BlueCoin Scanner] Found node: {node.get_name()} - {node.get_tag()}")

class BlueCoinNodeListener(NodeListener):
    """ Custom listener for BlueCoin Nodes. Logs events during BLE connections and disconnections. """
    def on_connect(self, node):
        log_system(f"[BlueCoin node] {node.get_name()}: {node.get_tag()} connected")

    def on_disconnect(self, node, unexpected=False):
        log_system(f"[BlueCoin node] {node.get_name()}: {node.get_tag()} disconnected {'unexpectedly' if unexpected else ' '}")

    def on_status_change(self, node, new_status, old_status):
        log_system(f"[BlueCoin node] Status changed from {old_status} to {new_status}")

def scan_bluecoin_devices(timeout: int = 5) -> list:
    """
    Performs a BLE scan to discover nearby BlueCoin nodes.

    Args:
        timeout (int): Duration in seconds for the scan.

    Returns:
        list: List of compatible BlueCoin nodes discovered during the scan.
    """
    nodes = []

    log_system(f"[BlueCoin Scanner] Starting BLE scan for {timeout} seconds...")
    manager = Manager.instance()
    listener = BlueCoinManagerListener()
    manager.add_listener(listener)

    try:
        manager.discover(timeout)
        nodes = manager.get_nodes()
    except Exception as e:
        log_system(f"[BlueCoin Scanner] Error during discovery: {e}", level="ERROR")

    if not nodes:
        log_system("[BlueCoin Scanner] No BlueCoin devices found.", level="WARNING")
    else:
        log_system(f"[BlueCoin Scanner] Total devices found: {len(nodes)}")

    return nodes

class BlueCoinThread(threading.Thread):
    """
    Thread for managing a single BlueCoin device connection and feature listening.

    Attributes:
        node: BlueST Node object representing the BlueCoin device.
        node_listener: Listener for connection and disconnection events.
        feature_listener: Listener for feature updates.
        feature: Feature to subscribe to.
        device_id: Identifier string for logging purposes.
    """

    def __init__(self, node, feature, feature_listener, device_id):
        super().__init__(daemon=True)
        self.node = node
        self.node_listener = BlueCoinNodeListener()
        self.feature = feature
        self.feature_listener = feature_listener
        self.device_id = device_id
        self.stop_event = threading.Event()

    def run(self):
        log_system(f"[BlueCoin Thread: {self.device_id}] Thread started.")
        self._connect()
        self._start_notifications()
        self._listen()

    def _connect(self):
        self.node.add_listener(self.node_listener)
        while not self.node.connect():
            log_system(f"[BlueCoin Thread: {self.device_id}] Connection failed, retrying...", level="WARNING")
            time.sleep(1)
        log_system(f"[BlueCoin Thread: {self.device_id}] Connected successfully.")
        self.feature.add_listener(self.feature_listener)

    def _start_notifications(self):
        self.node.enable_notifications(self.feature)

    def _stop_notifications(self):
        self.node.disable_notifications(self.feature)
        self.feature.remove_listener(self.feature_listener)

    def _listen(self):
        while not self.stop_event.is_set():
            try:
                if self.node.get_status() != NodeStatus.CONNECTED:
                    self._handle_reconnection()
                else:
                    self.node.wait_for_notifications(0.05)
            except BTLEDisconnectError:
                log_system(f"[BlueCoin Thread: {self.device_id}] BTLE exception caught", level="ERROR")
                self._handle_reconnection()

        self._cleanup()

    def _handle_reconnection(self):
        self._stop_notifications()
        with device_reconnection_lock:
            while not self.stop_event.is_set():
                try:
                    log_system(f"[BlueCoin Thread: {self.device_id}] Attempting reconnection...")
                    if self.node.connect():
                        log_system(f"[BlueCoin Thread: {self.device_id}] Reconnected successfully.")
                        self.feature.add_listener(self.feature_listener)
                        self._start_notifications()
                        return
                except BTLEDisconnectError:
                    log_system(f"[BlueCoin Thread: {self.device_id}] Reconnection failed, retrying...", level="WARNING")
                time.sleep(2)

    def stop(self):
        self.stop_event.set()
        self.join()
        log_system(f"[BlueCoin Thread: {self.device_id}] Thread stopped.")

    def _cleanup(self):
        self._stop_notifications()
        if self.node.get_status() == NodeStatus.CONNECTED:
            self.node.disconnect()
            log_system(f"[BlueCoin Thread: {self.device_id}] Disconnected cleanly.")