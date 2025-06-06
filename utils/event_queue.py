# event_queue.py
# Centralized queues for sensor event dispatching
#
# Author: Francesco Urru
# GitHub: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

from queue import Queue

# Shared queues
_activity_queue = Queue()
_temperature_queue = Queue()

def get_activity_queue() -> Queue:
    """
    Returns the global queue for activity events.
    """
    return _activity_queue

def get_temperature_queue() -> Queue:
    """
    Returns the global queue for temperature events.
    """
    return _temperature_queue