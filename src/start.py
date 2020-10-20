import os

from influxdb import InfluxDBHelper
from mongodb import MongoDBHelper
from rabbitmq import RabbitMQHelper
from krpc_helper import KRPCHelper


from logger import Logger

from engine import Engine
from game_env import GameEnv
from agents.actor_critic.agent import Agent


print('\n####### PRE-START CHECKINGS ######')

# check influx connectivity
print('checking influxdb access...')
influx: InfluxDBHelper = InfluxDBHelper(
    os.environ["INLFUXDB_URL"],
    os.environ["INFLUXDB_ACCESS_TOKEN"],
    os.environ["INFLUXDB_ORG"],
    os.environ["INFLUXDB_BUCKET"]
)
print('INFLUXDB IS READY')

# check mongo connectivity
print('checking mongodb access...')
mongo: MongoDBHelper = MongoDBHelper(
    os.environ["MONGODB_HOST"],
    os.environ["MONGODB_USER"],
    os.environ["MONGODB_PASSWORD"],
    os.environ["MONGODB_DBNAME"],
    os.environ["LOCAL_MODEL_FILENAME"]
)
print('MONGODB IS READY')

# check rabbit connectivity
print('checking rabbit access...')
rabbit: RabbitMQHelper = RabbitMQHelper(
    os.environ["RABBITMQ_CONN_URL"],
    os.environ["RABBITMQ_QUEUE"]
)
print('RABBITMQ IS READY')

# check krpc connectivity
print('checking KRPC connection with GAME...')
krpc: KRPCHelper = KRPCHelper(
    os.environ["KRPC_ADDRESS"],
    int(os.environ["KRPC_RPC_PORT"]),
    int(os.environ["KRPC_STREAM_PORT"])
)
print('KRPC IS READY')

print('\n####### DASHBOARD ######')
print('Please use the folliing links in order to access the differebt dashboards')
print(f'>>> MongoDB: {os.environ["MONGODB_DASHBOARD"]}')
print(f'>>> RabbitMQ: {os.environ["RABBITMQ_DASHBOARD"]}')
print(f'>>> InfluxDB: {os.environ["INFLUXDB_DASHBOARD"]}')

AGENT_MODE = os.environ["AGENT_MODE"]
if AGENT_MODE == "test":
    print('\n####### EVERYTHING LOOKS READY ######')
else:
    print(
        f'\n####### STARTING ENVIRONMENT WITH AGENT IN MODE [{AGENT_MODE}] ######')
    logger: Logger = Logger()

    env: GameEnv = GameEnv(
        logger,
        krpc,
        os.environ['SAVED_GAME_NAME']
    )

    agent: Agent = Agent(
        logger,
        mongo,
        rabbit,
        influx,
        env,
        AGENT_MODE,
        os.environ["MODEL_NAME"],
        os.environ["MODEL_VERSION"],
        os.environ["HOST_NAME"]
    )

    engine = Engine(
        logger,
        env,
        agent,
        int(os.environ['EPISODES']),
        int(os.environ['MAX_TRAJECTORY_STEPS'])
    )
    engine.run()
