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

def log_events(timestamp: str, feature_type: str, event: str, actuations: list, source: str):
    """
    Logs a sensor event with its duration and triggered actuations into both .log and .csv formats.

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


# Global variables to track the last logged event
_last_event_timestamp: datetime = None
_last_event_file: Path = None
_last_event_line_idx: int = None


# LOG event with duration
def log_event(timestamp: str,
              feature_type: str,
              event: str,
              actuations: list,
              source: str):
    """
    Registra un evento (senza durate) in due file: .log e .csv.
    Retroattivamente aggiorna l’evento precedente (nel file dove era stato scritto)
    aggiungendo la sua durata, calcolata come differenza tra il timestamp
    attuale e quello dell’ultimo evento, indipendentemente dal source.

    Parametri:
        timestamp (str): stringa ISO8601, es. "2025-06-06T10:38:16"
        feature_type (str): es. 'temperature' o 'activity'
        event (str): es. 'WALKING', 'TEMP_HIGH', ecc.
        actuations (list): lista di dict con chiavi 'target' e 'params'
        source (str): nome del sensore, es. 'BC_Temperature' o 'BC_Activity_Recognition'
    """
    global _last_event_timestamp, _last_event_file, _last_event_line_idx

    # Determines path folder for current source device
    log_base = Path(get_log_path())
    folder = _get_day_folder(log_base)

    log_filename = f"Event_Diary_{source}.log"
    log_path = folder / log_filename

    csv_filename = f"Event_Diary_{source}.csv"
    csv_path = folder / csv_filename

    # Convert timestam to datetime format
    now = datetime.fromisoformat(timestamp)
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H:%M:%S")

    # Build actuation string
    actions = []
    for action in actuations:
        target_name = action["target"].upper()
        if actuation_details_enabled():
            params = action.get("params", {})
            param_str = ", ".join(f"{k}={v}" for k, v in params.items())
            formatted = f"{target_name}({param_str})"
        else:
            formatted = target_name
        actions.append(formatted)
    action_str = ", ".join(actions)

    # Retroactive update of previous events on files .log e .csv to add duration
    if _last_event_timestamp is not None and _last_event_file is not None:
        # duration = now – _last_event_timestamp
        delta = now - _last_event_timestamp
        total_seconds = int(delta.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        duration_str = f"{minutes:02d}:{seconds:02d}"

        # Retroactive update .log
        prev_log_path = _last_event_file
        with open(prev_log_path, "r") as f_log:
            log_lines = f_log.readlines()

        # Add " - Duration: mm:ss" to the line _last_event_line_idx
        old_log_line = log_lines[_last_event_line_idx].rstrip("\n")
        log_lines[_last_event_line_idx] = old_log_line + f" - Duration: {duration_str}\n"

        with open(prev_log_path, "w") as f_log:
            f_log.writelines(log_lines)

        # Retroactive update .csv
        # Prepare CSV path relative to prev_log_path
        prev_csv_path = prev_log_path.with_suffix(".csv")

        if not prev_csv_path.exists():
            header = "date,timestamp,feature,event,actuation,duration\n"
            with open(prev_csv_path, "w") as f_csv:
                f_csv.write(header)

        with open(prev_csv_path, "r") as f_csv:
            csv_lines = f_csv.readlines()

        # Data line on a csv file start from index 1. Index 0 is the header.
        # Line to modify: _last_event_line_idx + 1
        prev_csv_idx = _last_event_line_idx + 1
        old_csv_line = csv_lines[prev_csv_idx].rstrip("\n")
        csv_lines[prev_csv_idx] = old_csv_line + f",{duration_str}\n"

        with open(prev_csv_path, "w") as f_csv:
            f_csv.writelines(csv_lines)

    # Append to .log file without duration
    line_txt = f"[{date_str} {time_str}] - {feature_type.upper()} - {event} - {action_str}\n"
    with open(log_path, "a") as f_log:
        f_log.write(line_txt)

    if debug_event_console_enabled():
        print(line_txt.strip())

    # 6) Append to .csv file without duration
    if not csv_path.exists():
        header = "date,timestamp,feature,event,actuation,duration\n"
        with open(csv_path, "w") as f_csv:
            f_csv.write(header)
        csv_line = f"{date_str},{time_str},{feature_type},{event},\"{action_str}\",\n"
    else:
        csv_line = f"{date_str},{time_str},{feature_type},{event},\"{action_str}\",\n"

    with open(csv_path, "a") as f_csv:
        f_csv.write(csv_line)
        
    # Update global variables
    _last_event_timestamp = now
    try:
        prev_count = len(log_lines)
    except NameError:
        prev_count = 0

    _last_event_file = log_path
    _last_event_line_idx = prev_count
