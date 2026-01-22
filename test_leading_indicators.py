# -*- coding: utf-8 -*-
"""
Test script to verify ISM_PMI and Leading_Index data from FRED
"""
import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

# Test indicators
indicators_to_test = {
    'ISM_PMI': 'NAPM',
    'Leading_Index': 'USSLIND',
}

end = datetime.datetime.now()
start = end - datetime.timedelta(days=365)  # 1 year

print("="*60)
print("Testing Leading Indicators from FRED")
print("="*60)

for name, series_id in indicators_to_test.items():
    print(f"\n{name} ({series_id}):")
    print("-" * 40)
    try:
        data = web.DataReader(series_id, 'fred', start, end, api_key=FRED_API_KEY)
        if data is not None and len(data) > 0:
            print(f"[OK] SUCCESS: {len(data)} rows retrieved")
            print(f"  Latest date: {data.index[-1].strftime('%Y-%m-%d')}")
            print(f"  Latest value: {data.iloc[-1].values[0]:.2f}")
            print(f"  First 5 values:")
            print(data.head())
        else:
            print("[ERROR] FAILED: No data returned")
    except Exception as e:
        print(f"[ERROR]: {str(e)}")

print("\n" + "="*60)
print("Test Complete")
print("="*60)
