import os
import subprocess
import time


class Speaker:

    def __init__(self, mac_address):
        self._mac_address = mac_address
        self._scan_on_command = "bluetoothctl scan on"
        self._scan_off_command = "bluetoothctl scan off"
        self._connect_command = "bluetoothctl connect"
        self._disconnect_command = "bluetoothctl disconnect"

    @staticmethod
    def scan(timeout=10):
        process = None
        try:
            process = subprocess.Popen(["bluetoothctl"], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            process.stdin.write("scan on\n")
            process.stdin.flush()

            print(f"Scanning for {timeout} seconds. Press Ctrl+C to stop.")
            time.sleep(timeout)

            process.stdin.flush()
            print("Scanning stopped.")
        except KeyboardInterrupt:
            print("Scan interrupted by user")
        finally:
            process.stdin.close()
            process.terminate()
            process.wait()

    def connect(self):
        os.system(self._connect_command + " " + self._mac_address)
        print("Speaker connected")

    def disconnect(self):
        os.system(self._disconnect_command + " " + self._mac_address)
        print("Speaker disconnected")