import yaml


class Settings (object):
    def __init__(self, load_from_yaml=""):
        # default settings
        self.max_episode_steps = 50
        self.save_game_name = "Launch into orbit"
        self.krpc_address = "127.0.0.1"
        self.krpc_rpc_port = 50000
        self.krpc_stream_port = 50001
        self.logs_path = 'artifacts/'
        if load_from_yaml:
            self.load_from_yaml(load_from_yaml)

    def load_from_yaml(self, yaml_path: str):
        with open(yaml_path, "r") as file:
            settings: dict = yaml.full_load_all(file)

        if settings["max_episode_steps"] != "":
            self.max_episode_steps = settings["max_episode_steps"]
        if settings["save_game_name"] != "":
            self.save_game_name = settings["save_game_name"]

        if settings["krpc"]["address"] != "":
            self.krpc_address = settings["krpc"]["address"]
        if settings["krpc"]["rpc_port"] != "":
            self.krpc_rpc_port = settings["krpc"]["rpc_port"]
        if settings["krpc"]["stream_port"] != "":
            self.krpc_stream_port = settings["krpc"]["stream_port"]
