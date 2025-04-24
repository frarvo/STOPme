# logger.py
# Actuator module for logging both sensor events and internal system state
#
# Author: Francesco Urru
# GitHub: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

import os
from datetime import datetime
from pathlib import Path
from utils.config import get_log_path, actuation_details_enabled, system_log_enabled, debug_system_console_enabled, debug_event_console_enabled

def _ensure_dir(path: Path):
    """Ensures that a given directory path exists. Creates it if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def _get_day_folder(base_dir: Path) -> Path:
    """
    Returns the path to the log directory named after today's date (DD-MM-YYYY).
    Creates the directory if it does not exist.
    """
    day_folder = datetime.now().strftime("%d-%m-%Y")
    full_path = base_dir / day_folder
    _ensure_dir(full_path)
    return full_path

def log_event(timestamp: str, feature_type: str, event: str, actuations: list, source: str):
    """
    Logs a sensor event and triggered actuations into both .log and .csv formats.

    Parameters:
        timestamp (str): timestamp of the event
        feature_type (str): e.g., 'temperature', 'activity'
        event (str): semantic event value (e.g., 'WALKING', 'TEMP_HIGH')
        actuations (list): list of dicts with 'target' and 'params'
        source (str): e.g., 'BC_Temperature', 'BC_Activity_Recognition'
    """
    log_base = Path(get_log_path())
    folder = _get_day_folder(log_base)

    date_str = datetime.fromisoformat(timestamp).strftime("%d-%m-%Y")
    time_str = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")

    # ACTUATION STRING
    # actions = list of actuators and their parameters
    actions = []
    for action in actuations:
        target_name = action["target"].upper() #target is the actuator. e.g. LED, METAMOTION, SPEAKER

        if actuation_details_enabled():
            # if event details enabled creates a string (formatted) with actuation type and parameters
            params = action.get("params", {}) # dict with params of a single actuator
            param_str = ", ".join(f"{key}={value}" for key,value in params.items()) # turn dict params into string
            formatted = f"{target_name}({param_str})"
        else:
            # else the string contains only the actuator name
            formatted = target_name

        actions.append(formatted)

    action_str = ", ".join(actions)


    # LOG FILE
    log_filename = f"Event_Diary_{source}.log"
    log_path = folder / log_filename

    line_txt = f"[{date_str} {time_str}] - {feature_type.upper()} - {event} - {action_str}\n"

    with open(log_path, "a") as f:
        f.write(line_txt)

    if debug_event_console_enabled():
        print(line_txt.strip())

    # CSV FILE
    csv_filename = f"Event_Diary_{source}.csv"
    csv_path = folder / csv_filename
    header = "date,timestamp,feature,event,actuation\n"
    line_csv = f"{date_str},{time_str},{feature_type},{event},\"{action_str}\"\n"

    write_header = not csv_path.exists()
    with open(csv_path, "a") as f:
        if write_header:
            f.write(header)
        f.write(line_csv)

def log_system(message: str, level: str = "INFO"):
    """
    Logs a system-level message into 'System_Log.log' in the folder of the day.

    Parameters:
        message (str): The message to log
        level (str): Logging level (INFO, WARNING, ERROR)
    """

    date = datetime.now().strftime("%d-%m-%Y")
    time = datetime.now().strftime("%H:%M:%S")
    line = f"[{date} {time}] - {level.upper()} - {message}\n"

    if debug_system_console_enabled():
        print(line.strip())
        
    if not system_log_enabled():
        return

    log_base = Path(get_log_path())
    folder = _get_day_folder(log_base)
    filepath = folder / "System_Log.log"
    
    with open(filepath, "a") as f:
        f.write(line)

