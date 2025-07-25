# feature_listener.py
# Feature listener module for BlueCoin sensor data callbacks
#
# Author: Francesco Urru
# Github: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

from blue_st_sdk.feature import FeatureListener
from utils.logger import log_system


class TemperatureFeatureListener(FeatureListener):
    """
    Listens for temperature data updates from a BlueCoin feature and
    dispatches them to the assigned recognizer for threshold evaluation.
    """

    def __init__(self, recognizer, sensor_id: str):
        """
        Args:
            recognizer: Instance of TemperatureRecognizer.
            sensor_id (str): ID of the BlueCoin device this listener is bound to.
        """
        super().__init__()
        self.recognizer = recognizer
        self.sensor_id = sensor_id

    def on_update(self, feature, sample):
        try:
            data = sample.get_data()
            #print(f"[DEBUG] Data type: {type(data)} | Data: {data}")
            if not data or not isinstance(data, list) or len(data) < 1:
                log_system(f"[Temperature Listener: {self.sensor_id}] Invalid sample data: {data}", level="WARNING")
                return
            temperature = data[0]
            #log_system(f"[Temperature Listener: {self.sensor_id}] Received: {temperature:.2f}°C")
            self.recognizer.process(value=temperature)
        except Exception as e:
            import traceback
            log_system(f"[Temperature Listener: {self.sensor_id}] Exception: {type(e).__name__}: {e}\n{traceback.format_exc()}", level="ERROR")


class ActivityFeatureListener(FeatureListener):
    """
    Listens for activity classification updates from a BlueCoin feature and
    dispatches them to the assigned recognizer.
    """

    def __init__(self, recognizer, sensor_id: str):
        """
        Args:
            recognizer: Instance of ActivityRecognizer.
            sensor_id (str): ID of the BlueCoin device this listener is bound to.
        """
        super().__init__()
        self.recognizer = recognizer
        self.sensor_id = sensor_id

    def on_update(self, feature, sample):
        try:
            data = sample.get_data()
            #print(f"[DEBUG] Data type: {type(data)} | Data: {data}")
            if not data or not isinstance(data, list) or len(data) < 1:
                log_system(f"[Activity Listener: {self.sensor_id}] Invalid sample data: {data}", level="WARNING")
                return
            activity_code = data[0]
            #log_system(f"[Activity Listener: {self.sensor_id}] Activity code: {activity_code}")
            self.recognizer.process(activity_class = activity_code)
        except Exception as e:
            import traceback
            log_system(
                f"[Temperature Listener: {self.sensor_id}] Exception: {type(e).__name__}: {e}\n{traceback.format_exc()}",
                level="ERROR")