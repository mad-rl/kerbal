import os
from mongodb import ModelVersion, MongoDBHelper

MONGODB_HOST = os.environ.get('MONGODB_HOST', 'localhost:27017')
MONGODB_USER = os.environ.get('MONGODB_USER', '')
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', '')
MONGODB_DBNAME = os.environ.get('MONGODB_DBNAME', 'test_experiments')

MONGODB_HOST = "cluster0.5bard.gcp.mongodb.net"
MONGODB_USER = "kerbal_admin"
MONGODB_PASSWORD = "awOJtce627PIGgN7"
MONGODB_DBNAME = "test_experiments"

mongodb: MongoDBHelper = MongoDBHelper(
    MONGODB_HOST,
    MONGODB_USER,
    MONGODB_PASSWORD,
    MONGODB_DBNAME
)

mv: ModelVersion = ModelVersion(
    'version_test',
    99,
    {'model_state_dict': 1},
    {'optimizer_state_dict': 2}
)

mongodb.create_model_version(mv)

mm_vv: list = mongodb.find_model_version()

print(len(mm_vv))
