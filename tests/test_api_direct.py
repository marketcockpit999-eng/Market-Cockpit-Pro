import requests
import json

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

test_ids = ['FBTSLB', 'H41RESPPDLKWW', 'WLCFLPCL']  # Include working one for comparison

print("Direct FRED API test...")
print("=" * 60)

for series_id in test_ids:
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&limit=5&sort_order=desc"
    
    print(f"\n{series_id}:")
    try:
        resp = requests.get(url, timeout=10)
        print(f"  HTTP Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            if 'observations' in data and len(data['observations']) > 0:
                obs = data['observations']
                print(f"  [OK] Got {len(obs)} observations")
                print(f"  Latest: {obs[0]['date']} = {obs[0]['value']}")
            else:
                print(f"  Response keys: {list(data.keys())}")
        else:
            try:
                error = resp.json()
                print(f"  Error: {error}")
            except:
                print(f"  Text: {resp.text[:150]}")
    except Exception as e:
        print(f"  Exception: {str(e)}")
