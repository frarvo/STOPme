# STOPme  
Modular Python system for real-time feedback using wireless BLE sensors and actuators.

STOPme is a modular and extensible Python system designed to connect wireless BLE wearable sensors and multisensory actuators to create real-time, responsive feedback based on physical activity, temperature, and future sensor-derived events.

This repository evolves from a working prototype (**STOPme_V0.3.0**) and restructures it into a fully decoupled architecture with centralized event dispatching, modular actuator control, and structured logging.

## Features

- Real-time acquisition from BLE devices (BlueCoin, MetaMotion)
- Local event recognition logic via configurable recognizers
- Modular actuator control (LED strip, vibration motor, speaker, logger)
- Centralized event dispatcher with pluggable activation policies
- Structured and thread-safe event + system logging
- Scalable, testable, and maintainable architecture

## Installation

## Requirements

## Usage examples

## Project Structure

```bash
progetto_stopme/
├── main.py                        # Entry point of the application
├── config.yaml                    # Configuration file for devices, thresholds, mappings

├── core/                          # Core logic and coordination
│   ├── event_dispatcher.py        # Reads events and routes them to actuators
│   ├── actuator_manager.py        # Manages actuator instances and mappings
│   ├── activation_policy.py       # Defines logic for selecting which actuators to trigger

├── recognizers/                   # Sensor data interpreters (event recognition)
│   ├── activity.py                # Maps activity feature values to semantic events
│   └── temperature.py             # Detects threshold crossings and emits events

├── actuators/                     # Modules that perform output actions
│   ├── led_strip.py               # Controls LED patterns
│   ├── speaker.py                 # Plays audio via Bluetooth speaker
│   ├── metawear.py                # Handles MetaMotion connection and vibration
│   └── logger.py                  # Logs sensor events and triggered actuations

├── sensors/                       # BLE device interface and data acquisition
│   ├── bluecoin.py                # Manages BlueCoin device connections and data
│   └── feature_listener.py        # Generic listener that uses recognizers

├── system/                        # System-level diagnostics and logging
│   └── system_logger.py           # Logs internal state (connections, errors, etc.)

├── utils/                         # Utility functions and helpers
│   └── file_utils.py              # Manages file paths, names, timestamps

├── assets/                        # Audio, visual, or external resources (e.g. patterns, mp3s)

└── legacy/                        # Previous working prototype for reference only
    └── STOPme_V0.3.0/
        ├── PROTOTYPE_V0.3.0.py    # Original monolithic main script
        └── MyModules/             # Support modules for the prototype
