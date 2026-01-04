"""Test all 9 SLOOS FRED IDs"""
import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"
end = datetime.datetime.now()
start = end - datetime.timedelta(days=365)

# SLOOS Indicators
sloos_ids = {
    # C&I Lending
    'DRTSCILM': 'C&I Standards (Existing, Large/Medium) - ALREADY HAVE',
    'DRSTDCL': 'C&I Standards (Large/Medium)',
    'DRSTSS': 'C&I Standards (Small)',
    'DRSDCL': 'C&I Demand (Large/Medium)',
    'BUSLOANS': 'C&I Loan Balance (Total)',
    
    # CRE Lending
    'SUBLPDRCSC': 'CRE Standards (Construction)',
    'SUBLPDRNS': 'CRE Standards (Nonfarm Nonres)',
    'SUBLPDRMF': 'CRE Standards (Multifamily)',
    'DRSDRE': 'CRE Demand',
    'CREACBW027SBOG': 'CRE Loan Balance (Weekly)',
}

results = []
for fid, name in sloos_ids.items():
    try:
        data = web.DataReader(fid, 'fred', start, end, api_key=FRED_API_KEY)
        latest = data.iloc[-1, 0]
        date = data.index[-1].strftime('%Y-%m-%d')
        results.append(f"OK  {fid}: {latest:,.1f} ({date}) - {name}")
    except Exception as e:
        results.append(f"ERR {fid}: {str(e)[:50]} - {name}")

# Write to file
with open('sloos_test_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

for r in results:
    print(r)
