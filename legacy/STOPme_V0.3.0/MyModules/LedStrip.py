import random
import threading
import time

import flux_led

SCAN_TIME = 5
MAX_RETRIES = 5
RETRY_WAIT = 30

class MyFluxLed(flux_led.WifiLedBulb):
    def __init__(self, ipaddr):
        super().__init__(ipaddr)
        self.status_flag = ""
        self.manual_off_flag = None
        self.remote_off_flag = None
        self.manual_off()

    def set_status(self, status):
        self.status_flag = status
        if status == "IDLE":
            self.manual_off_flag = True
            self.remote_off_flag = False
        if status == "OFF":
            self.manual_off_flag = False
            self.remote_off_flag = True

    def get_status(self):
        return self.status_flag

    def manual_off(self):
        self.setRgbw(0, 0, 0, 0)
        self.set_status("IDLE")

    def is_remote_off(self):
        self.refreshState()
        if not self.isOn():
            self.set_status("OFF")
            return True
        else:
            self.set_status("IDLE")
            return False

class LedThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.name = "LedThread"
        self.stop_flag = False
        self.action_flag = False
        self.led_strip = None
        self.pattern_list = [key for key,value in flux_led.pattern.PresetPattern.__dict__.items() if isinstance(value, int)]
        self.pattern = None
        self.current_effect = None

    def find_device(self):
        scanner = flux_led.BulbScanner()
        retries = 0
        devices = []

        while not self.stop_flag:
            while len(devices) == 0 and retries < MAX_RETRIES:
                devices = scanner.scan(SCAN_TIME)
                retries += 1
                if len(devices) == 0:
                    print("No devices found. Retrying")
            if len(devices) == 0:
                print("Max retries reached. Waiting...")
                time.sleep(RETRY_WAIT)
                retries = 0
                continue
            for device in devices:
                if device['id'] == '249494129187' and device['model'] == 'AK001-ZJ21412':
                    self.led_strip = MyFluxLed(device['ipaddr'])
                    print("Connected to Led strip")
                    return
            devices = []


    def run(self):
        print("LED thread running")

        while not self.stop_flag:
            if self.led_strip is None:
                self.find_device()
                if self.led_strip is None:
                    print("Failed to find device")
                    continue

            self.led_strip.turnOn()

            while not self.stop_flag:
                if not self.led_strip.is_remote_off():
                    with self.lock:
                        if self.action_flag and self.current_effect:
                            self.led_strip.set_effect(effect=self.current_effect, speed=100)
                time.sleep(2)




    def start_action(self, timeout=0, speeds=100):
        with self.lock:
            self.action_flag = True
            self.current_effect = random.choice(self.pattern_list)
        while self.led_strip is None:
            time.sleep(1)

        self.led_strip.set_effect(effect=self.current_effect, speed = speeds)

        if timeout != 0:
            time.sleep(timeout)
            self.stop_action()
        else:
            while self.action_flag is not False:
                time.sleep(1)


    def stop_action(self):
        with self.lock:
            self.action_flag = False
        if self.led_strip:
            self.led_strip.manual_off()

    def stop(self):
        self.stop_flag = True
        self.led_strip.turnOff()



