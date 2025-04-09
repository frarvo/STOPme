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

## Project Structure

```bash
progetto_stopme/
├── main.py
├── config.yaml
├── core/
│   ├── event_dispatcher.py
│   ├── actuator_manager.py
│   ├── activation_policy.py
├── recognizers/
│   ├── activity.py
│   └── temperature.py
├── actuators/
│   ├── led_strip.py
│   ├── speaker.py
│   ├── vibration.py
│   └── logger.py
├── sensors/
│   ├── bluecoin.py      
│   ├── metawear.py
│   └── feature_listener.py
├── system/
│   └── system_logger.py
├── utils/
│   └── file_utils.py
├── assets/
└── legacy/
    └── STOPme_V0.3.0/
        ├── PROTOTIPO_V0.3.0.py
        └── MyModules/
