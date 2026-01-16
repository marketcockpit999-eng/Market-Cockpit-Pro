import pandas_datareader.data as web
import datetime
import os

os.environ["FRED_API_KEY"] = "4e9f89c09658e42a4362d1251d9a3d05"
end = datetime.datetime.now()
start = end - datetime.timedelta(days=90)

# Test the banking sector FRED IDs
test_ids = {
    'Bank_Cash': 'CASSH',
    'Lending_Standards': 'DRTSCWMBS',
    'US_M2': 'M2SL',
    'US_CPI': 'CPIAUCSL'
}

print("=== Banking Sector Data Diagnostics ===\n")
for name, fred_id in test_ids.items():
    try:
        data = web.DataReader(fred_id, 'fred', start, end)
        if data.empty:
            print(f"{name} ({fred_id}): ❌ EMPTY DATA")
        else:
            latest = data.iloc[-1].values[0]
            latest_date = data.index[-1]
            print(f"{name} ({fred_id}): ✓ OK")
            print(f"  Latest: {latest:.2f} ({latest_date})")
            print(f"  Rows: {len(data)}")
    except Exception as e:
        print(f"{name} ({fred_id}): ❌ ERROR")
        print(f"  {str(e)[:100]}")
    print()
