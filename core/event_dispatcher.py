# event_dispatcher.py
# Dispatches recognized sensor events to the activation policy
# and triggers actions through the ActuatorManager
#
# Author: Francesco Urru
# Repository: https://github.com/frarvo/STOPme
# License: MIT

import queue
import threading
from utils.event_queue import get_event_queue
from utils.logger import log_system,log_event


LABELS = {
    0: "NO_CLASS",
    1: "NON_DANGEROUS",
    2: "DANGEROUS",
    3: "NON_STEREOTIPY",
}

class EventDispatcher:
    """
    Creates a thread that consumes event queue and dispatches actions via activation policy.
    """
    def __init__(self, actuator_manager, policy):
        """
        Initializes the dispatcher with actuator manager and activation policies.
        Args:
            actuator_manager: Instance of ActuatorManager for device control.
            policy: chooses which actuator to activate
        """
        self.actuator_manager = actuator_manager
        self.policy = policy
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._process_events, daemon=True)

    def start(self):
        """
        Starts the thread.
        """
        self._thread.start()
        log_system("[Dispatcher] Started.")

    def stop(self):
        """
        Signals the dispatcher thread to terminate.
        """
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join()
        log_system("[Dispatcher] Stopped.")

    def _process_events(self):
        q = get_event_queue()
        while not self._stop_event.is_set():
            try:
                event = q.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                raw_tag = event.get("stereotipy_tag", "")
                try:
                    tag = int(raw_tag)
                except Exception:
                    tag = None
                label = LABELS.get(tag, str(raw_tag))

                # If gated (not calibrated) skip actuation but still log
                gated = bool(event.get("gated", False))
                actuations = []

                if gated:
                    log_system("[Dispatcher] Event gated (sensor not calibrated); Skipping actuation.")
                else:
                    result = self.policy.handle(event)
                    if result:
                        try:
                            self.actuator_manager.trigger(
                                actuator_id=result["actuator_id"],
                                action_type="stereotipy_event",
                                **result["params"]
                            )
                            actuations = [{"target": result["actuator_id"], "params": result["params"]}]
                        except Exception as e:
                            log_system(f"[Dispatcher] Trigger error on {result.get('actuator_id')}: {e}", level="ERROR")
                    else:
                        log_system("[Dispatcher] Policy returned no action.")

                log_event(
                    timestamp=event.get("timestamp"),
                    feature_type="imu",
                    event=label,
                    actuations=actuations,
                    source=event.get("source", "dual_wrist")
                )
            except Exception as e:
                log_system(f"[Dispatcher] Dispatch error: {e}", level="ERROR")
            finally:
                try:
                    q.task_done()
                except Exception:
                    pass