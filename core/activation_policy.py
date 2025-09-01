# activation_policy.py
# Defines which actuators to activate based on the events.
#
# Author: Francesco Urru
# Repository: https://github.com/frarvo/STOPme
# License: MIT


from typing import List, Dict, Optional
import random
from utils.audio_paths import AudioLibrary
from utils.config import get_language_config, get_policy_attempts

TAG_NO_CLASS = 0
TAG_NON_DANGEROUS = 1
TAG_DANGEROUS = 2
TAG_NON_STEREOTIPY = 3


class StereotipyActivationPolicy:
    """
    Event-driven loop:
      - For tag 1,2: emit ONE actuation per event.
      - If the next event is still 1 or 2, retry on the SAME actuator (variation).
      - After N attempts on that actuator, switch actuator (random different if possible).
      - If the tag changes to 0 or 3 after an actuation, set the CURRENT actuator as
        "successful". Next time the same tag appears, choose this actuator.
    """

    def __init__(self, actuator_ids: List[str]):
        self.actuator_ids = list(actuator_ids or [])
        self.retries_per_actuator = max(1, int(get_policy_attempts()))
        self.rng = random.Random()

        # Language for the speaker
        self.lang = get_language_config()

        # State across events
        self._current_tag: Optional[int] = None
        self._current_actuator: Optional[str] = None
        self._attempts_on_current: int = 0
        self._variation_idx: int = 0

        # Remember "what worked" per severity (1 or 2)
        self._last_success_actuator: Dict[int, Optional[str]] = {
            TAG_NON_DANGEROUS: None,
            TAG_DANGEROUS: None,
        }

        # Variations
        self._led_variants_mild = [
            {"color": (255, 255, 255, 0), "intensity": 50, "speed": 100},
            {"color": (180, 220, 255, 0), "intensity": 60, "speed": 100},
            {"color": (200, 255, 200, 0), "intensity": 70, "speed": 100},
        ]
        self._led_variants_strong = [
            {"color": (255,   0,   0, 0), "intensity": 100, "speed": 100},
            {"color": (255, 128,   0, 0), "intensity": 100, "speed": 100},
            {"color": (255,   0, 255, 0), "intensity": 100, "speed": 100},
        ]
        self._meta_variants_mild = [
            {"duty": 40, "duration": 700},
            {"duty": 55, "duration": 800},
            {"duty": 70, "duration": 900},
        ]
        self._meta_variants_strong = [
            {"duty": 100, "duration": 900},
            {"duty": 100, "duration": 1100},
            {"duty": 100, "duration": 1300},
        ]
        self._spk_key_mild = f"NON_DANGEROUS_{self.lang.upper()}"
        self._spk_key_strong = f"DANGEROUS_{self.lang.upper()}"

    def handle(self, event: dict) -> Optional[Dict]:
        if not self.actuator_ids:
            return None

        tag = self._parse_tag(event.get("stereotipy_tag"))

        # If we’re back to non-stereotypy: mark success for the previous positive tag and reset.
        if tag in (TAG_NO_CLASS, TAG_NON_STEREOTIPY) or tag is None:
            if self._current_tag in (TAG_NON_DANGEROUS, TAG_DANGEROUS) and self._current_actuator:
                # Remember that this actuator "worked" for that severity
                self._remember_success(self._current_tag, self._current_actuator)
            self._reset_state()
            return None

        # First positive event (or severity changed): choose actuator
        if self._current_tag != tag or self._current_actuator is None:
            self._current_tag = tag
            preferred = self._last_success_actuator.get(tag)
            if preferred in self.actuator_ids:
                self._current_actuator = preferred
            else:
                self._current_actuator = self._pick_random(exclude=None)
            self._attempts_on_current = 0
            self._variation_idx = 0

        # If we reached the attempt limit on this actuator, switch now
        if self._attempts_on_current >= self.retries_per_actuator:
            self._current_actuator = self._pick_random(exclude=self._current_actuator)
            self._attempts_on_current = 0
            self._variation_idx = 0

        # Build actuation
        mild = (tag == TAG_NON_DANGEROUS)
        result = self._params_for(self._current_actuator, mild=mild, variation_index=self._variation_idx)
        if not result:
            # Fallback: pick another actuator immediately
            self._current_actuator = self._pick_random(exclude=self._current_actuator)
            self._attempts_on_current = 0
            self._variation_idx = 0
            result = self._params_for(self._current_actuator, mild=mild, variation_index=self._variation_idx)
            if not result:
                return None

        # Record attempt; the *next* incoming event will determine success/failure
        self._attempts_on_current += 1
        self._variation_idx += 1
        return result

    # ----- helpers -----
    def _parse_tag(self, raw) -> Optional[int]:
        try:
            return int(raw)
        except Exception:
            return None

    def _pick_random(self, exclude: Optional[str]) -> Optional[str]:
        candidates = self.actuator_ids
        if exclude and len(candidates) > 1:
            candidates = [a for a in candidates if a != exclude]
        return self.rng.choice(candidates) if candidates else None

    def _params_for(self, actuator_id: Optional[str], *, mild: bool, variation_index: int) -> Optional[Dict]:
        if not actuator_id:
            return None

        if actuator_id.startswith("led_"):
            variants = self._led_variants_mild if mild else self._led_variants_strong
            params = variants[variation_index % len(variants)]

        elif actuator_id.startswith("speaker_"):
            key = self._spk_key_mild if mild else self._spk_key_strong
            try:
                file_path = str(getattr(AudioLibrary, key))
            except AttributeError:
                file_path = str(getattr(AudioLibrary, "MISSING_FILE"))
            params = {"file": file_path}

        elif actuator_id.startswith("meta_"):
            variants = self._meta_variants_mild if mild else self._meta_variants_strong
            params = variants[variation_index % len(variants)]

        else:
            return None

        return {"actuator_id": actuator_id, "params": params}

    def _remember_success(self, tag: int, actuator_id: str):
        # store the actuator as preferred for that tag
        if tag in (TAG_NON_DANGEROUS, TAG_DANGEROUS):
            self._last_success_actuator[tag] = actuator_id

    def _reset_state(self):
        self._current_tag = None
        self._current_actuator = None
        self._attempts_on_current = 0
        self._variation_idx = 0