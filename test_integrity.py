import sys
import os
import pandas as pd

# Add parent directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import get_market_data, FRED_INDICATORS

print("--- Data Integrity Check ---")

# 1. Check Config Logic
required_original_keys = ['M2SL', 'Fed_Assets', 'SP500', 'VIX']
check_config = all(k in FRED_INDICATORS.keys() or k in ['SP500', 'VIX'] for k in required_original_keys)
print(f"Config Integrity: {'OK' if check_config else 'FAILED'}")

# 2. Check Data Fetching (Use cache if available)
print("Fetching/Loading Data...")
try:
    df, _ = get_market_data(_force_refresh=False)
except Exception as e:
    print(f"Error fetching data: {e}")
    sys.exit(1)

# 3. Verify Existing Columns (Regression Test)
critical_cols = ['M2SL', 'Fed_Assets', 'SP500', 'VIX', 'DXY', 'BTC']
missing = [c for c in critical_cols if c not in df.columns]

if not missing:
    print("OK: All critical existing columns found.")
else:
    print(f"FAIL: MISSING COLUMNS: {missing}")

# 4. Verify New Columns (New Feature Test)
new_cols = ['M2_Velocity', 'Financial_Stress', 'Global_Liquidity_Proxy']
missing_new = [c for c in new_cols if c not in df.columns]

if not missing_new:
    print("OK: All NEW columns found.")
else:
    print(f"WARN: Missing NEW columns: {missing_new}")

print(f"Total Columns: {len(df.columns)}")
