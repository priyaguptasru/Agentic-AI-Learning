from rabbitmq.connection import RabbitMQConnection

connection = RabbitMQConnection().get_connection()

channel = connection.channel()

channel.queue_declare(queue="pdf_queue", durable=True)

print("Queue Created Successfully!")

connection.close()
