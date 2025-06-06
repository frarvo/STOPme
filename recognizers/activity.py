# recognizers/activity.py
# Recognizer module for activity classification events
#
# Author: Francesco Urru
# Repository: https://github.com/frarvo/STOPme
# License: MIT

from datetime import datetime
from utils.logger import log_event
from utils.event_queue import get_activity_queue


class ActivityRecognizer:
    """
    Recognizes activity classes and logs corresponding events.
    Dispatches structured activity events to the shared queue.
    """

    def __init__(self, source: str):
        """
        Initialize the recognizer for a specific sensor source.

        Args:
            source (str): Identifier of the BlueCoin source device.
        """
        self.label = None
        self.source = source
        self.queue = get_activity_queue()

    def process(self, activity_class):
        """
        Interpret activity class from sensor and push semantic event to the activity queue.

        Args:
            activity_class: Activity label from BlueCoin:
                            1 = Stationary, 2 = Walking,
                            3 = Walking Fast, 4 = Running
        """
        timestamp = datetime.now().isoformat()

        labels = {
            0: "NO_ACTIVITY",
            1: "STATIONARY",
            2: "WALKING",
            3: "WALKING_FAST",
            4: "RUNNING",
            5: "BIKING",
            6: "DRIVING",
            7: "STAIRS",
            8: "ERROR"
        }

        self.label = labels.get(activity_class, "UNKNOWN")

        log_event(
            timestamp=timestamp,
            feature_type="activity",
            event=self.label,
            actuations=[],
            source=self.source
        )

        self.queue.put({
            "type": "activity",
            "value": self.label,
            "source": self.source,
            "timestamp": timestamp
        })