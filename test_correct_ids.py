"""Test correct FRED series IDs for SLOOS"""
import requests

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

# Corrected FRED IDs based on FRED website search
test_ids = {
    # C&I Lending Standards
    'DRTSCILM': 'C&I Std Large/Mid (existing)',
    'DRTSCIS': 'C&I Std Small Firms',  # Corrected from DRSTSS
    'DRTSCLCC': 'C&I Demand Large/Mid', # Different ID pattern
    
    # CRE Lending  
    'DRTSSP': 'CRE Std All Property Types',
    'DRTSCRE': 'CRE Std Total',
    'SUBLPDR': 'CRE Subprime',
    
    # SOMA Bills alternatives
    'TREAST': 'Treasury Securities Held',
    'WSHOMCB': 'SOMA Holdings',
}

print("=== Testing Corrected FRED IDs ===")
for fred_id, name in test_ids.items():
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={fred_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit=3"
        response = requests.get(url, timeout=15)
        data = response.json()
        
        if 'observations' in data and len(data['observations']) > 0:
            obs = data['observations'][0]
            print(f"OK    {fred_id:15s}: {obs['value']:>10s} ({obs['date']}) - {name}")
        else:
            err = data.get('error_message', 'No data')[:40]
            print(f"FAIL  {fred_id:15s}: {err} - {name}")
    except Exception as e:
        print(f"ERROR {fred_id:15s}: {str(e)[:40]} - {name}")
