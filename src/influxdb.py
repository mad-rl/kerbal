from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


class Metric():
    def __init__(
        self,
        measurement: str,
        model_version: str,
        episode: int,
        step: int
    ):
        self.measurement: str = measurement
        self.model_version: str = model_version
        self.episode: int = episode
        self.step: int = step
        self.ts = datetime.utcnow()


class Metric_Reward(Metric):
    def __init__(
        self,
        model_version: str,
        episode: int,
        step: int,
        reward: float
    ):
        super().__init__(
            "reward",
            model_version,
            episode,
            step
        )
        self.reward: float = reward


class InfluxDBHelper():
    def __init__(
        self,
        url: str,
        token: str,
        org: str,
        bucket: str
    ):
        self.org: str = org
        self.bucket: str = bucket
        self.client: InfluxDBClient = InfluxDBClient(
            url=url,
            token=token,
            org=org
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def send_reward(self, metric: Metric_Reward):
        _point = Point(metric.measurement)
        _point.tag("model_version", metric.model_version)
        _point.field("episode", metric.episode)
        _point.field("step", metric.step)
        _point.field("reward", metric.reward)
        _point.time(metric.ts, WritePrecision.NS)
        self.write_api.write(bucket=self.bucket, record=[_point])