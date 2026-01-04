"""Test FRED API for failing indicators"""
import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"
end = datetime.datetime.now()
start = end - datetime.timedelta(days=365*2)

# Test indicators that showed N/A
test_ids = {
    'WHTLSBL': 'SOMA Bills',
    'DRTSCILM': 'Lending Standards (existing)',
    'DRSTDCL': 'CI Std Large',
    'DRSTSS': 'CI Std Small',
    'DRSDCL': 'CI Demand',
    'BUSLOANS': 'CI Loans',
    'SUBLPDRCSC': 'CRE Construction',
    'SUBLPDRNS': 'CRE Office',
    'SUBLPDRMF': 'CRE Multifamily',
    'DRSDRE': 'CRE Demand',
    'CREACBW027SBOG': 'CRE Loans',
}

results = []
for fred_id, name in test_ids.items():
    try:
        data = web.DataReader(fred_id, 'fred', start, end, api_key=FRED_API_KEY)
        if data.empty or data.iloc[-1, 0] is None:
            results.append(f"EMPTY {fred_id}: No data - {name}")
        else:
            latest = data.iloc[-1, 0]
            date = data.index[-1].strftime('%Y-%m-%d')
            results.append(f"OK    {fred_id}: {latest:,.1f} ({date}) - {name}")
    except Exception as e:
        results.append(f"ERROR {fred_id}: {str(e)[:60]} - {name}")

print("=== FRED API Test Results ===")
for r in results:
    print(r)
