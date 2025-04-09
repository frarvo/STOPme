#########
# PROTOTIPO_V0.3.0 04/04/2025

# FUNZIONALITA':
# Connessione a speaker
# Connessione a due BlueCoin
# Connessione a striscia led
# Gestione disconnessione, riconnessione e ripresa attività delle bluecoin e della striscia
# Riconoscimento eventi
# Log degli eventi

# CAMBIAMENTI:
# Introdotto il dispositivo vibroattuatore MetaMotionRL
# Introdotta l'attuazione della vibrazione

# MIGLIORAMENTI:
# -

# NOTE:
# L'attuazione per adesso è tutta in contemporanea, speaker, led e vibroattuatore vanno assieme,
# Il comportamento verrà modificato in versioni successive

#########



# IMPORT
import sys

from blue_st_sdk.features.feature_activity_recognition import FeatureActivityRecognition
from blue_st_sdk.features.feature_temperature import FeatureTemperature
from blue_st_sdk.manager import Manager

from MyModules.Speaker import Speaker
from MyModules.BlueCoin import MyManagerListener
from MyModules.BlueCoin import MyNodeListener
from MyModules.BlueCoin import MyFeatureListenerActivity
from MyModules.BlueCoin import MyFeatureListenerTemperature
from MyModules.BlueCoin import BlueCoinThread
from MyModules.LedStrip import LedThread
from MyModules.BleLock import bluetooth_scan_lock


# Macro
SCANNING_TIME_s = 2
SPEAKER_MAC = "7A:DA:DF:A4:E6:ED"
DEVICE_MAC = SPEAKER_MAC
LOGGING = True
EXPECTED_BLUE_COINS = 2





def main():
    speaker = Speaker(DEVICE_MAC)
    threads_list = []
    led_thread = LedThread()
    try:
        speaker.scan(SCANNING_TIME_s)
        speaker.connect()

        manager = Manager.instance()
        manager_listener = MyManagerListener()
        manager.add_listener(manager_listener)

        node_listener = MyNodeListener()
        feature_listener_temp = MyFeatureListenerTemperature()
        feature_listener_activity = MyFeatureListenerActivity()

        # Ricerca dispositivi
        print('Scanning Bluetooth devices...\n')
        discovered_devices = []
        while len(discovered_devices) != EXPECTED_BLUE_COINS:
            print("No available devices found. Retrying ...")
            with bluetooth_scan_lock:
                if manager.discover(SCANNING_TIME_s) is True:
                    discovered_devices = manager.get_nodes()

        print('Available Bluetooth devices:')
        i = 0
        feature_listener = None
        feature = None
        for device in discovered_devices:
            print('%d) %s: [%s]' % (i + 1, device.get_name(), device.get_tag()))
            if device.get_name() == "BCNB240":
                feature = device.get_feature(FeatureTemperature)
                feature_listener = feature_listener_temp
            elif device.get_name() == "AM2V210":
                feature = device.get_feature(FeatureActivityRecognition)
                feature_listener = feature_listener_activity

            thread = BlueCoinThread(device, node_listener, feature, feature_listener, i+1)
            threads_list.append(thread)
            i += 1


        for thread in threads_list:
            print(f"Starting thread: {thread.name}\n")
            thread.start()
        led_thread.start() # non fare join su led_thread, per questo non è nella lista

        for thread in threads_list:
            thread.join()

    # Interruzione dovuta a interrupt da tastiera (ctrl + c)
    except KeyboardInterrupt:
        # Exiting.
        print('\nProgram interrupted from user. Exiting...\n')

    finally:
        for thread in threads_list:
            thread.stop()

        for thread in threads_list:
            thread.join()
        led_thread.stop()
        led_thread.join()
        speaker.disconnect()
        sys.exit(0)




if __name__ == "__main__":
    main()