import os
import threading
import time

from blue_st_sdk.manager import ManagerListener
from blue_st_sdk.node import NodeListener, NodeStatus
from blue_st_sdk.feature import FeatureListener
from bluepy.btle import BTLEDisconnectError

from MyModules.EventLogger import Log
from MyModules.LedStrip import LedThread
from MyModules.MetaMotion import MetaWearThread
from MyModules.BleLock import bluetooth_scan_lock

from playsound import playsound

USER = os.getlogin()

AUDIO_STATIONARY = f"/home/{USER}/Desktop/file_audio_progetto/stationary.mp3"
AUDIO_WALKING = f"/home/{USER}/Desktop/file_audio_progetto/walking.mp3"
AUDIO_WALKING_FAST = f"/home/{USER}/Desktop/file_audio_progetto/walking_fast.mp3"
AUDIO_RUNNING = f"/home/{USER}/Desktop/file_audio_progetto/running.mp3"
ACTION_NOT_RECOGNISED = f"/home/{USER}/Desktop/file_audio_progetto/action_not_recognise.mp3"
audio1 = f"/home/{USER}/Desktop/file_audio_progetto/temperature_down.mp3"
audio2 = f"/home/{USER}/Desktop/file_audio_progetto/temperature_up.mp3"




class MyManagerListener(ManagerListener):
    # Notifica l'inizio o la fine della ricerca
    def on_discovery_change(self, manager, enabled):
        print("Discovery %s." % ('started' if enabled else 'stopped'))

    def on_node_discovered(self, manager, node):
        print("New device discovered: %s." % (node.get_name()))


class MyNodeListener(NodeListener):
    def on_status_change(self, node, new_status, old_status):
        print("Status changed from %s to %s." % (old_status, new_status))

    # Notifica la connessione a un dispositivo
    def on_connect(self, node):
        print("Device %s connected." % (node.get_name()))
        print("Node status : %s" % node.get_status())

    # Notifica la disconnessione da un dispositivo, sia volontaria che involontaria
    def on_disconnect(self, node, unexpected=False):
        print("Device %s disconnected %s." % \
            (node.get_name(), ' unexpectedly' if unexpected else ''))
        if unexpected:
            print("Node status: %s" % node.get_status())


class MyFeatureListenerTemperature(FeatureListener):
    def __init__(self):
        super().__init__()
        self.limit = 32
        self.change = 0
        self.data = 0
        self.log = None

    def on_update(self, feature, sample):
        if self.log is None:
            self.log = Log(feature)
        self.data = sample.get_data()[0]
        print(self.data)
        self.temp_limit_alert(self.data, self.limit)

    def temp_limit_alert(self, temp, limit):
        if temp < limit:
            if self.change != 1:
                playsound(audio1)
                self.log.add_entry("La temperatura è SOTTO la soglia")
                self.change = 1

        if temp >= limit:
            if self.change != 2:
                playsound(audio2)
                self.log.add_entry("La temperatura è SOPRA la soglia")
                self.change = 2

class MyFeatureListenerActivity(FeatureListener):
    def __init__(self):
        super().__init__()
        self.log = None
        self.led_thread = LedThread()
        self.led_thread.start()
        self.meta_thread = MetaWearThread()
        self.meta_thread.start()


    def on_update(self, feature, sample):
        if self.log is None:
            self.log = Log(feature)
        # print(feature)
        activity = sample.get_data()[0]
        if activity == 1:
            print("YOU ARE STATIONARY")
            playsound(AUDIO_STATIONARY)
            self.log.add_entry("STATIONARY")
            self.led_thread.start_action(timeout=5)
        elif activity == 2:
            print("YOU ARE WALKING")
            playsound(AUDIO_WALKING)
            self.log.add_entry("WALKING")
            self.meta_thread.set_vibration(40, 1000)
            self.led_thread.start_action(timeout=5)
        elif activity == 3:
            print("YOU ARE WALKING FAST")
            playsound(AUDIO_WALKING_FAST)
            self.log.add_entry("WALKING FAST")
            self.meta_thread.set_vibration(70, 1000)
            self.led_thread.start_action(timeout=5)
        elif activity == 4:
            print("YOU ARE RUNNING")
            playsound(AUDIO_RUNNING)
            self.log.add_entry("RUNNING")
            self.meta_thread.set_vibration(100, 1000)
            self.led_thread.start_action(timeout=5)
        else:
            print(feature)
            playsound(ACTION_NOT_RECOGNISED)
            self.log.add_entry("ACTION NOT RECOGNISED")


class BlueCoinThread(threading.Thread):
    def __init__(self, node, node_listener, feature, feature_listener, task_id):
        super().__init__()
        self.name = "BlueCoinThread"
        self.node = node
        self.node_listener = node_listener
        self.feature_listener = feature_listener
        self.feature = feature
        self.reconnection_manager = BlueCoinReconnectionManager(node)
        self.task_id = task_id
        self.stop_flag = False

    def run(self):
        self.connect()
        while not self.stop_flag:
            print("BlueCoin thread n.%s is running" % self.task_id)
            self.get_data()
        self.node.disconnect()

    def stop(self):
        self.stop_flag = True

    def connect(self):
        node = self.node
        node.add_listener(self.node_listener)
        print('Connecting to %s...' % (node.get_name()))
        while node.connect() is not True:
            print('Connection failed. Retry\n')
        print("Connection to %s successful" % node.get_name())

        self.feature.add_listener(self.feature_listener)


    def get_data(self):
        self.node.enable_notifications(self.feature)
        while not self.stop_flag:
            if self.node.wait_for_notifications(0.05):
                print(self.node.get_name())
            elif self.node.get_status() != NodeStatus.CONNECTED:
                self.node.disable_notifications(self.feature)
                self.reconnection_manager.reconnect()
                self.node.enable_notifications(self.feature)
        self.node.disable_notifications(self.feature)
        self.feature.remove_listener(self.feature_listener)


class BlueCoinReconnectionManager:
    def __init__(self, node):
        print("Reconnection manager instantiated")
        self._node = node

    def get_node(self):
        return self._node

    def reconnect(self):
        node = self.get_node()
        node_name = node.get_name()
        print("Trying to re-establish connection to device %s" % node_name)
        while True:
            print("Attempting reconnection to %s" % node_name)
            try:
                if not node.connect():
                    print("Reconnection to %s failed" % node_name)
                    print(node.get_status())
                else:
                    print("Reconnection to %s successful" % node_name)
                    print(node.get_status())
                    break

            except BTLEDisconnectError:
                print("Reconnection failed due to an exception")
            time.sleep(1)
