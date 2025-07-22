# recognizers/temperature.py
# Recognizer module for temperature-based event classification
#
# Author: Francesco Urru
# Repository: https://github.com/frarvo/STOPme
# License: MIT

from datetime import datetime
from utils.logger import log_event
from utils.event_queue import get_temperature_queue


class TemperatureRecognizer:
    """
    Recognizes temperature threshold crossings and logs corresponding events,
    also dispatches structured events into the temperature queue.
    """

    def __init__(self, thresholds: dict[str, float], source: str):
        """
        Initialize with threshold values.

        Args:
            thresholds (dict): Keys are 'low', 'medium', 'high'.
            source (str): source is the BlueCoin of origin
        """
        self.low = thresholds.get("low", 28.0)
        self.medium = thresholds.get("medium", 32.0)
        self.high = thresholds.get("high", 36.0)
        self.source = source
        self._last_state = None
        self.queue = get_temperature_queue()

    def process(self, value):
        """
        Analyze the temperature and log the current state based on thresholds.
        Push the event to the shared temperature queue if state changed.

        Args:
            value: Temperature value from the sensor.
        """
        timestamp = datetime.now().isoformat()

        if value < self.low:
            state = "LOW"
        elif value < self.medium:
            state = "MEDIUM"
        elif value < self.high:
            state = "HIGH"
        else:
            state = "CRITICAL"

        if state != self._last_state:
            log_event(
                timestamp=timestamp,
                feature_type="temperature",
                event=state,
                actuations=[],
                source=self.source
            )

            self.queue.put({
                "type": "temperature",
                "event": state,
                "source": self.source,
                "timestamp": timestamp
            })

        self._last_state = state