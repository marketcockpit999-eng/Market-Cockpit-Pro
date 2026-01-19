
import pandas_datareader.data as web
import datetime
import os

# Check if we can get FRED API Key from environment or utils
try:
    from utils.config import FRED_API_KEY
except:
    FRED_API_KEY = os.environ.get('FRED_API_KEY')

print(f"API Key present: {bool(FRED_API_KEY)}")

series_ids = ['ECBASSETSW', 'M2V', 'STLFSI4']
start = datetime.datetime(2025, 1, 1)

for sid in series_ids:
    try:
        df = web.DataReader(sid, 'fred', start, api_key=FRED_API_KEY)
        print(f"✅ {sid}: Fetched {len(df)} rows. Last: {df.iloc[-1].values[0]}")
    except Exception as e:
        print(f"❌ {sid}: Failed. Error: {e}")
