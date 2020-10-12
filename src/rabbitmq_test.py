import os
from rabbitmq import ExperienceMessage, RabbitMQHelper

RABBITMQ_CONN_URL = os.environ.get(
    'RABBITMQ_CONN_URL', 'amqps://hwoyewux:vXqL372CvK4JdD_kJTVhdUcRRX1FZeYm@kangaroo.rmq.cloudamqp.com/hwoyewux')
RABBITMQ_QUEUE = os.environ.get('RABBITMQ_QUEUE', 'test_experiences')

rabbitmq: RabbitMQHelper = RabbitMQHelper(RABBITMQ_CONN_URL, RABBITMQ_QUEUE)

exp: ExperienceMessage = ExperienceMessage(
    1,
    2,
    [1, 2, 3],
    3,
    -0.9,
    1.4
)

rabbitmq.send_experience(exp)


def callback(experience_message: ExperienceMessage):
    print(experience_message.to_json())
    rabbitmq.close_conn()


rabbitmq.start_consuming(callback)
