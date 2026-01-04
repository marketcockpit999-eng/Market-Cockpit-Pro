import yfinance as yf
import datetime
import pandas as pd

YAHOO_INDICATORS = {
    'SP500': '^GSPC',
    'VIX': '^VIX',
    'HYG': 'HYG',
    'DXY': 'DX-Y.NYB',
    'USDJPY': 'JPY=X',
    'EURUSD': 'EURUSD=X',
    'USDCNY': 'CNY=X',
}

end = datetime.datetime.now()
start = end - datetime.timedelta(days=30)

y_tickers = list(YAHOO_INDICATORS.values())
print(f"Downloading: {y_tickers}")

y_data = yf.download(y_tickers, start=start, end=end, progress=False)['Close']
print(f"\nOriginal columns: {list(y_data.columns)}")

inv_yahoo = {v: k for k, v in YAHOO_INDICATORS.items()}
y_data = y_data.rename(columns=inv_yahoo)
print(f"Renamed columns: {list(y_data.columns)}")

print(f"\nLast 5 rows:\n{y_data.tail()}")

# Check for variation
for col in y_data.columns:
    data = y_data[col].dropna()
    if len(data) > 0:
        min_val = data.min()
        max_val = data.max()
        variation = max_val - min_val
        print(f"\n{col}: min={min_val:.2f}, max={max_val:.2f}, variation={variation:.2f}")
