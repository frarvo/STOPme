# STOPME - TODO List

This file tracks implementation progress based on the current roadmap.
Each item corresponds to a task or milestone derived from the roadmap.
Completed tasks should be moved to the DONE section.

## TODO

### PHASE 1 – Module Restructuring and Base Refactoring
- [ ] Standardize all actuator modules (threads, interfaces, reconnection)
- [ ] Move MetaMotion to `actuators/vibration.py`
- [ ] Create `actuators/logger.py` for event logging
- [ ] Implement `system/system_logger.py` for internal logs

### PHASE 2 – Control Architecture
- [ ] Create `core/actuator_manager.py` with unified `trigger()` method
- [ ] Define context-aware logic in `activation_policy.py`
- [ ] Implement `event_dispatcher.py` to connect recognizers, policy and actuators

### PHASE 3 – Sensor & Listener Refactor
- [ ] Create `recognizers/temperature.py` (stateful, multi-threshold)
- [ ] Create `recognizers/activity.py` (numeric → semantic)
- [ ] Build `sensors/feature_listener.py` (generic listener)
- [ ] Simplify `bluecoin.py` to only manage connection and data forwarding

### PHASE 4 – Utilities and Cleanup
- [ ] Move prototype to `legacy/STOPme_V0.3.0/` and add local README
- [ ] Remove `logs/` from repository (use runtime directories)
- [ ] Create and use `config.yaml` for MACs, mappings, thresholds
- [ ] Implement `utils/file_utils.py` for filename and path generation

## DONE