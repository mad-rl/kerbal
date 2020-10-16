import os
import time

import json

from settings import Settings


class Logger(object):
    def __init__(self, settings: Settings):
        self.uid = time.time()
        self.settings = settings

    def save(
        self,
        data: dict,
        id: str = "default",
    ):
        log_file = f'{self.uid}_{id}.log'
        full_log_path = os.path.join(self.settings.logs_path, log_file)
        with open(full_log_path, "a") as file:
            file.write(json.dumps(data))
            file.write("\n")

    def print(
        self,
        data: dict
    ):
        print(json.dumps(data))
