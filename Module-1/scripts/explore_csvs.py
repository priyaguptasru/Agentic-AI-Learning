import os
import pandas as pd

base_dir = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

csv_folder = os.path.join(
    base_dir,
    "data",
    "csvs"
)

for file_name in os.listdir(csv_folder):

    if file_name.endswith(".csv"):

        file_path = os.path.join(
            csv_folder,
            file_name
        )

        print("\n" + "=" * 50)
        print("File:", file_name)

        df = pd.read_csv(file_path)

        print("\nRows, Columns:")
        print(df.shape)

        print("\nColumn Names:")
        print(df.columns.tolist())

        print("\nData Types:")
        print(df.dtypes)

        print("\nMissing Values:")
        print(df.isnull().sum())