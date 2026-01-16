import pandas_datareader.data as web
import datetime
import os

os.environ["FRED_API_KEY"] = "4e9f89c09658e42a4362d1251d9a3d05"
end = datetime.datetime.now()
start = end - datetime.timedelta(days=30)

tickers = {
    'SRF': 'WORAL',
    'FIMA': 'H41RESPPALGTRFNWW',
    'Total_Loans': 'H41RESPALDKNWW'
}

print("--- Raw FRED Data (Last 30 Days) ---")
for name, ticker in tickers.items():
    try:
        s = web.DataReader(ticker, 'fred', start, end)
        if s.empty:
            print(f"{name} ({ticker}): EMPTY")
        else:
            last_val = s.iloc[-1].values[0]
            print(f"{name} ({ticker}): RAW={last_val} (Date: {s.index[-1]})")
    except Exception as e:
        print(f"{name} ({ticker}): ERROR: {str(e)}")
