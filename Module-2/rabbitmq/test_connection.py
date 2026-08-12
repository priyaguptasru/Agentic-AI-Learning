import time
from rabbitmq.connection import RabbitMQConnection

connection = RabbitMQConnection().get_connection()

print("Connected")
print("Sleeping for 60 seconds...")

time.sleep(60)

connection.close()

print("Connection Closed")
