# config.py
# Extract configuration variables from config.yaml file to python
#
# Author: Francesco Urru
# GitHub: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

import yaml
from pathlib import Path
from os.path import expanduser

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
try:
    with open(CONFIG_PATH, 'r') as f:
        CONFIG = yaml.safe_load(f) or {}
    if not isinstance(CONFIG, dict):
        CONFIG = {}
except Exception:
    CONFIG = {}

# LOGGER
def get_log_path():
    """
    Returns the resolved base log path, expanding "~" to the users home directory.
    :return:
    """
    default_base = str(Path.home() / "Documents" / "STOPME" / "logs")
    return str(Path(expanduser(CONFIG.get("log_base_path", default_base))))

def actuation_details_enabled() -> bool:
    return CONFIG.get("enable_actuation_detail", True)

def system_log_enabled() -> bool:
    return CONFIG.get("enable_system_log", True)

def debug_system_console_enabled() -> bool:
    return CONFIG.get("debug_system_console", False)

def debug_event_console_enabled()-> bool:
    return CONFIG.get("debug_event_console", False)

# METAMOTION
def get_metamotion_config() -> dict:
    """
    Returns the MetaMotion configuration dictionary from config.yaml
    :return:
    """
    return CONFIG.get("metamotion", {})

# SPEAKER
def get_speaker_config() -> dict:
    """
    Returns the Speaker configuration dictionary from config.yaml
    :return:
    """
    return CONFIG.get("speaker", {})

# LED_STRIP
def get_led_strip_config() -> dict:
    """
    Returns the Led_Strip configuration dictionary from config.yaml
    :return:
    """
    return CONFIG.get("led_strip", {})

# BLUECOIN
def get_bluecoin_config() -> list[dict]:
    """
    Returns the list of BlueCoin sensors configurations from config.yaml
    each entry has:
        id: bc_left, bc_right
        name: STOPmeL, STOPmeR
    """
    return CONFIG.get("bluecoins", []) or []

# IMU CONFIGURATION
def get_sync_config() -> dict:
    """
    Returns synchronization configuration dictionary from config.yaml
    Keys:
        max_skew_ms (int): max desync between wrists
        stale_ms (int): drops old wrist data if the other wrist doesn't send data
    """
    sync_cfg = CONFIG.get("sync", {}) or {}
    return {
        "max_skew_ms": int(sync_cfg.get("max_skew_ms", 25)),
        "stale_ms": int(sync_cfg.get("stale_ms", 100))
    }

# BUFFER CONFIGURATION
def get_buffer_config() -> dict:
    """
    Returns Buffer configuration dictionary from config.yaml.
    Keys:
        window_size (int): buffer window size in samples
        hop_size (int): buffer overlap samples
        calibration_windows (int): number of windows to wait for calibration
        gate_actuation_during_calibration (bool): prevents actuation if not calibrated
    """
    buff_cfg = CONFIG.get("buffer", {}) or {}
    return {
        "window_size": int(buff_cfg.get("window_size", 150)),
        "overlap": int(buff_cfg.get("overlap", 75)),
        "debug_print_buffer": bool(buff_cfg.get("debug_print_buffer", True)),
        "debug_print_features": bool(buff_cfg.get("debug_print_features", True))
    }

# ACTUATION LANGUAGE CONFIGURATION
def get_language_config() -> str:
    """
    Returns the language selected for actuation from config.yaml.
    Check for "ita" or "eng". Set "eng" as default if not present or not correct
    """
    language = CONFIG.get("language", "").lower()
    return language if language in {"ita", "eng"} else "eng"

# POLICY CONFIGURATION
def get_policy_attempts() -> int:
    """
    Returns policy configuration dictionary from config.yaml
    KEYS:
        attempts:       number of attemps before changing actuator
    """
    policy_config = CONFIG.get("policy", {}) or {}
    return int(policy_config.get("attempts", 5))

# QUEUE SIZE
def get_event_queue_size() -> int:
    """
    Returns event queue size from config.yaml
    """
    return int(CONFIG.get("event_queue_size", 5))


