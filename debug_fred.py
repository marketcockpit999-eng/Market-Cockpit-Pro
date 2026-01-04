import pandas_datareader.data as web
import datetime
import pandas as pd
import os

os.environ["FRED_API_KEY"] = "4e9f89c09658e42a4362d1251d9a3d05"
end = datetime.datetime.now()
start = end - datetime.timedelta(days=730)

tickers = {
    'SOMA_Bills': 'WHTLSBL',
    'SRF': 'WLCFSRF',
    'FIMA': 'WLCFFMRA',
    'Total_Loans': 'H41RESPALDKNWW',
    'Reserves': 'WRESBAL',
    'SOMA_Total': 'WSHOSHO'
}

print("--- FRED Data Debug ---")
for name, ticker in tickers.items():
    try:
        s = web.DataReader(ticker, 'fred', start, end)
        if s.empty:
            print(f"{name} ({ticker}): EMPTY")
        else:
            print(f"{name} ({ticker}): {len(s)} rows, Latest: {s.iloc[-1].values[0]} ({s.index[-1]})")
    except Exception as e:
        print(f"{name} ({ticker}): ERROR: {str(e)[:100]}")
