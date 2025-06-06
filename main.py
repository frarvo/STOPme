# main.py
# Entry point for the STOPme system
#
# Author: Francesco Urru
# Repository: https://github.com/frarvo/STOPme
# License: MIT

import time
from core.sensor_manager import SensorManager
from core.actuator_manager import ActuatorManager
from core.activation_policy import TemperatureActivationPolicy, ActivityActivationPolicy
from core.event_dispatcher import EventDispatcher
from utils.logger import log_system


def main():
    log_system("[MAIN] Initializing STOPme system...")

    # Initialize managers
    sensor_manager = SensorManager()
    actuator_manager = ActuatorManager()

    # Scan sensors and actuators
    sensor_manager.scan_sensors()
    actuator_manager.scan_actuators()

    # Initialize sensors and actuators
    actuator_manager.initialize_actuators()
    sensor_manager.initialize_sensors()

    # Extract actuator lists
    actuators_list = actuator_manager.get_actuators_ids()

    # Instantiate activation policies
    temperature_policy = TemperatureActivationPolicy(actuators_list)
    activity_policy = ActivityActivationPolicy(actuators_list)

    # Instantiate event dispatcher
    dispatcher = EventDispatcher(
        actuator_manager=actuator_manager,
        temperature_policy=temperature_policy,
        activity_policy=activity_policy
    )
    # Initialize event dispatcher
    dispatcher.start()


    log_system("[MAIN] System is now running. Press Ctrl+C to terminate.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_system("[MAIN] Termination signal received.")
        dispatcher.stop()
        actuator_manager.stop_all()
        sensor_manager.stop_all()
        log_system("[MAIN] System shutdown complete.")


if __name__ == "__main__":
    main()