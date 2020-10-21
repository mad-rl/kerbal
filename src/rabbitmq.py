import json
import pika


class ExperienceMessage():
    def __init__(
        self,
        host: str,
        state: list,
        action: int,
        reward: float,
        next_state: list
    ):
        self.host: str = host
        self.state: list = state
        self.action: int = action
        self.reward: float = reward
        self.next_state: list = next_state

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __iter__(self):
        yield 'host', self.host
        yield 'state', self.state
        yield 'action', self.action
        yield 'reward', self.reward
        yield 'next_state', self.next_state

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
        self.experiences_batch: list = []

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
            experience_json['state'],
            experience_json['action'],
            experience_json['reward'],
            experience_json['next_state']
        )
        self.experiences_batch.append(experienceMessage)
        method, properties, body = ch.basic_get(queue=self.queue)
        if method is None:
            self.stop_consuming()

    def get_all_experiences(self) -> list:
        self.experiences_batch = []
        print("start consuming")
        self.start_consuming()
        print(f"experiences received {len(self.experiences_batch)}")
        print("stop consuming")
        return self.experiences_batch

    def start_consuming(self):
        self.channel.basic_consume(queue=self.queue,
                                   auto_ack=True,
                                   on_message_callback=self.__on_experience_received__)
        self.channel.start_consuming()

    def stop_consuming(self):
        self.channel.stop_consuming()

    def close_conn(self):
        self.connection.close()
