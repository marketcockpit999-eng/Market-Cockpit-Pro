import pandas as pd
import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

# Test a few FRED indicators to see their actual latest dates
indicators = {
    'WALCL': 'Fed Assets',
    'RRPONTSYD': 'ON RRP',
    'WRESBAL': 'Reserves',
    'EFFR': 'EFFR',
}

end = datetime.datetime.now()
start = end - datetime.timedelta(days=14)

print("Checking actual data dates from FRED:")
print("=" * 60)

for fred_id, name in indicators.items():
    try:
        data = web.DataReader(fred_id, 'fred', start, end, api_key=FRED_API_KEY)
        latest_date = data.index[-1]
        latest_value = data.iloc[-1].values[0]
        print(f"{name:15s} ({fred_id:10s}): {latest_date.strftime('%Y-%m-%d')} = {latest_value:.2f}")
    except Exception as e:
        print(f"{name:15s} ({fred_id:10s}): ERROR - {e}")

print("\n" + "=" * 60)
print(f"Today: {datetime.datetime.now().strftime('%Y-%m-%d')}")
