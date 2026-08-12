from celery import Celery

celery_app = Celery(
    "module2",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://",
    include=["tasks"],
)

celery_app.conf.update(task_default_queue="pdf_queue")
