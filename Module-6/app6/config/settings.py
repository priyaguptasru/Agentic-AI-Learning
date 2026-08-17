import os

from dotenv import load_dotenv

load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = os.getenv("MODEL_NAME")

TEMPERATURE = float(
    os.getenv(
        "TEMPERATURE",
        "0",
    )
)

DATABASE_URL = os.getenv("DATABASE_URL")
