import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

end = datetime.datetime.now()
start = end - datetime.timedelta(days=365)

print("Testing correct SOMA Bills ID: WHTLSBL")
try:
    data = web.DataReader('WHTLSBL', 'fred', start, end, api_key=FRED_API_KEY)
    print(f"[OK] Got {len(data)} rows")
    print(f"Latest date: {data.index[-1]}")
    print(f"Latest value: {data.iloc[-1, 0]:.2f} Billions")
    print("\nLast 5 values:")
    print(data.tail())
except Exception as e:
    print(f"[FAIL] {str(e)}")
