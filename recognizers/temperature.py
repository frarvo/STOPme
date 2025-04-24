
# recognizers/temperature.py
# Recognizer module for temperature-based event classification
#
# Author: Francesco Urru
# Repository: https://github.com/frarvo/STOPme
# License: MIT


from utils.logger import log_system


class TemperatureRecognizer:
    """
    Recognizes temperature threshold crossings and logs corresponding events.
    """

    def __init__(self, thresholds: dict[str, float]):
        """
        Initialize with threshold values.

        Args:
            thresholds (dict): Keys are 'low', 'medium', 'high'.
        """
        self.low = thresholds.get("low", 28.0)
        self.medium = thresholds.get("medium", 32.0)
        self.high = thresholds.get("high", 36.0)
        self._last_state = None

    def recognize(self, value: float):
        """
        Analyze the temperature and log the current state based on thresholds.

        Args:
            value (float): Temperature value from the sensor.
        """
        if value < self.low:
            state = "LOW"
        elif value < self.medium:
            state = "MEDIUM"
        elif value < self.high:
            state = "HIGH"
        else:
            state = "CRITICAL"

        if state != self._last_state:
            log_system(f"[TempRecognizer] Temperature {value:.2f}°C → State changed to {state}")
            self._last_state = state
