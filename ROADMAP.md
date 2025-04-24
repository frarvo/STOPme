# STOPme - DEVELOPMENT ROADMAP

This roadmap describes the implementation phases of the STOPME system, focusing on building a modular, scalable and maintainable architecture for real-time BLE-driven multisensory interaction.

## PHASE 1 – Module Restructuring and Base Refactoring

1. **Actuator modules standardization**
   - Each actuator must run in its own thread.
   - Must expose consistent interfaces (`execute()`, `start_action()`, etc.)
   - Must manage internal connection/reconnection logic.

2. **Custom Logger **
   - Create `utils/logger.py`.
   - Writes sensor events + triggered actuations.
   - Format: `[timestamp] - feature - event - actuations(...)`
   - Logs system state: connections, errors, configuration loading.
   - Uses custom path/naming logic.

## PHASE 2 – Control Architecture

3. **ActuatorManager**
   - Instantiates all actuators.
   - Maps each BlueCoin to its actuators.
   - Provides unified `trigger(id, type, **params)` method.

4. **SensorManager**
   - Istantiates all sensors (BlueCoin).
   - Maps a recognizer to each BlueCoin.

5. **ActivationPolicy**
   - Defines rules and context-sensitive logic.
   - May store internal state (counters, thresholds, time).
   - Returns a list of actuations for each event.

6. **EventDispatcher**
   - Receives events from a queue.
   - Asks `ActivationPolicy` what to do.
   - Triggers actuators via `ActuatorManager`.
   - Logs everything using the logger (event + actuation).

## PHASE 3 – Sensor & Listener Refactor

7. **Recognizers**
   - `recognizers/temperature.py`: stateful threshold-based recognizer.
   - `recognizers/activity.py`: maps numeric values to semantic labels.

8. **GenericFeatureListener**
   - Located in `sensors/feature_listener.py`
   - Accepts `source_id`, `feature_type`, `recognizer`, and `queue`.
   - Calls recognizer, emits structured event with timestamp.

9. **BlueCoin logic simplification**
    - BlueCoin modules only connect, listen and push raw values.
    - Attuation logic removed entirely.

## PHASE 4 – Utilities and Cleanup

10. **Legacy code isolation**
    - Move prototype code to `legacy/STOPme_V0.3.0/`
    - Document in a local README.

11. **Repository root cleanup**
    - Remove `logs/` folder from GitHub.
    - Use runtime-created paths (`~/Documents/STOPME/...`) for logs.

12. **Project configuration**
    - `config.yaml` holds device MACs, actuator mappings, thresholds, etc.

13. **File utilities module**
    - `utils/file_utils.py` for generating filenames, paths, and timestamps.

## FINAL NOTES

- The logger is always triggered for each event (implicit system rule).
- The system logger is completely separate and logs only internal/system events.
- Architecture separates: sensors → recognizers → dispatcher → actuators.
- Event structure includes: timestamp, source, type, value.
- Logging uses structured output with controlled naming/location.
