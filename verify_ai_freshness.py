import sys
import os
import pandas as pd

# Add parent directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils import DATA_FRESHNESS_RULES, get_indicators_for_ai
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

print("--- AI & Freshness Verification ---")

# 1. Check Freshness Rules Integrity
weekly_rules = DATA_FRESHNESS_RULES.get('weekly')
print(f"Weekly Rules Exists: {weekly_rules is not None}")
if weekly_rules:
    indicators = weekly_rules.get('indicators', [])
    print(f"Weekly Indicators Count: {len(indicators)}")
    print(f"Loaded Indicators: {indicators}")
    
    # Check for items that were potentially overwritten
    critical_checks = ['Financial_Stress', 'Reserves', 'SomaBillsRatio', 'Credit_Card_Loans']
    
    missing = [i for i in critical_checks if i not in indicators]
    
    if not missing:
        print("OK: Freshness Check: All merged indicators present.")
    else:
        print(f"FAIL: Freshness Check: MISSING MERGED ITEMS: {missing}")

# 2. Check AI Indicators
ai_inds = get_indicators_for_ai()
print(f"\nAI Indicators Count: {len(ai_inds)}")

new_features = ['M2_Velocity', 'Financial_Stress', 'ECB_Assets', 'USD_EUR', 'Global_Liquidity_Proxy']

found_count = 0
for f in new_features:
    if f in ai_inds:
        print(f"OK: AI Monitored: {f}")
        found_count += 1
    else:
        print(f"WARN: Not explicitly in Freshness Rules (Calculated?): {f}")

print("--- Done ---")
