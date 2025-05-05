# audio_paths.py
# Centralized symbolic mapping for audio files used by the speaker actuator
#
# Author: Francesco Urru
# GitHub: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

from pathlib import Path
from utils.logger import log_system

class AudioLibrary:
    """
    Dynamically provides access to named audio files with automatic validation.
    Accessing AudioLibrary.alert will return the path, and log a warning if the file is missing.
    """

    _base_path = Path(__file__).resolve().parent.parent / "assets" / "audio"
    _files = {
        "STATIONARY" : "stationary.mp3",
        "WALKING" : "walking.mp3",
        "WALKING_FAST" : "walking_fast.mp3",
        "RUNNING" : "running.mp3",
        "TEMPERATURE_DOWN" : "temperature_down.mp3",
        "TEMPERATURE_UP" : "temperature_up.mp3"
    }

    def __getattr__(self, name):
        """
        Called automatically when accessing a missing attribute like AudioLibrary.alert
        """
        if name in self._files:
            path = self._base_path / self._files[name]
            if not path.exists():
                log_system(f"[AudioLibrary] Missing audio file: {path}", level="WARNING")
            return path
        raise AttributeError(f"[AudioLibrary] Unknown audio key: '{name}'")

# Singleton instance
AudioLibrary = AudioLibrary()