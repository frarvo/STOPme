# event_dispatcher.py
# Dispatches recognized sensor events to the appropriate activation policy
# and triggers actions through the ActuatorManager
#
# Author: Francesco Urru
# Repository: https://github.com/frarvo/STOPme
# License: MIT

import threading
from utils.event_queue import get_activity_queue, get_temperature_queue


class EventDispatcher:
    """
    Continuously listens to sensor event queues and dispatches actions via activation policies.
    """

    def __init__(self, actuator_manager, temperature_policy, activity_policy):
        """
        Initializes the dispatcher with actuator manager and activation policies.

        Args:
            actuator_manager: Instance of ActuatorManager for device control.
            temperature_policy: Instance of TemperatureActivationPolicy.
            activity_policy: Instance of ActivityActivationPolicy.
        """
        self.actuator_manager = actuator_manager
        self.temperature_policy = temperature_policy
        self.activity_policy = activity_policy

        self._stop_event = threading.Event()

        self._activity_thread = threading.Thread(target=self._process_activity_events, daemon=True)
        self._temperature_thread = threading.Thread(target=self._process_temperature_events, daemon=True)

    def start(self):
        """
        Starts the dispatcher threads for activity and temperature events.
        """
        self._activity_thread.start()
        self._temperature_thread.start()

    def stop(self):
        """
        Signals the dispatcher threads to terminate.
        """
        self._stop_event.set()
        self._activity_thread.join()
        self._temperature_thread.join()

    def _process_activity_events(self):
        queue = get_activity_queue()
        while not self._stop_event.is_set():
            event = queue.get()
            result = self.activity_policy.handle(event)
            if result:
                self.actuator_manager.trigger(
                    actuator_id=result["actuator_id"],
                    action_type="temperature_event",
                    **result["params"]
                )

    def _process_temperature_events(self):
        queue = get_temperature_queue()
        while not self._stop_event.is_set():
            event = queue.get()
            result = self.temperature_policy.handle(event)
            if result:
                self.actuator_manager.trigger(
                    actuator_id=result["actuator_id"],
                    action_type="activity_event",
                    **result["params"]
                )