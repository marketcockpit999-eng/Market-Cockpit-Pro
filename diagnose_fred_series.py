# -*- coding: utf-8 -*-
"""
Enhanced diagnostic script to find correct FRED series IDs
Tests multiple possible series IDs for ISM PMI and Leading Index
"""
import pandas_datareader.data as web
import datetime
import requests

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

# Multiple candidate series IDs to test
test_cases = {
    'ISM Manufacturing PMI': [
        'NAPM',      # Current (Institute for Supply Management)
        'NAPMNOI',   # ISM Manufacturing: New Orders Index
        'ISM',       # Alternative
        'MANEMP',    # Manufacturing Employment
    ],
    'Leading Economic Index': [
        'USSLIND',   # Current (US Leading Index for United States)
        'LEADING',   # Alternative
        'LEI',       # Alternative
        'DCOILWTICO', # Try oil as proxy (shouldn't work but test)
    ],
}

end = datetime.datetime.now()
start = end - datetime.timedelta(days=730)  # 2 years

print("="*60)
print("FRED Series ID Diagnostic Tool")
print("="*60)

for indicator_name, series_ids in test_cases.items():
    print(f"\n{indicator_name}:")
    print("="*60)
    
    for series_id in series_ids:
        print(f"\nTesting: {series_id}")
        print("-" * 40)
        
        # First, check if series exists via FRED API
        api_url = f"https://api.stlouisfed.org/fred/series?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
        try:
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'seriess' in data and len(data['seriess']) > 0:
                    series_info = data['seriess'][0]
                    print(f"[OK] Series found in FRED!")
                    print(f"  Title: {series_info.get('title', 'N/A')}")
                    print(f"  Frequency: {series_info.get('frequency', 'N/A')}")
                    print(f"  Units: {series_info.get('units', 'N/A')}")
                    print(f"  Last Updated: {series_info.get('last_updated', 'N/A')}")
                    print(f"  Observation End: {series_info.get('observation_end', 'N/A')}")
                else:
                    print("[ERROR] Series not found in FRED")
                    continue
            else:
                print(f"[ERROR] HTTP {response.status_code}")
                continue
        except Exception as e:
            print(f"[ERROR] API check failed: {str(e)}")
            continue
        
        # Now try to fetch actual data
        try:
            df = web.DataReader(series_id, 'fred', start, end, api_key=FRED_API_KEY)
            if df is not None and len(df) > 0:
                print(f"[OK] Data retrieved: {len(df)} rows")
                print(f"  Latest date: {df.index[-1].strftime('%Y-%m-%d')}")
                print(f"  Latest value: {df.iloc[-1].values[0]:.2f}")
                print(f"  Sample data:")
                print(df.tail(3))
            else:
                print("[ERROR] No data returned")
        except Exception as e:
            print(f"[ERROR] Data fetch failed: {str(e)}")

print("\n" + "="*60)
print("Diagnostic Complete")
print("="*60)
