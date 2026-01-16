import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

end = datetime.datetime.now()
start = end - datetime.timedelta(days=365)

test_ids = {
    'TREASBILL': 'SOMA Bills (Treasury Bills in SOMA)',
    'TOTLOAN': 'Total Loans (Discount Window)'
}

print("Testing new FRED IDs...")
print("=" * 60)

for fred_id, description in test_ids.items():
    print(f"\n{fred_id}: {description}")
    try:
        data = web.DataReader(fred_id, 'fred', start, end, api_key=FRED_API_KEY)
        if len(data) > 0:
            print(f"  [OK] Got {len(data)} rows")
            print(f"  Latest date: {data.index[-1]}")
            print(f"  Latest value: {data.iloc[-1, 0]:.2f}")
            print(f"  Last 3 values:")
            print(data.tail(3))
        else:
            print("  [EMPTY] No data")
    except Exception as e:
        print(f"  [FAIL] {str(e)[:100]}")
