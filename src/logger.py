from settings import Settings
import time
import os


class Logger(object):
    def __init__(self, settings: Settings):
        self.uid = time.time()
        self.settings = settings

    def save(
        self,
        json: dict,
        id: str = "default",
    ):
        log_file = f'{self.uid}_{id}.log'
        full_log_path = os.path.join(self.settings.logs_path, log_file)
        with open(full_log_path, "a") as file:
            file.write(json.dumps(json))
            file.write("\n")

    def print(
        self,
        json: dict
    ):
        print(json.dumps(json))
