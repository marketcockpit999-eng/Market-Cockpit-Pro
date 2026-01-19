# -*- coding: utf-8 -*-
"""
Diagnostic script: Identify freshness count discrepancy
Problem: UI shows (59+1+10=70) but rules define 66
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from utils.config import DATA_FRESHNESS_RULES

# 1. Extract items from DATA_FRESHNESS_RULES
defined_items = set()
for category, config in DATA_FRESHNESS_RULES.items():
    for indicator in config['indicators']:
        defined_items.add(indicator)

print("=" * 60)
print(f"DATA_FRESHNESS_RULES defined: {len(defined_items)} items")
print("=" * 60)

# 2. Compare with actual DataFrame columns
print("\nLoading actual DataFrame...")
try:
    from utils.data import get_market_data
    df, df_original = get_market_data()
    
    last_valid_dates = df.attrs.get('last_valid_dates', {})
    monitored_columns = set(last_valid_dates.keys())
    
    # Remove known exceptions
    monitored_columns.discard('RMP_Alert_Active')
    monitored_columns.discard('RMP_Status_Text')
    
    print(f"DataFrame columns: {len(df.columns)}")
    print(f"last_valid_dates keys (after exclusions): {len(monitored_columns)}")
    
    # Diff analysis
    extra_in_df = monitored_columns - defined_items
    missing_from_df = defined_items - monitored_columns
    
    print("\n" + "=" * 60)
    print("EXTRA items (in DataFrame but NOT in DATA_FRESHNESS_RULES):")
    print("=" * 60)
    for item in sorted(extra_in_df):
        print(f"  + {item}")
    
    print("\n" + "=" * 60)
    print("MISSING items (in DATA_FRESHNESS_RULES but NOT in DataFrame):")
    print("=" * 60)
    for item in sorted(missing_from_df):
        print(f"  - {item}")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Defined in rules: {len(defined_items)}")
    print(f"  Actually monitored: {len(monitored_columns)}")
    print(f"  Extra (need to add to rules or exclude): {len(extra_in_df)}")
    print(f"  Missing (data not available): {len(missing_from_df)}")
    print("=" * 60)
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
