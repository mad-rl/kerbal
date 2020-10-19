from mongodb import ModelVersion, MongoDBHelper


class ModelManager():
    def __init__(self):
        self.db: MongoDBHelper = MongoDBHelper()

    def get_model_version(self, model_version='latest') -> ModelVersion:
