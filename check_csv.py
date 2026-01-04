import pandas as pd
import os

# Check CSV file
csv_file = "manual_h41_data.csv"

if os.path.exists(csv_file):
    print(f"CSV file exists: {csv_file}")
    df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
    print(f"\nData in CSV:")
    print(df)
    print(f"\nData types:")
    print(df.dtypes)
    print(f"\nIndex:")
    print(df.index)
else:
    print(f"CSV file NOT found: {csv_file}")
