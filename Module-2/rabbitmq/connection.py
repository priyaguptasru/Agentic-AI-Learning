import pika


class RabbitMQConnection:

    def __init__(self):
        self.host = "localhost"
        self.port = 5672
        self.username = "guest"
        self.password = "guest"

    def get_connection(self):

        credentials = pika.PlainCredentials(
            self.username,
            self.password
        )

        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials
        )

        return pika.BlockingConnection(parameters)