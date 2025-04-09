# STOPME - DEVELOPMENT ROADMAP

This roadmap describes the implementation phases of the STOPME system, focusing on building a modular, scalable and maintainable architecture for real-time BLE-driven multisensory interaction.

## PHASE 1 – Module Restructuring and Base Refactoring

1. **Actuator modules standardization**
   - Each actuator must run in its own thread.
   - Must expose consistent interfaces (`execute()`, `start_action()`, etc.)
   - Must manage internal connection/reconnection logic.

2. **MetaMotion as actuator**
   - Move MetaMotion control from `sensors/` to `actuators/`.
   - File renamed (e.g. `vibration.py`) and structured like other actuators.

3. **Logger as actuator**
   - Create `actuators/logger.py`.
   - Writes sensor events + triggered actuations.
   - Format: `[timestamp] - feature - event - actuations(...)`

4. **System logger**
   - Create `system/system_logger.py`.
   - Logs system state: connections, errors, configuration loading.
   - Uses the same custom path/naming logic as the event logger.

## PHASE 2 – Control Architecture

5. **ActuatorManager**
   - Instantiates all actuators.
   - Maps each BlueCoin to its actuators.
   - Provides unified `trigger(id, type, **params)` method.

6. **ActivationPolicy**
   - Defines rules and context-sensitive logic.
   - May store internal state (counters, thresholds, time).
   - Returns a list of actuations for each event.

7. **EventDispatcher**
   - Receives events from a queue.
   - Asks `ActivationPolicy` what to do.
   - Triggers actuators via `ActuatorManager`.
   - Logs everything using the logger (event + actuation).

## PHASE 3 – Sensor & Listener Refactor

8. **Recognizers**
   - `recognizers/temperature.py`: stateful threshold-based recognizer.
   - `recognizers/activity.py`: maps numeric values to semantic labels.

9. **GenericFeatureListener**
   - Located in `sensors/feature_listener.py`
   - Accepts `source_id`, `feature_type`, `recognizer`, and `queue`.
   - Calls recognizer, emits structured event with timestamp.

10. **BlueCoin logic simplification**
    - BlueCoin modules only connect, listen and push raw values.
    - Attuation logic removed entirely.

## PHASE 4 – Utilities and Cleanup

11. **Legacy code isolation**
    - Move prototype code to `legacy/STOPme_V0.3.0/`
    - Document in a local README.

12. **Repository root cleanup**
    - Remove `logs/` folder from GitHub.
    - Use runtime-created paths (`~/Documents/STOPME/...`) for logs.

13. **Project configuration**
    - `config.yaml` holds device MACs, actuator mappings, thresholds, etc.

14. **File utilities module**
    - `utils/file_utils.py` for generating filenames, paths, and timestamps.

## FINAL NOTES

- The logger is always triggered for each event (implicit system rule).
- The system logger is completely separate and logs only internal/system events.
- Architecture separates: sensors → recognizers → dispatcher → actuators.
- Event structure includes: timestamp, source, type, value.
- Logging uses structured output with controlled naming/location.