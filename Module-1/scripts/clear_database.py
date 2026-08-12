import os
import sys

# ----------------------------------
# ADD MODULE-1 TO PYTHON PATH
# ----------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

MODULE1_DIR = os.path.dirname(CURRENT_DIR)

if MODULE1_DIR not in sys.path:
    sys.path.append(MODULE1_DIR)

# ----------------------------------

from sqlalchemy import text

from models.session import SessionLocal


def clear_database():

    db = SessionLocal()

    try:

        db.execute(
            text("""
                TRUNCATE TABLE
                    paragraphs,
                    sections,
                    pages,
                    documents
                RESTART IDENTITY CASCADE;
            """)
        )

        db.commit()

        print("Database cleared successfully.")

    finally:

        db.close()


if __name__ == "__main__":

    clear_database()