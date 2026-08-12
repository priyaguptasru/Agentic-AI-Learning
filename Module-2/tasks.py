import time

from celery_app import celery_app


@celery_app.task
def process_pdf(filename):

    print("=" * 50)
    print("Celery Worker Started")
    print(f"Processing : {filename}")
    print("=" * 50)

    print("Extracting PDF...")
    time.sleep(3)

    print("Generating Embeddings...")
    time.sleep(2)

    print("Saving into Database...")
    time.sleep(2)

    print("PDF Processed Successfully")

    return f"{filename} processed successfully"