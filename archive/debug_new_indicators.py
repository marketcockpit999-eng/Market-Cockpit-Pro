# -*- coding: utf-8 -*-
"""
Debug script for new indicators
Run: python debug_new_indicators.py
"""

import pandas_datareader.data as web
import yfinance as yf
import datetime
import os

# Test FRED indicators
FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

NEW_FRED = {
    'NFCI': 'NFCI',
    'Small_Bank_Deposits': 'DPSSCBW027SBOG',
    'CC_Delinquency': 'DRCCLACBS',
    'CP_Spread': 'CPFF',
    'Breakeven_10Y': 'T10YIE',
    'Credit_Card_Loans': 'CCLACBW027SBOG',
    'Consumer_Loans': 'CLSACBW027NBOG',
    'Bank_Securities': 'H8B1002NCBCAG',
    'Bank_Deposits': 'DPSACBW027SBOG',
}

NEW_YAHOO = {
    'MOVE': '^MOVE',
}

end = datetime.datetime.now()
start = end - datetime.timedelta(days=730)

print("=" * 60)
print("🔍 FRED INDICATORS TEST")
print("=" * 60)

for name, ticker in NEW_FRED.items():
    try:
        s = web.DataReader(ticker, 'fred', start, end, api_key=FRED_API_KEY)
        latest = s.iloc[-1].values[0]
        date = s.index[-1].strftime('%Y-%m-%d')
        print(f"✅ {name:25} = {latest:12.4f} ({date})")
    except Exception as e:
        print(f"❌ {name:25} = ERROR: {str(e)[:40]}")

print("\n" + "=" * 60)
print("🔍 YAHOO INDICATORS TEST")
print("=" * 60)

for name, ticker in NEW_YAHOO.items():
    try:
        data = yf.download(ticker, start=start, end=end, progress=False)['Close']
        latest = data.iloc[-1]
        date = data.index[-1].strftime('%Y-%m-%d')
        print(f"✅ {name:25} = {latest:12.4f} ({date})")
    except Exception as e:
        print(f"❌ {name:25} = ERROR: {str(e)[:40]}")

print("\n" + "=" * 60)
print("🔍 CACHE FILE CHECK")
print("=" * 60)

cache_file = os.path.join(os.path.dirname(__file__), '.market_data_cache.pkl')
if os.path.exists(cache_file):
    import time
    age = time.time() - os.path.getmtime(cache_file)
    print(f"⚠️  Cache file exists: {cache_file}")
    print(f"   Age: {age:.0f} seconds ({age/60:.1f} minutes)")
    print(f"   TTL: 600 seconds (10 minutes)")
    if age < 600:
        print(f"   ❗ Cache is ACTIVE - delete to force refresh!")
    else:
        print(f"   ✅ Cache is EXPIRED - will refresh on next request")
else:
    print("✅ No cache file - data will be fetched fresh")

print("\n💡 To force refresh, delete the cache file:")
print(f"   del \"{cache_file}\"")
