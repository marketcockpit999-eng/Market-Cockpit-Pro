import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"
end = datetime.datetime.now()
start = end - datetime.timedelta(days=30)

results = []
results.append("=== Testing FRED API for H.4.1 Data ===")
results.append("")

ids = {
    'WLCFLL': 'Total Loans',
    'WLCFLPCL': 'Primary Credit', 
    'WHTLSBL': 'SOMA Bills'
}

for fid, name in ids.items():
    try:
        data = web.DataReader(fid, 'fred', start, end, api_key=FRED_API_KEY)
        latest = data.iloc[-1, 0]
        date = data.index[-1].strftime('%Y-%m-%d')
        results.append(f"OK {name} ({fid}): {latest:,.0f} M -> {latest/1000:.2f} B ({date})")
    except Exception as e:
        results.append(f"FAIL {name} ({fid}): ERROR - {e}")

results.append("")
results.append("If all show OK, FRED API is working and manual input is not needed!")

# Write to file
with open('test_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

# Also print
for r in results:
    print(r)
