from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS


class Metric():
    def __init__(
        self,
        measurement: str,
        host: str,
        model_name: str,
        model_version: str,
        episode: int,
        step: int
    ):
        self.measurement: str = measurement
        self.host: str = host
        self.model_name: str = model_name
        self.model_version: str = model_version
        self.episode: int = episode
        self.step: int = step
        self.ts = datetime.utcnow()


class Metric_Reward(Metric):
    def __init__(
        self,
        host: str,
        model_name: str,
        model_version: str,
        episode: int,
        step: int,
        reward: float
    ):
        super().__init__(
            "reward",
            host,
            model_name,
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
        self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)

    def send_reward(self, metric: Metric_Reward):
        _point = Point(metric.measurement)
        _point.tag("host", metric.host)
        _point.tag("model_name", metric.model_name)
        _point.tag("episode", metric.episode)
        _point.field("model_version", metric.model_version)
        _point.field("step", metric.step)
        _point.field("reward", metric.reward)
        _point.time(metric.ts, WritePrecision.NS)
        self.write_api.write(bucket=self.bucket, record=[_point])
