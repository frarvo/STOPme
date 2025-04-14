# STOPme - TODO List (Incremental, Safe Refactor Strategy)

This TODO list follows the development strategy designed to progressively refactor and modularize the STOPME system,
ensuring each step is testable and doesn't break existing functionality.

## TODO

### PHASE 1 – Autonomous Modules (Safe to implement immediately)
- [x] Implement `actuators/logger.py` with log_event() and log_system()
- [x] Refactor MetaMotion control into `actuators/metamotion.py`
- [ ] Refactor LED control into `actuators/led_strip.py`
- [ ] Define Speaker control into `actuators/speaker.py`
- [ ] Test each actuator module independently

### PHASE 2 – Core Actuator Coordination
- [ ] Create `core/actuator_manager.py` to manage actuator instances and trigger calls
- [ ] Integrate logger actuator into ActuatorManager for event logging

### PHASE 3 – Event Recognition Logic
- [ ] Implement `recognizers/temperature.py` with multiple thresholds and state memory
- [ ] Implement `recognizers/activity.py` as numeric → semantic mapper

### PHASE 4 – Sensor Input Refactor
- [ ] Implement `sensors/feature_listener.py` as generic listener with recognizer support
- [ ] Update listener to insert structured events (with timestamp) into the event queue

### PHASE 5 – Core Dispatch & Logic
- [ ] Implement `core/activation_policy.py` with internal decision logic
- [ ] Implement `core/event_dispatcher.py` that connects events to actuators through policy

### PHASE 6 – Final Refactor
- [ ] Refactor `sensors/bluecoin.py` to only handle BLE connection and data forwarding
- [ ] Use listener + recognizer architecture for each feature
- [ ] Link BlueCoin threads to dispatcher logic
