import os
import pandas as pd

from scripts.logger import log_error


# --------------------------------------------------
# CLEAN CSV DATA
# --------------------------------------------------

def clean_csv_data():

    # Move from scripts -> Module-1
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    input_folder = os.path.join(
        base_dir,
        "data",
        "csvs"
    )

    output_folder = os.path.join(
        base_dir,
        "output",
        "cleaned_csv"
    )

    log_folder = os.path.join(
        base_dir,
        "output",
        "logs"
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    os.makedirs(
        log_folder,
        exist_ok=True
    )

    report_file = os.path.join(
        log_folder,
        "data_quality_report.txt"
    )

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as report:

        report.write(
            "DATA QUALITY REPORT\n"
        )

        report.write(
            "=" * 60 + "\n\n"
        )

        for file_name in os.listdir(input_folder):

            if not file_name.endswith(".csv"):
                continue

            file_path = os.path.join(
                input_folder,
                file_name
            )

            print(
                f"\nProcessing: {file_name}"
            )

            # ----------------------------
            # READ CSV
            # ----------------------------

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

            # original_rows = len(df)

            duplicate_count = (
                df.duplicated().sum()
            )


            missing_values = (
                df.isnull().sum()
            )
            

            # ----------------------------
            # REPORT
            # ----------------------------

            report.write(
                f"File: {file_name}\n"
            )

            report.write(
                f"Rows: {df.shape[0]}\n"
            )

            report.write(
                f"Columns: {df.shape[1]}\n\n"
            )

            report.write(
                "Missing Values:\n"
            )

            for col, count in (
                missing_values.items()
            ):

                report.write(
                    f"{col}: {count}\n"
                )

            report.write(
                f"\nDuplicate Rows: "
                f"{duplicate_count}\n"
            )

            report.write(
                "\n" + "-" * 60 + "\n\n"
            )

            # ----------------------------
            # CLEANING
            # ----------------------------

            df = df.drop_duplicates()

            text_columns = (
                df.select_dtypes(
                    include=[
                        "object",
                        "string"
                    ]
                ).columns
            )

            for col in text_columns:

                df[col] = (
                    df[col]
                    .astype(str)
                    .str.strip()
                )

                df[col] = (
                    df[col]
                    .replace(
                        [
                            "nan",
                            "None"
                        ],
                        pd.NA
                    )
                )

                df[col] = (
                    df[col]
                    .fillna(
                        "Unknown"
                    )
                )

            numeric_columns = (
                df.select_dtypes(
                    include="number"
                ).columns
            )

            for col in numeric_columns:

                df[col] = (
                    df[col]
                    .fillna(
                        df[col].median()
                    )
                )

            output_file = os.path.join(
                output_folder,
                file_name
            )

            # ----------------------------
            # SAVE CSV
            # ----------------------------

            try:

                df.to_csv(
                    output_file,
                    index=False
                )

            except Exception as e:

                log_error(
                    f"CSV Save Failed | "
                    f"{file_name} | {e}"
                )

                print(
                    f"Skipped Saving: "
                    f"{file_name}"
                )

                continue

            print(
                f"Saved: {output_file}"
            )

    print(
        "\nAll CSV files processed successfully!"
    )

    print(
        f"Report saved to: {report_file}"
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    clean_csv_data()