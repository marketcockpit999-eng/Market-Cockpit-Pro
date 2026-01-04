import pandas as pd
import pandas_datareader.data as web
import datetime

# Test data integration logic
FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

# Load manual data
manual_csv = "manual_h41_data.csv"
df_manual = pd.read_csv(manual_csv, index_col=0, parse_dates=True)
print("Manual data:")
print(df_manual)
print(f"\nManual data index: {df_manual.index}")

# Load FRED data (small sample)
end = datetime.datetime.now()
start = end - datetime.timedelta(days=30)
df_fred = web.DataReader('WALCL', 'fred', start, end, api_key=FRED_API_KEY)
print(f"\nFRED data index (last 5):")
print(df_fred.index[-5:])

# Check if dates match
print(f"\nDate in manual CSV: {df_manual.index[0]}")
print(f"Date in FRED: {df_fred.index[-1]}")
print(f"Dates match: {df_manual.index[0] in df_fred.index}")

# Test merge
print("\n--- Testing merge logic ---")
for date in df_manual.index:
    print(f"Checking date: {date}")
    if date in df_fred.index:
        print(f"  Date EXISTS in FRED DataFrame")
    else:
        print(f"  Date NOT FOUND in FRED DataFrame")
        print(f"  Closest dates in FRED: {df_fred.index[-3:]}")
