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

## Requirements
Cosa serve? (Ubuntu, Python ecc)

## Installation
(sudo apt install... pip install...)

## Usage examples
--

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

├── utils/                         # Utility functions and helpers
│   └── file_utils.py              # Manages file paths, names, timestamps

├── assets/                        # Audio, visual, or external resources (e.g. patterns, mp3s)

└── legacy/                        # Previous working prototype for reference only
    └── STOPme_V0.3.0/
        ├── PROTOTYPE_V0.3.0.py    # Original monolithic main script
        └── MyModules/             # Support modules for the prototype
```

## Legacy
The folder `legacy/STOPme_V0.3.0/` contains the original monolithic prototype that this project is based on.

It includes functional but tightly coupled logic for BLE sensor handling, actuation, and logging, and served as the foundation for the current modular architecture.

This code is preserved for reference only and is no longer maintained.

## License

This project is licensed under the MIT License.

### Third-Party Licenses

This project uses several third-party Python packages, each governed by its own license. Below is a summary of the main dependencies:

- **metawear**, **pywarble** – Provided by [MbientLab](https://www.mbientlab.com). These packages are used unmodified and are not redistributed with this project. Some of them may interact with the BlueZ Bluetooth stack (GPLv2), but this project does not include, modify, or statically link any GPL-licensed code.
- **blue-st-sdk** – Licensed under a BSD-style License from [STMicroelectronics](https://www.st.com/content/st_com/en.html) Fully compatible with the project's MIT licensing.
- **bluepy** – A Python interface to Bluetooth Low Energy on Linux. License not explicitly stated in the package, but the project references BlueZ (GPLv2). This project uses `bluepy` as a runtime dependency without modification or redistribution.
- **playsound** – Licensed under the MIT License. It is a simple audio playback module, fully compatible with this project's MIT licensing.
- **flux_led** – Licensed under LGPLv3+. It is used as a runtime dependency and not modified or statically linked, making it compatible with this project’s MIT license.
- **Other packages** (e.g., `requests`, `urllib3`, `charset-normalizer`, `idna`, `pyserial`, `webcolors`, `certifi`, etc.) are licensed under permissive licenses such as MIT, BSD, Apache 2.0, or MPL 2.0 and are fully compatible with this project when used as unmodified runtime dependencies.

**Note:** This project does **not** include or redistribute any third-party source code or binaries. All dependencies are used as runtime libraries via `pip` and remain subject to their original licenses.
