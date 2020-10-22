import json
import pika


class ExperienceMessage():
    def __init__(
        self,
        model_version: str,
        host: str,
        state: list,
        action: int,
        reward: float,
        next_state: list
    ):
        self.model_version: str = model_version
        self.host: str = host
        self.state: list = state
        self.action: int = action
        self.reward: float = reward
        self.next_state: list = next_state

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __iter__(self):
        yield 'model_version', self.model_version
        yield 'host', self.host
        yield 'state', self.state
        yield 'action', self.action
        yield 'reward', self.reward
        yield 'next_state', self.next_state

    def to_dict(self) -> dict:
        return dict(self)


class RabbitMQHelper():
    def __init__(self, rabbit_conn_url: str, rabbit_api_url: str):
        params = pika.URLParameters(rabbit_conn_url)
        params.socket_timeout = 5
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.queue_name = ""
        self.api_url = rabbit_api_url

    def new_queue(self, queue_name: str):
        # print(f"declaring new queue [{queue_name}]")
        self.queue_name = queue_name
        self.queue_status = self.channel.queue_declare(
            queue=self.queue_name, auto_delete=True)
        self.experiences_batch: list = []

    def send_experience(self, experience: ExperienceMessage):
        self.new_queue(experience.model_version)

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=experience.to_json()
        )

    def __on_experience_received__(self, ch, method, properties, body):
        message_json: dict = json.loads(body)

        if message_json.get("finish") is True:
            self.stop_consuming()
        else:
            experienceMessage: ExperienceMessage = ExperienceMessage(
                message_json['model_version'],
                message_json['host'],
                message_json['state'],
                message_json['action'],
                message_json['reward'],
                message_json['next_state']
            )
            self.experiences_batch.append(experienceMessage)

    def get_all_experiences_by_model_version(self, model_version: str) -> list:
        self.experiences_batch = []
        # print("start consuming")
        self.start_consuming(model_version)
        print(f"experiences received {len(self.experiences_batch)}")
        # print("stop consuming")
        return self.experiences_batch

    def start_consuming(self, model_version: str):
        if model_version != self.queue_name:
            self.new_queue(model_version)

        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps({"finish": True})
        )

        print(f"start_consuming from queue {self.queue_name}")

        self.channel.basic_consume(queue=self.queue_name,
                                   auto_ack=True,
                                   on_message_callback=self.__on_experience_received__)
        self.channel.start_consuming()

    def stop_consuming(self):
        # print("stop_consuming")
        self.channel.stop_consuming()

    def close_conn(self):
        self.connection.close()
