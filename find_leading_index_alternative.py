# -*- coding: utf-8 -*-
"""
Search FRED for alternative Leading Economic Index series
"""
import pandas_datareader.data as web
import datetime
import requests

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

# Candidate series for Leading Economic Index
candidates = {
    # Conference Board LEI (most common)
    'DSPIC96': 'Real Disposable Personal Income (not LEI but leading)',
    
    # OECD Leading Indicators
    'USALOLITONOSTSAM': 'OECD Leading Indicators: US (Amplitude Adjusted)',
    'USALORSGPNOSTSAM': 'OECD Leading Indicators: US (Trend Restored)',
    
    # Regional Fed Leading Indexes
    'SLCEILSI': 'St. Louis Fed Leading Index',
    'CFNAI': 'Chicago Fed National Activity Index',
    'CFNAIMA3': 'Chicago Fed National Activity Index: 3-Month Moving Average',
    
    # Philadelphia Fed State Leading Indexes (multiple states)
    'SLIND': 'Philadelphia Fed Leading Index (try this)',
    'CSLIND': 'Coincident Index (not leading, but try)',
    
    # Alternative Economic Indicators
    'NEWORDER': 'Manufacturers New Orders',
    'PERMIT': 'Building Permits',
    'UMCSENT': 'Consumer Sentiment',
    'UNRATE': 'Unemployment Rate',
}

end = datetime.datetime.now()
start = end - datetime.timedelta(days=730)  # 2 years

print("="*70)
print("Searching for Leading Economic Index Alternatives")
print("="*70)

successful_series = []

for series_id, description in candidates.items():
    print(f"\nTesting: {series_id}")
    print(f"Description: {description}")
    print("-" * 70)
    
    # Check if series exists
    api_url = f"https://api.stlouisfed.org/fred/series?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'seriess' in data and len(data['seriess']) > 0:
                series_info = data['seriess'][0]
                title = series_info.get('title', 'N/A')
                frequency = series_info.get('frequency', 'N/A')
                last_updated = series_info.get('last_updated', 'N/A')
                obs_end = series_info.get('observation_end', 'N/A')
                
                print(f"[OK] Series found!")
                print(f"  Title: {title}")
                print(f"  Frequency: {frequency}")
                print(f"  Last Updated: {last_updated}")
                print(f"  Obs End: {obs_end}")
                
                # Try to fetch data
                try:
                    df = web.DataReader(series_id, 'fred', start, end, api_key=FRED_API_KEY)
                    if df is not None and len(df) > 0:
                        latest_date = df.index[-1].strftime('%Y-%m-%d')
                        latest_value = df.iloc[-1].values[0]
                        
                        print(f"[OK] Data retrieved: {len(df)} rows")
                        print(f"  Latest: {latest_date} = {latest_value:.2f}")
                        
                        # Check if data is recent (within last 6 months)
                        if (datetime.datetime.now() - df.index[-1]).days < 180:
                            print("  [RECOMMENDED] Data is recent!")
                            successful_series.append({
                                'series_id': series_id,
                                'description': description,
                                'title': title,
                                'frequency': frequency,
                                'latest_date': latest_date,
                                'latest_value': latest_value,
                                'rows': len(df)
                            })
                        else:
                            print(f"  [WARNING] Data is old (last: {latest_date})")
                except Exception as e:
                    print(f"[ERROR] Data fetch failed: {str(e)}")
        else:
            print(f"[ERROR] HTTP {response.status_code}")
    except Exception as e:
        print(f"[ERROR] API check failed: {str(e)}")

# Summary
print("\n" + "="*70)
print("SUMMARY: Recommended Alternatives")
print("="*70)

if successful_series:
    print(f"\nFound {len(successful_series)} suitable alternatives:\n")
    for i, series in enumerate(successful_series, 1):
        print(f"{i}. {series['series_id']} - {series['title']}")
        print(f"   Frequency: {series['frequency']}")
        print(f"   Latest: {series['latest_date']} = {series['latest_value']:.2f}")
        print(f"   Description: {series['description']}")
        print()
else:
    print("\n[WARNING] No suitable alternatives found!")
    print("Manual search required on FRED website.")

print("="*70)
