import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

# Possible H.4.1 related IDs
candidates = {
    # SOMA / Treasury Bills candidates
    'WS HOBILL': 'Weekly: SOMA Holdings Bills',
    'WSHOBN': 'Weekly: SOMA Holdings Notes',
    'SOMA': 'System Open Market Account',
    'TREAST': 'Treasury Securities',
    
    # Discount Window / Loans candidates
    'DISCBORR': 'Discount Window Borrowing',
    'H41RESPAL': 'H.4.1 All Loans',
    'RESPPALLN': 'Reserve Bank Loans',
}

end = datetime.datetime.now()
start = end - datetime.timedelta(days=90)

print("Testing H.4.1 related candidates...")
print("=" * 60)

for fred_id, description in candidates.items():
    print(f"\n{fred_id}: {description}")
    try:
        data = web.DataReader(fred_id, 'fred', start, end, api_key=FRED_API_KEY)
        if len(data) > 0:
            print(f"  [OK] {len(data)} rows, Latest: {data.iloc[-1, 0]:.2f}")
        else:
            print("  [EMPTY]")
    except Exception as e:
        err = str(e)[:50]
        print(f"  [FAIL] {err}")
