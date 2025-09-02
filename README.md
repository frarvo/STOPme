# STOPme 1.0
Modular Python system for real-time feedback using wireless BLE sensors and actuators.

STOPme is a modular and extensible Python system designed to connect wireless BLE wearable sensors and multisensory actuators to create real-time, responsive feedback based on detected events.

This repository evolves from a working prototype (**STOPme_V0.3.0**) and restructures it into a fully decoupled architecture with centralized event dispatching, modular actuator control, and structured logging.

## Features
- Real-time acquisition from BLE devices (BlueCoin, MetaMotion)
- Local event recognition logic
- Modular actuator control (LED strip, vibration motor, speaker)
- Centralized event dispatcher with pluggable actuations policies
- Structured and thread-safe event + system logging
- Scalable, testable, and maintainable architecture

## Requirements

### Operating System

Tested on **Ubuntu 20.04** on MSI Cubi N ADL. Detected incompatibilities with newer versions (22.04, 24.04).

### Python Version

Tested on **Python 3.9.5** using both PyCharm virtual environments and system-wide installations.  
Detected slight incompatibilities with newer versions due to outdated dependencies.

### pip Version

`pip 23.2.1`

---

### System Dependencies

Be sure to update the APT repositories and install the needed packages:

```bash
sudo apt update
sudo apt upgrade
sudo apt install python3-pip python3-distutils libglib2.0-dev
sudo apt install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev \
libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev \
zlib1g-dev libffi-dev bluetooth bluez libbluetooth-dev libudev-dev libboost-all-dev
```

### Python dependencies
It is advised to install the dependencies in the presented order.
#### [BlueST-SDK-Python](https://github.com/STMicroelectronics/BlueSTSDK_Python)
```bash
pip install blue-st-sdk.
```

#### bluepy
```bash
pip install bluepy
```
*NOTE: bluepy need sudo permission to access bluetooth devices. To grand these permission:
```bash
sudo apt install libcap2-bin.
sudo setcap “cap_net_raw+eip cap_net_admin+eip” /home/$USER/.local/lib/python3.9/site-packages/bluepy/bluepy-helper.
```

#### [MetaWear-SDK-Python](https://github.com/mbientlab/MetaWear-SDK-Python/tree/master)
```bash
pip install metawear
```

#### [PyWarble](https://github.com/mbientlab/PyWarble)
*NOTE: warble is automatically installed as a metawear dependency. Release version causes buffer overflow. Debug mode resolves the issue.
To compile in debug mode:
1) Uninstall the automatically installed version:
```bash
pip uninstall warble
```
2) If you don't have git installed:
```
sudo apt install git
```
3) Clone the git repo:
```
git clone --recurse-submodules https://github.com/mbientlab/PyWarble.git
```
4) Move into the PyWarble folder
```
cd PyWarble
```
6) Edit the setup.py
```
change row 77 from "args = ["make", "-C", warble, "-j%d" % (cpu_count())]" to "args = ["make", "-C", warble, "CONFIG=debug”, “j%d" % (cpu_count())]"
change row 89 from "so = os.path.join(warble, 'dist', 'release', 'lib', machine)" to “so = os.path.join(warble, 'dist', 'debug', 'lib', machine)"
```
5) execute setup:
```
pip install .
```
7) verify correct installation with "pip list", warble 1.2.8 should appear in the list.

#### others
```bash
pip install opuslib playsound flux_led
```


## Project Structure
```bash
STOPme/
├── main.py                                    # Entry point of the application
├── config.yaml                                # Configuration file for devices, buffers and logging details

├── actuators/                                 # Modules that perform output actions
│   ├── led_strip.py                           # Controls LED patterns
│   ├── speaker.py                             # Plays audio via Bluetooth speaker ESP Muse Luxe
│   ├── metawear.py                            # Handles MetaMotion connection and vibration
│   ├── actuator_manager.py                    # Manages actuators scans, connections and activation

├── assets/                                    # Audio, visual, or external resources
│   └── audio/                                 # Audio alerts in mp3 format

├── classifiers/                               # Event dectection logic
│   ├── stereotipy_classifier.py               # Classifier class with logging logic
│   ├── predict_models_wrapper_quat.py         # Wrapper for event recognition library
│   ├── libPredictPericolosaWristsQuat.so      # C library for event recognition (FineTree classifier)

├── core/                                      # Core logic and coordination
│   ├── event_dispatcher.py                    # Reads events from a queue and routes them to actuators
│   ├── actuation_policy.py                    # Defines logic for selecting which actuators to trigger

├── data_pipeline/                             # Data stream buffering and processing 
│   ├── data_buffer.py                         # Stores synchronized data in a sliding window buffer ready for processing
│   ├── synchronizer.py                        # Synchronizes data between two separate stream
│   ├── data_processing_wrapper_quat.py        # Wrapper for processing library
│   ├── libProcessDataWristsQuat.so            # C library for data processing

├── sensors/                                   # BLE device interface and data acquisition
│   ├── bluecoin.py                            # Defines BlueCoin device connections 
│   ├── sensor_manager.py                      # Manages sensors instances and data stream
│   └── feature_listener.py                    # Listener for specific features (accelerometer, gyroscope and quaternions)
│   └── feature_mems_sensor_fusion_compact.py  # Host side quaternion reconstruction logic

├── utils/                         # Utility functions and helpers
│   └── config.py                  # Manages general configuration, paths and timeouts, from config.yaml
│   └── audio_paths.py             # Manages audio file paths
│   └── logger.py                  # Logs sensor events with duration and actuation, and system events
│   └── lock.py                    # Global thread-safety locks
│   ├── event_queue.py             # Control logic for queue stream
```

## License

This project is licensed under the MIT License.

### Third-Party Licenses

This project uses several third-party Python packages, each governed by its own license. Below is a summary of the main dependencies:

- **metawear**, **pywarble** – Provided by [MbientLab](https://www.mbientlab.com). These packages are used unmodified and are not redistributed with this project. Some of them may interact with the BlueZ Bluetooth stack (GPLv2), but this project does not include, modify, or statically link any GPL-licensed code.
- **blue-st-sdk** – Licensed under a BSD-style License from [STMicroelectronics](https://www.st.com/content/st_com/en.html) Fully compatible with the project's MIT licensing.
- **bluepy** – A Python interface to Bluetooth Low Energy on Linux. License not explicitly stated in the package, but the project references BlueZ (GPLv2). This project uses bluepy as a runtime dependency without modification or redistribution.
- **playsound** – Licensed under the MIT License. It is a simple audio playback module, fully compatible with this project's MIT licensing.
- **flux_led** – Licensed under LGPLv3+. It is used as a runtime dependency and not modified or statically linked, making it compatible with this project’s MIT license.
- **Other packages** (e.g., requests, urllib3, charset-normalizer, idna, pyserial, webcolors, certifi, etc.) are licensed under permissive licenses such as MIT, BSD, Apache 2.0, or MPL 2.0 and are fully compatible with this project when used as unmodified runtime dependencies.

**Note:** This project does **not** include or redistribute any third-party source code or binaries. All dependencies are used as runtime libraries via pip and remain subject to their original licenses.
