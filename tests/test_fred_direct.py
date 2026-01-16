"""Test FRED API using direct HTTP request instead of pandas_datareader"""
import requests
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

# Test indicators that failed with pandas_datareader
failed_ids = ['WHTLSBL', 'DRSTDCL', 'DRSTSS', 'DRSDCL', 'SUBLPDRNS', 'SUBLPDRMF', 'DRSDRE']

print("=== Direct FRED API Test ===")
for fred_id in failed_ids:
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={fred_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=5"
        response = requests.get(url, timeout=15)
        data = response.json()
        
        if 'observations' in data and len(data['observations']) > 0:
            obs = data['observations'][0]
            print(f"OK    {fred_id}: {obs['value']} ({obs['date']})")
        else:
            print(f"EMPTY {fred_id}: {data.get('error_message', 'No observations')[:50]}")
    except Exception as e:
        print(f"ERROR {fred_id}: {str(e)[:50]}")
