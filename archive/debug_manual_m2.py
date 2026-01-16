
import streamlit as st
import pandas as pd
import sys
import os

# Mock streamlit.secrets/session_state if needed, though get_market_data doesn't use secrets directly for keys (it uses config)
# But it uses st.cache_data. We can bypass or let it run (it might form warnings).

# Add current dir to path
sys.path.append(os.getcwd())

from utils.data_fetcher import get_market_data
from utils.config import MANUAL_GLOBAL_M2, FRED_INDICATORS

def check_structure():
    print("Checking MANUAL_GLOBAL_M2 config...")
    print(MANUAL_GLOBAL_M2)

    print("\nFetching market data...")
    # Force refresh to verify injection
    df, df_original = get_market_data(_force_refresh=True)
    
    print("\nVerifying specific columns:")
    check_cols = ['CN_M2', 'JP_M2', 'EU_M2', 'CN_CPI', 'JP_CPI', 'EU_CPI']
    
    for col in check_cols:
        if col in df.columns:
            valid = df[col].dropna()
            if len(valid) > 0:
                last_date = valid.index[-1]
                val = valid.iloc[-1]
                print(f"✅ {col}: Found. Last date: {last_date}, Value: {val}")
            else:
                print(f"❌ {col}: Column exists but NO valid data (All NaNs).")
        else:
            print(f"❌ {col}: Column MISSING from dataframe.")

    # Check last_valid_dates attribute
    lvd = df.attrs.get('last_valid_dates', {})
    print(f"\nFreshness Item Count in attrs: {len(lvd)}")
    
    # Check if our suspects are in lvd
    missing_in_lvd = [c for c in check_cols if c not in lvd]
    if missing_in_lvd:
        print(f"⚠️ Missing from last_valid_dates attrs: {missing_in_lvd}")
    else:
        print("✅ All check columns are present in last_valid_dates.")

if __name__ == "__main__":
    check_structure()
