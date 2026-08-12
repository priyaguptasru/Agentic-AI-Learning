import json

import pika

from rabbitmq.connection import RabbitMQConnection


class Producer:

    def __init__(self):

        self.connection = RabbitMQConnection().get_connection()
        self.channel = self.connection.channel()

    def publish_pdf_task(self, filename):

        message = {"filename": filename, "task": "process_pdf"}

        self.channel.basic_publish(
            exchange="",
            routing_key="pdf_queue",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),  # Persistent Message
        )

        print(f"Message Sent : {filename}")

    def close(self):
        self.connection.close()


if __name__ == "__main__":

    producer = Producer()

    for i in range(1, 6):
        producer.publish_pdf_task(f"invoice_{i}.pdf")

    producer.close()
