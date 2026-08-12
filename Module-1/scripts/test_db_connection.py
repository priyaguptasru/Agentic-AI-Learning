from sqlalchemy import text

from models.database import engine

try:

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT version();")
        )

        print(
            result.fetchone()
        )

    print(
        "\nDatabase Connection Successful!"
    )

except Exception as e:

    print(
        f"Error: {e}"
    )