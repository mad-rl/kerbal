from pymongo import MongoClient


class ModelVersion():
    def __init__(
        self,
        version: str,
        score: int,
        model_state_dict: dict,
        optimizer_state_dict: dict
    ):
        self.version: str = version
        self.score: int = score
        self.model_state_dict: dict = model_state_dict
        self.optimizer_state_dict: dict = optimizer_state_dict

    def __iter__(self):
        yield 'version', self.version
        yield 'score', self.score
        yield 'model_state_dict', self.model_state_dict
        yield 'optimizer_state_dict', self.optimizer_state_dict

    def to_dict(self) -> dict:
        return dict(self)


def from_dict(m: dict) -> ModelVersion:
    return ModelVersion(
        m["version"],
        m["score"],
        m["model_state_dict"],
        m["optimizer_state_dict"]
    )


ModelVersion.from_dict = staticmethod(from_dict)


class MongoDBHelper():
    def __init__(self, host, user, password, dbname):
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

    def create_model_version(self, mv: ModelVersion):
        q: dict = {"model_version": mv.model_version}
        v: dict = {"$set": {
            "score": 0,
            "model_state_dict": mv.model_state_dict,
            "optimizer_state_dict": mv.optimizer_state_dict
        }}
        self.collection.update_one(q, v, upsert=True)

    def find_model_version(self, model_version: str) -> ModelVersion:
        m: dict = self.collection.find_one({'model_version': model_version})
        if m is None:
            return m

        return ModelVersion.from_dict(m)
