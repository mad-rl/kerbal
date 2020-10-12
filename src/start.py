import os
from influxdb import InfluxDBHelper
from mongodb import MongoDBHelper
from rabbitmq import RabbitMQHelper
from krpc_helper import KRPCHelper

from logger import Logger

from engine import Engine
from game_env import GameEnv
from agents.actor_critic.agent import Agent

# check influx connectivity
print('checking influxdb access...')
influx: InfluxDBHelper = InfluxDBHelper(
    os.environ["INLFUXDB_URL"],
    os.environ["INFLUXDB_ACCESS_TOKEN"],
    os.environ["INFLUXDB_ORG"],
    os.environ["INFLUXDB_BUCKET"],
    os.environ["INFLUXDB_CLIENT_HOSTNAME"]
)
print('INFLUXDB IS READY')

# check mongo connectivity
print('checking mongodb access...')
mongo: MongoDBHelper = MongoDBHelper(
    os.environ["MONGODB_HOST"],
    os.environ["MONGODB_USER"],
    os.environ["MONGODB_PASSWORD"],
    os.environ["MONGODB_DBNAME"]
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
krpc: KRPCHelper = KRPCHelper(
    os.environ["KRPC_ADDRESS"],
    int(os.environ["KRPC_RPC_PORT"]),
    int(os.environ["KRPC_STREAM_PORT"])
)

AGENT_MODE = os.environ["AGENT_MODE"]
if AGENT_MODE == "test":
    print('all working')
else:
    logger: Logger = Logger()
    env: GameEnv = GameEnv(
        logger,
        krpc,
        os.environ['SAVED_GAME_NAME']
    )
    agent: Agent = Agent(
        logger,
        mongo,
        AGENT_MODE,
        env,
        ''
    )
    engine = Engine(
        logger,
        rabbit,
        influx,
        env,
        agent,
        int(os.environ['EPISODES']),
        int(os.environ['MAX_STEPS_PER_EPISODE'])
    )
    engine.run()
