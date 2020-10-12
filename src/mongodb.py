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

    def create_model_version(self, model_version: ModelVersion):
        self.collection.insert_one(model_version.to_dict())

    def find_model_version(self, model_version: str = 'latest') -> list:
        mm_vv: list = []
        if model_version == 'latest':
            m: dict = self.collection.find_one()
            print(m)
            mv: ModelVersion = ModelVersion.from_dict(m)
            mm_vv.append(mv)
        else:
            mm_vv_dict: dict = self.collection.find()
            for m_v_d in mm_vv_dict:
                mv: ModelVersion = ModelVersion.from_dict(m_v_d)
                mm_vv.append(mv)
        return mm_vv
