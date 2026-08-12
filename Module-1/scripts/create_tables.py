from models.database import Base
from models.database import engine

# Import all models
from models.document import Document
from models.page import Page
from models.section import Section
from models.paragraph import Paragraph
from models.csv_file import CSVFile
from models.csv_record import CSVRecord


# ----------------------------------
# CREATE DATABASE TABLES
# ----------------------------------

def create_tables():

    Base.metadata.create_all(engine)

    print(
        "Database tables created successfully!"
    )


# ----------------------------------
# MAIN
# ----------------------------------

if __name__ == "__main__":

    create_tables()