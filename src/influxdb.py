from datetime import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS


class Metric():
    def __init__(
        self,
        measurement: str,
        model_version: str,
        experiment_id: str,
        episode: int,
        step: int
    ):
        self.measurement: str = measurement
        self.model_version: str = model_version
        self.experiment_id: str = experiment_id
        self.episode: int = episode
        self.step: int = step
        self.ts: int = int(datetime.now().timestamp()*1000000000)


class Metric_Reward(Metric):
    def __init__(
        self,
        model_version: str,
        experiment_id: str,
        episode: int,
        step: int,
        reward: float
    ):
        super().__init__(
            "reward",
            model_version,
            experiment_id,
            episode,
            step
        )
        self.reward: float = reward


class InfluxDBHelper():
    def __init__(self, url: str, token: str, org: str, bucket: str, host: str):
        self.org: str = org
        self.bucket: str = bucket
        self.host_name: str = host

        self.client: InfluxDBClient = InfluxDBClient(
            url=url,
            token=token,
            org=org
        )
        self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)

    def send_reward(self, metric: Metric_Reward):
        _point = Point(metric.measurement)
        _point.tag("model_version", metric.model_version)
        _point.tag("experiment_id", metric.experiment_id)
        _point.field("episode", metric.episode)
        _point.field("step", metric.step)
        _point.field("reward", metric.reward)
        _point.time(metric.ts)
        self.write_api.write(bucket=self.bucket, record=[_point])
