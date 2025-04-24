# recognizers/activity.py
# Recognizer module for activity classification events
#
# Author: Francesco Urru
# Repository: https://github.com/frarvo/STOPme
# License: MIT


from utils.logger import log_system


class ActivityRecognizer:
    """
    Recognizes activity classes and logs or triggers actuations accordingly.
    """

    def __init__(self):
        self._last_state = None

    def recognize(self, activity_class: int):
        """
        Interpret activity class from sensor.

        Args:
            activity_class (int): Activity label from BlueCoin:
                                  1 = Stationary, 2 = Walking,
                                  3 = Walking Fast, 4 = Running
        """
        labels = {
            1: "STATIONARY",
            2: "WALKING",
            3: "WALKING_FAST",
            4: "RUNNING"
        }

        label = labels.get(activity_class, "UNKNOWN")

        if label != self._last_state:
            log_system(f"[ActivityRecognizer] Activity changed to {label}")
            self._last_state = label