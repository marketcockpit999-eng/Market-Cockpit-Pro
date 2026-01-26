# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.getcwd()))

try:
    from utils.auto_render import get_render_stats, INDICATORS
    from utils import get_indicators_for_page
    
    print("--- Auto Render Stats ---")
    stats = get_render_stats()
    print(f"Total Indicators: {stats['total']}")
    print(f"By Pattern: {stats['by_pattern']}")
    
    print("\n--- Page Breakdown ---")
    pages = ['01_liquidity', '03_us_economic', '09_banking']
    for page in pages:
        inds = get_indicators_for_page(page)
        print(f"{page}: {len(inds)} indicators")
        
    print("\n--- Pattern Check ---")
    # Verify some key indicators have the correct pattern
    checks = {
        'ON_RRP': 'standard',
        'CPI': 'mom_yoy',
        'NFP': 'manual_calc'
    }
    for key, expected in checks.items():
        pattern = INDICATORS.get(key, {}).get('display_pattern')
        print(f"{key}: pattern={pattern} (expected={expected})")
        assert pattern == expected
        
    print("\n[OK] Internal logic verification passed!")

except Exception as e:
    print(f"\n[ERROR] Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
