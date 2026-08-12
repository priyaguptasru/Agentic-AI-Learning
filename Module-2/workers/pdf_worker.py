import json

from rabbitmq.connection import RabbitMQConnection


class PDFWorker:

    def __init__(self):

        self.connection = RabbitMQConnection().get_connection()

        self.channel = self.connection.channel()

        self.channel.basic_qos(prefetch_count=1)

        self.channel.queue_declare(queue="pdf_queue", durable=True)

    def callback(self, ch, method, properties, body):

        message = json.loads(body)

        print("=" * 50)
        print("PDF Processing Started")
        print(f"Filename : {message['filename']}")
        print(f"Task     : {message['task']}")
        print("=" * 50)

        # Simulate PDF Processing
        print("Extracting PDF...")
        print("Generating Embeddings...")
        print("Saving into Database...")

        print("PDF Processed Successfully")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):

        self.channel.basic_consume(
            queue="pdf_queue", on_message_callback=self.callback, auto_ack=False
        )

        print("Waiting for PDF Tasks...")

        self.channel.start_consuming()


if __name__ == "__main__":

    worker = PDFWorker()

    worker.start()
