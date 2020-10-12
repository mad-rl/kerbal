import time
import os


class Logger(object):
    def __init__(self):
        self.uid = time.time()

    def save(
        self,
        json: dict,
        id: str = "default",
    ):
        log_file = f'{self.uid}_{id}.log'
        full_log_path = os.path.join(os.environ['LOGS_PATH'], log_file)
        with open(full_log_path, "a") as file:
            file.write(json.dumps(json))
            file.write("\n")

    def print(
        self,
        json: dict
    ):
        print(json.dumps(json))
