# Legacy Prototype - STOPME v0.3.0

This folder contains the original prototype of the STOPME system, implemented as a monolithic Python script (`PROTOTIPO_V0.3.0.py`) and a set of support modules under the `MyModules/` directory.

The prototype was fully functional and used for initial testing and validation. It includes:

- BLE sensor integration (BlueCoin, MetaMotion)
- WiFi LED strip control
- Audio feedback via Bluetooth speaker
- Basic vibration control using MetaMotion
- Simple event-based actuation logic
- Log writing to local files using a custom format

This code is now preserved for reference only.  
The new version of STOPME introduces a modular, decoupled architecture with:

- Independent threads for actuators
- Event recognizers and dispatchers
- Configurable policies for triggering
- Structured logging with separation between system and event logs

**Note**: This legacy code is no longer maintained and is not used in the current system.
