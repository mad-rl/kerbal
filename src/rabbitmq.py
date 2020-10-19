import json
import time
import pika


class ExperienceMessage():
    def __init__(
        self,
        host: str,
        episode: int,
        step: int,
        state: list,
        action: int,
        reward: float,
        value: float
    ):
        self.host: str = host
        self.episode: int = episode
        self.step: int = step
        self.state: list = state
        self.action: int = action
        self.reward: float = reward
        self.value: int = value
        self.ts = int(time.time()*100000)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __iter__(self):
        yield 'host', self.host
        yield 'episode', self.episode
        yield 'step', self.step
        yield 'state', self.state
        yield 'action', self.action
        yield 'reward', self.reward
        yield 'value', self.value

    def to_dict(self) -> dict:
        return dict(self)


class RabbitMQHelper():
    def __init__(self, url, queue):
        params = pika.URLParameters(url)
        params.socket_timeout = 5
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.queue = queue
        self.channel.queue_declare(queue=self.queue)

    def send_experience(self, experience: ExperienceMessage):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            body=experience.to_json()
        )

    def __on_experience_received__(self, ch, method, properties, body):
        experience_json: dict = json.loads(body)
        experienceMessage: ExperienceMessage = ExperienceMessage(
            experience_json['host'],
            experience_json['episode'],
            experience_json['step'],
            experience_json['state'],
            experience_json['action'],
            experience_json['reward'],
            experience_json['value']
        )
        self.boundCallback(experienceMessage)

    # callback(ch, method, properties, body):
    def start_consuming(self, boundCallback):
        self.boundCallback = boundCallback
        self.channel.basic_consume(queue=self.queue,
                                   auto_ack=True,
                                   on_message_callback=self.__on_experience_received__)
        self.channel.start_consuming()

    def close_conn(self):
        self.connection.close()
