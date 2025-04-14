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
### Operating system
Tested on Ubuntu 20.04 on MSI Cubi N ADL. Detected incompatibilities with newer versions (22.04, 24.04).
### Python version
Tested on Python 3.9.5. Both PyCharm virtual environment and system wide installation. Detected slight incompatibilities with newer versions due to outdated 
dependencies.
### pip version
pip 23.2.1

### System dependencies
Be sure to update the apt repositories and install the needed packages:
sudo apt udpdate 
sudo apt upgrade
sudo apt install python3-pip python3-distutils libglib2.0-dev
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev 	libexpat1-dev liblzma-dev zlib1g-dev libffi-dev bluetooth bluez libbluetooth-dev libudev-dev libboost-all-dev

### Python dependencies
It is advised to install the dependencies in the presented order
#### [BlueST-SDK-Python](https://github.com/STMicroelectronics/BlueSTSDK_Python)
pip install blue-st-sdk

#### bluepy
pip install bluepy
*NOTE: bluepy need sudo permission to access bluetooth devices. To grand these permission:
        1) install setcap: sudo apt install libcap2-bin
        2) execute: sudo setcap “cap_net_raw+eip cap_net_admin+eip” /home/<USER>/.local/lib/python3.9/site-packages/bluepy/bluepy-helper

#### [MetaWear-SDK-Python](https://github.com/mbientlab/MetaWear-SDK-Python/tree/master)
pip install metawear

#### [PyWarble](https://github.com/mbientlab/PyWarble)
*NOTE: warble is automatically installed as a metawear dependency. I detected problems with the release version which cause buffer overflow during execution.
Due to inexperience in debugging and copyright policy i could not modify the source code, but i noticed that compiling in debug mode resolves the issue.
To compile in debug mode:
    1) uninstall the automatically installed version: "pip uninstall warble"
    2) clone the git repo (if you don't have git installed: "sudo apt install git"): "git clone --recurse-submodules https://github.com/mbientlab/PyWarble.git"
    3) cd into the PyWarble folder 
    4) edit the setup.py
        a) change row 77 from "args = ["make", "-C", warble, "-j%d" % (cpu_count())]" to "args = ["make", "-C", warble, "CONFIG=debug”, “j%d" % (cpu_count())]"
        b) change row 89 from "so = os.path.join(warble, 'dist', 'release', 'lib', machine)" to “so = os.path.join(warble, 'dist', 'debug', 'lib', machine)"
    5) execute setup: "pip install ."
    6) verify correct installation with "pip list", warble 1.2.8 should appear in the list.


#### others
pip install opuslib playsound flux_led


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
│   └── config.py                  # Manages general configuration, paths and timeouts
│   └── audio_paths.py             # Manages file paths, names

├── assets/                        # Audio, visual, or external resources
│   └── audio/                     # Audio alerts in mp3 format

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
