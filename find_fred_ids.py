import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

# Alternative FRED IDs to test
candidates = {
    # SOMA Bills candidates
    'WSHOBILL': 'Treasury Bills in SOMA (old)',
    'SWPT': 'Total System Open Market Account (SOMA)',
    'WSHOMCB': 'Mortgage-Backed Securities in SOMA',
    
    # Discount Window / Total Loans candidates  
    'WLC FL': 'Total Loans, All Commercial Banks',
    'TOTDISCBOR': 'Total Discount Window Borrowing',
    'H41RESPPALD': 'H.4.1 Release Discount Window',
}

end = datetime.datetime.now()
start = end - datetime.timedelta(days=90)

print("Testing alternative FRED IDs...")
print("=" * 60)

for fred_id, description in candidates.items():
    print(f"\n{fred_id}: {description}")
    try:
        data = web.DataReader(fred_id, 'fred', start, end, api_key=FRED_API_KEY)
        if len(data) > 0:
            print(f"  [OK] {len(data)} rows, Latest: {data.iloc[-1, 0]:.2f} on {data.index[-1].strftime('%Y-%m-%d')}")
        else:
            print("  [EMPTY] No data")
    except Exception as e:
        error_msg = str(e)[:60]
        print(f"  [FAIL] {error_msg}")
