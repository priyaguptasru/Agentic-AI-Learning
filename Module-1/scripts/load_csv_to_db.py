import os
import pandas as pd

from scripts.logger import log_error

from models.session import SessionLocal

from models.csv_file import CSVFile
from models.csv_record import CSVRecord


# ----------------------------------
# LOAD CSV TO DATABASE
# ----------------------------------

def load_csv_to_db():

    # ----------------------------------
    # FIND CLEANED CSV FOLDER
    # ----------------------------------

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    csv_folder = os.path.join(
        base_dir,
        "output",
        "cleaned_csv"
    )

    # ----------------------------------
    # CREATE DATABASE SESSION
    # ----------------------------------

    db = SessionLocal()

    try:

        # ----------------------------------
        # PROCESS CSV FILES
        # ----------------------------------

        for file_name in os.listdir(csv_folder):

            if not file_name.endswith(".csv"):
                continue

            print(
                f"\nProcessing: {file_name}"
            )

            file_path = os.path.join(
                csv_folder,
                file_name
            )

            # ----------------------------------
            # READ CSV
            # ----------------------------------

            try:

                df = pd.read_csv(
                    file_path
                )

            except Exception as e:

                log_error(
                    f"CSV Read Failed | "
                    f"{file_name} | {e}"
                )

                print(
                    f"Skipped: {file_name}"
                )

                continue

            # ----------------------------------
            # LOAD INTO DATABASE
            # ----------------------------------

            try:

                # ----------------------------------
                # CHECK IF FILE ALREADY LOADED
                # ----------------------------------

                existing_file = (
                    db.query(CSVFile)
                    .filter(
                        CSVFile.file_name == file_name
                    )
                    .first()
                )

                if existing_file:

                    print(
                        f"Already Loaded: {file_name}"
                    )

                    continue

                # ----------------------------------
                # INSERT CSV FILE METADATA
                # ----------------------------------

                csv_file = CSVFile(
                    file_name=file_name,
                    total_rows=len(df)
                )

                db.add(csv_file)

                db.flush()

                # ----------------------------------
                # INSERT RECORDS
                # ----------------------------------

                for _, row in df.iterrows():
                    '''Instead of creating separate database columns for every CSV schema, the project stores each row in the record_data JSON field.
                    csv_files stores metadata about each uploaded CSV (such as file name and row count), while csv_records stores the actual data rows. This creates a normalized one-to-many relationship and avoids repeating file information for every record.'''

                    row_json = row.to_dict()

                    record = CSVRecord(
                        file_id=csv_file.file_id,
                        record_data=row_json
                    )

                    db.add(record)

                db.commit()

                print(
                    f"Loaded: {file_name}"
                )

            except Exception as e:

                db.rollback()

                log_error(
                    f"CSV Load Failed | "
                    f"{file_name} | {e}"
                )

                print(
                    f"Skipped: {file_name}"
                )

                continue

    finally:

        # ----------------------------------
        # CLOSE DATABASE SESSION
        # ----------------------------------

        db.close()

    print(
        "\nAll CSV files loaded successfully!"
    )


# ----------------------------------
# MAIN
# ----------------------------------

if __name__ == "__main__":

    load_csv_to_db()