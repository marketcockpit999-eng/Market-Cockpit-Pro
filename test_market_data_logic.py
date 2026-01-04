import pandas as pd
import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

def get_market_data_debug():
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=730)
    
    # FRED Indicators
    FRED_INDICATORS = {
        'M2SL': 'M2SL',
        'CPI': 'CPIAUCSL',
    }
    
    fred_series = []
    for name, ticker in FRED_INDICATORS.items():
        try:
            s = web.DataReader(ticker, 'fred', start, end, api_key=FRED_API_KEY)
            s.columns = [name]
            fred_series.append(s)
            print(f"[OK] Fetched {name}: {len(s)} rows")
        except Exception as e:
            print(f"[FAIL] Failed {name}: {e}")
    
    # Join All
    df = pd.concat(fred_series, axis=1).sort_index()
    
    print("\n=== Before Unit Conversion ===")
    print(df[['M2SL', 'CPI']].tail(3))
    
    # Unit Normalization (Million to Billion)
    mil_to_bil = ['M2SL']
    for col in mil_to_bil:
        if col in df.columns:
            df[col] = df[col] / 1000
            print(f"\n[OK] Converted {col} to Billions")
    
    print("\n=== After Unit Conversion ===")
    print(df[['M2SL', 'CPI']].tail(3))
    
    # Calculate Real M2 (M2 adjusted for CPI)
    if all(c in df.columns for c in ['M2SL', 'CPI']):
        # Normalize CPI to base 100 at earliest date
        cpi_base = df['CPI'].iloc[0] if not pd.isna(df['CPI'].iloc[0]) else 1
        print(f"\n[OK] CPI Base: {cpi_base}")
        df['US_Real_M2_Index'] = (df['M2SL'] / df['CPI']) * cpi_base
        print("[OK] Calculated US_Real_M2_Index")
    
    print("\n=== After Real M2 Calculation ===")
    print(df[['M2SL', 'CPI', 'US_Real_M2_Index']].tail(3))
    
    # Forward fill
    df = df.ffill()
    
    print("\n=== After Forward Fill ===")
    print(df[['M2SL', 'CPI', 'US_Real_M2_Index']].tail(3))
    
    print("\n=== Final Values ===")
    print(f"M2SL (Nominal): {df['M2SL'].iloc[-1]:.4f} B")
    print(f"US_Real_M2_Index: {df['US_Real_M2_Index'].iloc[-1]:.4f} B")
    
    return df

if __name__ == "__main__":
    print("=== Testing get_market_data() Logic ===\n")
    df = get_market_data_debug()
