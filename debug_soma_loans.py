import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

# テスト対象のFRED ID
test_ids = {
    'SOMA_Bills': 'WSHOBILL',
    'Total_Loans': 'WLCFL',
    'Primary_Credit': 'WLCFLPCL',
}

end = datetime.datetime.now()
start = end - datetime.timedelta(days=730)

print("=" * 60)
print("FRED Data Availability Test")
print("=" * 60)

for name, fred_id in test_ids.items():
    print(f"\nTesting: {name} ({fred_id})")
    print("-" * 40)
    try:
        data = web.DataReader(fred_id, 'fred', start, end, api_key=FRED_API_KEY)
        print(f"[OK] Success! Got {len(data)} rows")
        print(f"   Latest date: {data.index[-1]}")
        print(f"   Latest value: {data.iloc[-1, 0]:.2f}")
        print(f"   First 3 rows:")
        print(data.head(3))
    except Exception as e:
        print(f"[FAIL] Failed: {str(e)}")

print("\n" + "=" * 60)
print("Testing alternative IDs for Total Loans:")
print("=" * 60)

alternative_ids = {
    'H41RESPALDKNWW': 'H41: Total Discount Window Borrowing',
    'DISCBORR': 'Discount Window Primary Credit',
    'WLCFL': 'Total Loans, All Commercial Banks',
}

for fred_id, description in alternative_ids.items():
    print(f"\n{description} ({fred_id})")
    try:
        data = web.DataReader(fred_id, 'fred', start, end, api_key=FRED_API_KEY)
        print(f"[OK] Got {len(data)} rows, Latest: {data.iloc[-1, 0]:.2f}")
    except Exception as e:
        print(f"[FAIL] {str(e)[:50]}")
