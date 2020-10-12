import random
import time
from influxdb import Metric_Reward, InfluxDBHelper

INLFUXDB_URL = "https://us-central1-1.gcp.cloud2.influxdata.com"
INFLUXDB_ACCESS_TOKEN = "waV8QrVEyI6meORF2ylDVDWqj-1acvn_SKwXw25-iD9KKN-mi3femljDy8o9JInrYXh7drqULlIbi5eBLCzmkA=="
INFLUXDB_CLIENT_HOSTNAME = "jonas_local"
INFLUXDB_ORG = "93d1b9af98b85018"
INFLUXDB_BUCKET = "test_mad_rl_kerbal"

idb: InfluxDBHelper = InfluxDBHelper(
    INLFUXDB_URL,
    INFLUXDB_ACCESS_TOKEN,
    INFLUXDB_ORG,
    INFLUXDB_BUCKET,
    INFLUXDB_CLIENT_HOSTNAME
)

exp = 0
metrics = []
while exp < 100:
    exp = exp + 1
    time.sleep(random.randrange(1, 10))
    mr: Metric_Reward = Metric_Reward(
        f'ppo_v{exp}',
        f'exp00{exp}',
        exp+1,
        exp+2,
        random.randrange(1, 10000)/10000*-1
    )
    idb.send_reward(mr)
    print(idb.client.health())
    print(mr)
