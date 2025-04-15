import yaml
from pathlib import Path
from os.path import expanduser

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

with open(CONFIG_PATH, 'r') as f:
    CONFIG = yaml.safe_load(f)

# LOGGER
def get_log_path():
    """
    Returns the resolved base log path, expanding "~" to the users home directory.
    :return:
    """
    return str(Path(expanduser(CONFIG["log_base_path"])))

def get_thresholds(sensor_type):
    return CONFIG["thresholds"].get(sensor_type, {})

def get_device_config(device_id):
    return CONFIG["devices"].get(device_id, {})

def actuation_details_enabled() -> bool:
    return CONFIG.get("log_actuation_details", True)

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
