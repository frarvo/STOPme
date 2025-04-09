import os
from datetime import datetime


class Log:
    def __init__(self, feature):
        self.username = os.getlogin()
        self.logs_path = f"/home/{self.username}/Desktop/logs"
        if not os.path.exists(self.logs_path):
            os.makedirs(self.logs_path)
        self.day = datetime.now().strftime("%d.%m.%Y")
        self.time = datetime.now().strftime("%H:%M:%S")
        self.day_folder_path = ""
        self.feature = feature
        self.feature_name = self.feature.FEATURE_NAME
        self._create_log()

    def _create_log(self):
        self.day_folder_path = os.path.join(self.logs_path, self.day)
        if not os.path.exists(self.day_folder_path):
            os.makedirs(self.day_folder_path)

        file_name = f"{self.feature_name}_{self.day}.txt"
        file_path = os.path.join(self.day_folder_path, file_name)
        try:
            with open(file_path, "a") as log_file:
                if not os.path.exists(file_path):
                    log_file.write(f"Log file creato per la feature {self.feature_name} il {self.day} alle {self.time}\n")
                else:
                    log_file.write(f"\nLog file aperto per aggiornamento alle {self.time}\n")
            print(f"Log per {self.feature_name} creato con successo: {file_path}")
        except Exception as e:
            print(f"Errore nella creazione del log: {e}")

        return self

    def add_entry(self, data):
        current_time = datetime.now().strftime("%H:%M:%S")

        if not os.path.exists(self.day_folder_path):
            os.makedirs(self.day_folder_path)

        log_files = [f for f in os.listdir(self.day_folder_path) if f.startswith(self.feature_name) and f.endswith(".txt")]
        if log_files:
            latest_log_file = os.path.join(self.day_folder_path, log_files[-1])
            try:
                with open(latest_log_file, "a") as log_file:
                    log_file.write(f"{current_time} - {self.feature_name} - {data} \n")
                print(f"Entry aggiunto con successo a: {latest_log_file}")
                print(f"{current_time} - {self.feature_name} - {data} \n")
            except Exception as e:
                print(f"Errore nell'aggiungere la entry: {e}")
        else:
            print(f"Nessun file di log trovato per la feature '{self.feature_name}' oggi.")