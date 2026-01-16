import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

test_ids = {
    'FBTSLB': 'SOMA Bills (FRB Treasury Short-term)',
    'H41RESPPDLKWW': 'Total Loans (H.4.1 Table 1B)'
}

end = datetime.datetime.now()
start = end - datetime.timedelta(days=365)

print("Testing NEW FRED IDs...")
print("=" * 60)

for fred_id, description in test_ids.items():
    print(f"\n{fred_id}: {description}")
    try:
        data = web.DataReader(fred_id, 'fred', start, end, api_key=FRED_API_KEY)
        if len(data) > 0:
            print(f"  [SUCCESS!] Got {len(data)} rows")
            print(f"  Latest date: {data.index[-1]}")
            print(f"  Latest value: {data.iloc[-1, 0]:.2f}")
            print(f"  Data frequency: {data.index.inferred_freq}")
            print(f"  Last 5 values:")
            print(data.tail(5))
        else:
            print("  [EMPTY] No data")
    except Exception as e:
        print(f"  [FAIL] {str(e)[:100]}")
