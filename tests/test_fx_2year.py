import yfinance as yf
import datetime
import pandas as pd

YAHOO_INDICATORS = {
    'DXY': 'DX-Y.NYB',
    'USDJPY': 'JPY=X',
    'EURUSD': 'EURUSD=X',
    'USDCNY': 'CNY=X',
}

# Use 2-year range like the app
end = datetime.datetime.now()
start = end - datetime.timedelta(days=730)

y_tickers = list(YAHOO_INDICATORS.values())
print(f"Downloading 2 years of FX data...")

y_data = yf.download(y_tickers, start=start, end=end, progress=False)['Close']

inv_yahoo = {v: k for k, v in YAHOO_INDICATORS.items()}
y_data = y_data.rename(columns=inv_yahoo)

print(f"Total rows: {len(y_data)}")
print(f"\nFirst 3 rows:\n{y_data.head(3)}")
print(f"\nLast 3 rows:\n{y_data.tail(3)}")

# Check for variation over 2 years
print("\n=== 2-YEAR VARIATION ===")
for col in y_data.columns:
    data = y_data[col].dropna()
    if len(data) > 0:
        min_val = data.min()
        max_val = data.max()
        variation = max_val - min_val
        pct_variation = (variation / min_val) * 100
        print(f"{col}: min={min_val:.2f}, max={max_val:.2f}, variation={variation:.2f} ({pct_variation:.1f}%)")
