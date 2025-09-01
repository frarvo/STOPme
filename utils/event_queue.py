# event_queue.py
# Centralized queues for sensor event dispatching
#
# Author: Francesco Urru
# GitHub: https://github.com/frarvo
# Repository: https://github.com/frarvo/STOPme
# License: MIT

from queue import Queue
from typing import Optional, Tuple, Any
MAX_Q_SIZE = 1

# Shared queue (with limit to avoid stacking and losing real time)
_event_queue = Queue(maxsize=MAX_Q_SIZE)

# Counter for internal regulation (if an event is dropped when queue is full, duration would be wrong)
_dropped_counts = {"event":0}

def get_event_queue() -> Queue:
    """
    Returns the global queue for activity events.
    """
    return _event_queue

def enqueue_drop_oldest(q: Queue, item, kind:Optional[str] = None) -> Tuple[bool, Optional[Any]]:
    """
    Enque 'item'. If queue is full, drops the oldest item. Reduces latency
    Returns dropped flag and dropped item
    """
    dropped = False
    dropped_item = None
    try:
        q.put_nowait(item)
        return False, None
    except Exception:
        # Queue is full, drop oldest, try new enqueue
        try:
            dropped_item = q.get_nowait()
            dropped = True
        except Exception:
            return False, None
        try:
            q.put_nowait(item)
        except Exception:
            return dropped, dropped_item

    if dropped and kind in _dropped_counts:
        _dropped_counts[kind] += 1
    return dropped, dropped_item

def get_drop_count(kind:str) -> int:
    """
    Returns number of dropped items
    """
    return _dropped_counts.get(kind,0)