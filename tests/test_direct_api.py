import pandas as pd
import requests
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

# Test direct API access
test_ids = ['TREASBILL', 'TOTLOAN']

print("Testing FRED API direct access...")
print("=" * 60)

for series_id in test_ids:
    print(f"\n{series_id}:")
    
    # Method 1: Direct CSV download
    url_csv = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    print(f"  CSV URL: {url_csv}")
    resp_csv = requests.get(url_csv)
    print(f"  CSV Status: {resp_csv.status_code}")
    if resp_csv.status_code == 200:
        print(f"  CSV Content (first 200 chars): {resp_csv.text[:200]}")
    
# Method 2: FRED API endpoint
    url_api = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
    print(f"  API URL: {url_api[:80]}...")
    resp_api = requests.get(url_api)
    print(f"  API Status: {resp_api.status_code}")
    if resp_api.status_code == 200:
        try:
            data = resp_api.json()
            if 'observations' in data and len(data['observations']) > 0:
                latest = data['observations'][-1]
                print(f"  [OK] Latest: {latest['date']} = {latest['value']}")
            else:
                print(f"  API Response: {data}")
        except:
            print(f"  Response text: {resp_api.text[:200]}")
    else:
        print(f"  Error: {resp_api.text[:200]}")
