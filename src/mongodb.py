import time
import os
import gridfs
from gridfs import GridOut
from pymongo import MongoClient


class MongoDBHelper():
    def __init__(self, host: str, user: str, password: str, dbname: str, local_model_filename: str):
        user_and_pass: str = ""
        if user != "":
            user_and_pass = f"{user}:{password}@"
        url_conn: str = f"mongodb+srv://" \
            f"{user_and_pass}" \
            f"{host}/" \
            f"{dbname}?" \
            f"retryWrites=true&w=majority"
        self.client: MongoClient = MongoClient(url_conn)
        self.db = self.client[dbname]
        self.collection = self.db['models_versions']
        self.fs = gridfs.GridFS(self.db)
        self.last_model_file_md5: str = ''
        self.local_model_file_name: str = local_model_filename

    def save_model_version(self, model_name: str):
        model_file_name: str = f"{model_name}.pt"
        local_file = open(self.local_model_file_name, mode="rb")
        print(
            f"saving local model {self.local_model_file_name} to {model_file_name} in mongo")
        self.fs.put(local_file.read(), filename=model_file_name)

    def wait_for_new_model_version(self, model_name: str, agent_mode: str) -> (str, str):
        local_file_ready = False
        while local_file_ready is False:
            time.sleep(3.0)
            file: GridOut = self.find_model_by_name(model_name)
            if agent_mode == "learner":
                local_file_ready = True
            elif agent_mode == "collector":
                if file is not None:
                    print(
                        f"checking new version "
                        f"local[{self.last_model_file_md5}] "
                        f"remote[{file.md5}]"
                    )
                    if file.md5 != self.last_model_file_md5:
                        self.last_model_file_md5 = file.md5
                        local_file_ready = True

        if file is not None:
            print(
                f"loading remote[{file.md5}] version "
                f"last local version [{self.last_model_file_md5}]"
            )
            self.last_model_file_md5 = file.md5
            if os.path.exists(self.local_model_file_name):
                os.remove(self.local_model_file_name)
            local_file = open(self.local_model_file_name, mode="wb")
            local_file.write(file.read())
            local_file.close()
            return (self.local_model_file_name, self.last_model_file_md5)
        else:
            return (None, self.last_model_file_md5)

    def find_model_by_name(self, model_name: str) -> GridOut:
        model_file_name: str = f"{model_name}.pt"
        file: GridOut = None
        print(f"checking if remote {model_file_name} exists")
        if self.fs.exists(filename=model_file_name):
            print(f"getting last remote version of {model_file_name}")
            file = self.fs.get_last_version(filename=model_file_name)
        return file
