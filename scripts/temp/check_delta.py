# Check if delta=0 is due to forward-fill
import sys
sys.path.insert(0, '.')
from utils.data_fetcher import get_market_data

print("=" * 60)
print("Delta Calculation Audit - Checking Last Values")
print("=" * 60)

df, df_original = get_market_data()

# Check key series
key_cols = ['ON_RRP', 'TGA', 'Fed_Assets', 'Net_Liquidity', 'Reserves', 'SRF']

for col in key_cols:
    if col in df.columns:
        series = df[col].dropna()
        if len(series) >= 3:
            last_3 = series.tail(3).tolist()
            delta = last_3[-1] - last_3[-2]
            print(f"\n{col}:")
            print(f"  Last 3 values: {[f'{v:.2f}' for v in last_3]}")
            print(f"  Delta (last - prev): {delta:.2f}")
            if abs(delta) < 0.01:
                print(f"  >>> ISSUE: Delta is near-zero!")
        else:
            print(f"\n{col}: Insufficient data ({len(series)} points)")
    else:
        print(f"\n{col}: Column not found")

print("\n" + "=" * 60)
print("Checking df_original (before forward-fill)")
print("=" * 60)

for col in key_cols:
    if col in df_original.columns:
        series = df_original[col].dropna()
        if len(series) >= 3:
            last_3 = series.tail(3).tolist()
            delta = last_3[-1] - last_3[-2]
            print(f"\n{col}:")
            print(f"  Last 3 values: {[f'{v:.2f}' for v in last_3]}")
            print(f"  Delta (last - prev): {delta:.2f}")
