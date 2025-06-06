# activation_policy.py
# Defines activation policies for temperature and activity events.
#
# Author: Francesco Urru
# Repository: https://github.com/frarvo/STOPme
# License: MIT

import random
from typing import List, Dict, Optional
from utils.audio_paths import AudioLibrary


class TemperatureActivationPolicy:
    """
    Chooses a random actuator from the list and maps the temperature level
    to an action consistent with that actuator type.
    """

    def __init__(self, actuator_ids: List[str]):
        """
        Args:
            actuator_ids (List[str]): List of actuator IDs (e.g., 'led_192...', 'speaker_XX:XX...', 'meta_XX:XX...')
        """
        self.actuator_ids = actuator_ids

        # Mapping LED
        self.color_map = {
            "LOW": (0, 255, 0, 0),          # Verde
            "MEDIUM": (255, 255, 0, 0),     # Giallo
            "HIGH": (255, 165, 0, 0),       # Arancione
            "CRITICAL": (255, 0, 0, 0)      # Rosso
        }

        # Mapping Speaker
        self.audio_map = {
            "LOW": AudioLibrary.TEMPERATURE_LOW,
            "MEDIUM": AudioLibrary.TEMPERATURE_MEDIUM,
            "HIGH": AudioLibrary.TEMPERATURE_HIGH,
            "CRITICAL": AudioLibrary.TEMPERATURE_CRITICAL
        }

        # Mapping MetaMotion
        self.vibration_map = {
            "LOW": {"duty": 30, "duration": 1000},
            "MEDIUM": {"duty": 50, "duration": 1000},
            "HIGH": {"duty": 80, "duration": 1000},
            "CRITICAL": {"duty": 100, "duration": 1000}
        }

    def handle(self, event:dict) -> Optional[Dict]:
        """
        Process incoming temperature event and select an actuator to trigger.

        Args:
            event (dict): Event dictionary with keys 'event' and 'source'

        Returns:
            Optional[Dict]: {
                "actuator_id": str,
                "params": dict
            }
        """
        event_value = event.get("event")
        if not self.actuator_ids:
            return None

        actuator_id = random.choice(self.actuator_ids)

        if actuator_id.startswith("led_"):
            params = {"color": self.color_map.get(event_value, (255, 255, 255, 0))}

        elif actuator_id.startswith("speaker_"):
            params = {"file": self.audio_map.get(event_value, "default.mp3")}

        elif actuator_id.startswith("meta_"):
            params = self.vibration_map.get(event_value, {"duty": 50, "duration": 500})

        else:
            # Unknown actuator type
            return None

        return {
            "actuator_id": actuator_id,
            "params": params
        }

    def reset(self):
        """
        No state is kept, so nothing to reset.
        """
        pass


class ActivityActivationPolicy:
    """
    Controls actuation logic for activity events:
    - Uses the same actuator up to 3 consecutive times
    - Rotates to the next actuator after 3 attempts
    - Resets cycle on new event or sensor
    - Stops actuation when 'STATIONARY' is received

    LED: white color, variable speed (25-100%)
    MetaMotion: fixed duration, variable intensity (25-100%)
    Speaker: mapped audio file per activity
    """

    def __init__(self, actuator_ids: List[str]):
        """
        Initialize policy with actuator rotation and scaling maps.

        Args:
            actuator_ids (List[str]): Ordered list of available actuator IDs.
        """
        self.actuator_ids = actuator_ids
        self.index = 0
        self.attempts = 0
        self.last_event = None
        self.last_sensor = None

        self.speed_map = {
            "STATIONARY": 25,
            "WALKING": 50,
            "WALKING_FAST": 75,
            "RUNNING": 100
        }

        self.intensity_map = {
            "STATIONARY": 25,
            "WALKING": 50,
            "WALKING_FAST": 75,
            "RUNNING": 100
        }

        self.duration = 1000  # ms for MetaMotion haptic motor

    def handle(self, event: dict) -> Optional[Dict]:
        """
        Process an incoming activity event and select an actuator to trigger.

        Args:
            event (dict): Event dictionary with keys 'event' and 'source'.

        Returns:
            dict: {
                "actuator_id": str,
                "params": dict (for .execute())
            }
        """
        event_value = event.get("event")
        sensor_id = event.get("source")

        if event_value == "STATIONARY" or event_value is None:
            self.reset()
            return None

        # Reset cycle on new event or sensor
        if event_value != self.last_event or sensor_id != self.last_sensor:
            self.reset()
            self.last_event = event_value
            self.last_sensor = sensor_id

        actuator_id = self.actuator_ids[self.index]

        if actuator_id.startswith("led_"):
            params = {
                "color": (255, 255, 255, 0),
                "speed": self.speed_map.get(event_value, 50),
                "intensity": 100
            }

        elif actuator_id.startswith("speaker_"):
            try:
                file_path = str(getattr(AudioLibrary, event_value))
            except AttributeError:
                file_path = str(AudioLibrary.STATIONARY)
            params = {"file": file_path}

        elif actuator_id.startswith("meta_"):
            duty = self.intensity_map.get(event_value, 50)
            params = {"duty": duty, "duration": self.duration}

        else:
            return None

        # Rotate after 3 attempts
        self.attempts += 1
        if self.attempts >= 3:
            self.attempts = 0
            self.index = (self.index + 1) % len(self.actuator_ids)

        return {
            "actuator_id": actuator_id,
            "params": params
        }

    def reset(self):
        """
        Resets internal state and cycle position.
        """
        self.index = 0
        self.attempts = 0
        self.last_event = None
        self.last_sensor = None