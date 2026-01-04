import pandas_datareader.data as web
import yfinance as yf
import datetime
import pandas as pd
import os

os.environ["FRED_API_KEY"] = "4e9f89c09658e42a4362d1251d9a3d05"

FRED_INDICATORS = {
    'ON_RRP': 'RRPONTSYD',         
    'Reserves': 'WRESBAL',         
    'TGA': 'WTREGEN',              
    'Fed_Assets': 'WALCL',         
    'SOMA_Bills': 'WSHOBL',        
    'SOMA_Total': 'WSHOSHO',       
    'Primary_Credit': 'WLCFLPCL',  
    'Total_Loans': 'WLCFLL',       
    'EFFR': 'EFFR',                
    'IORB': 'IORB',                
    'Credit_Spread': 'BAMLH0A0HYM2', 
    'Breakeven_10Y': 'T10YIE',       
    'US_TNX': 'DGS10',               
    'Unemployment': 'UNRATE',       
    'CPI': 'CPIAUCSL',              
}

end = datetime.datetime.now()
start = end - datetime.timedelta(days=30)

print(f"{'Indicator':<20} | {'Value':<15} | {'Date':<10}")
print("-" * 50)

for name, ticker in FRED_INDICATORS.items():
    try:
        s = web.DataReader(ticker, 'fred', start, end)
        valid = s.dropna()
        if not valid.empty:
            val = valid.iloc[-1].iloc[0]
            date = valid.index[-1].strftime("%Y-%m-%d")
            print(f"{name:<20} | {val:<15,.2f} | {date:<10}")
        else:
            print(f"{name:<20} | NO DATA        | N/A")
    except Exception as e:
        print(f"{name:<20} | ERROR: {str(e)[:15]} | N/A")
