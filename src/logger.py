import time
import json
import os


class Logger(object):
    def __init__(self):
        self.uid = time.time()

    def save(
        self,
        data: dict,
        id: str = "default",
    ):
        log_file = f'{self.uid}_{id}.log'
        full_log_path = os.path.join(os.environ['LOGS_PATH'], log_file)
        with open(full_log_path, "a") as file:
            file.write(json.dumps(data))
            file.write("\n")

    def print(
        self,
        data: dict
    ):
        print(json.dumps(data))
