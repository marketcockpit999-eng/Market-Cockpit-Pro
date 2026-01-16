#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Health Check Script
================================================================================
Quick validation of data integrity and indicator status.

Usage:
    python scripts/health_check.py              # Basic check
    python scripts/health_check.py --verbose    # Detailed output
    python scripts/health_check.py --fetch      # Force fresh data fetch
================================================================================
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix for UnicodeEncodeError in Windows terminals
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description='Market Cockpit Pro Health Check')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--fetch', '-f', action='store_true', help='Force fresh data fetch')
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 MARKET COCKPIT PRO - HEALTH CHECK")
    print("=" * 60)
    
    # ==========================================================================
    # Step 1: Check imports
    # ==========================================================================
    print("\n📦 Step 1: Checking imports...")
    
    try:
        from utils.indicators import (
            INDICATORS,
            get_fred_indicators,
            get_yahoo_indicators,
            get_freshness_rules,
        )
        print("  ✅ utils.indicators loaded")
    except ImportError as e:
        print(f"  ❌ utils.indicators FAILED: {e}")
        return 1
    
    try:
        from utils.config import (
            FRED_INDICATORS,
            YAHOO_INDICATORS,
            DATA_FRESHNESS_RULES,
            FRED_API_KEY,
        )
        print("  ✅ utils.config loaded")
    except ImportError as e:
        print(f"  ❌ utils.config FAILED: {e}")
        return 1
    
    try:
        from utils.data_fetcher import get_market_data
        print("  ✅ utils.data_fetcher loaded")
    except ImportError as e:
        print(f"  ❌ utils.data_fetcher FAILED: {e}")
        return 1
    
    # ==========================================================================
    # Step 2: Check indicator registry
    # ==========================================================================
    print("\n📊 Step 2: Indicator Registry...")
    
    total_indicators = len(INDICATORS)
    fred_count = len(get_fred_indicators())
    yahoo_count = len(get_yahoo_indicators())
    
    print(f"  Total indicators: {total_indicators}")
    print(f"  FRED indicators:  {fred_count}")
    print(f"  Yahoo indicators: {yahoo_count}")
    
    # Verify FRED_INDICATORS matches
    if FRED_INDICATORS == get_fred_indicators():
        print("  ✅ FRED_INDICATORS matches indicator registry")
    else:
        print("  ⚠️  FRED_INDICATORS mismatch!")
        print(f"     Config: {len(FRED_INDICATORS)}, Registry: {fred_count}")
    
    # Verify YAHOO_INDICATORS matches  
    if YAHOO_INDICATORS == get_yahoo_indicators():
        print("  ✅ YAHOO_INDICATORS matches indicator registry")
    else:
        print("  ⚠️  YAHOO_INDICATORS mismatch!")
    
    # Check freshness rules
    rules = get_freshness_rules()
    total_in_rules = sum(len(r['indicators']) for r in rules.values())
    print(f"  Freshness rules: {total_in_rules} indicators tracked")
    
    if args.verbose:
        for period, rule in rules.items():
            print(f"    {period}: {len(rule['indicators'])} indicators")
    
    # ==========================================================================
    # Step 3: Check cache
    # ==========================================================================
    print("\n💾 Step 3: Cache Status...")
    
    cache_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '.market_data_cache.pkl'
    )
    
    if os.path.exists(cache_file):
        import time
        age = time.time() - os.path.getmtime(cache_file)
        size = os.path.getsize(cache_file) / 1024  # KB
        print(f"  Cache file: {cache_file}")
        print(f"  Age: {age:.0f} seconds ({age/60:.1f} minutes)")
        print(f"  Size: {size:.1f} KB")
        if age < 600:
            print(f"  ⚠️  Cache is ACTIVE (TTL: 10 min)")
        else:
            print(f"  ✅ Cache is EXPIRED")
    else:
        print("  ✅ No cache file")
    
    # ==========================================================================
    # Step 4: Data fetch test (optional)
    # ==========================================================================
    if args.fetch:
        print("\n📡 Step 4: Fetching data...")
        
        # Delete cache first
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print("  Deleted cache file")
        
        try:
            df, df_original = get_market_data(_force_refresh=True)
            print(f"  ✅ Data fetched successfully")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Date range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"  ❌ Data fetch FAILED: {e}")
            return 1
        
        # Check each indicator
        print("\n📋 Indicator Status:")
        
        missing = []
        all_nan = []
        ok = []
        
        all_indicators = list(INDICATORS.keys())
        
        for name in all_indicators:
            if name not in df.columns:
                missing.append(name)
                status = "❌ MISSING"
            elif df[name].isna().all():
                all_nan.append(name)
                status = "⚠️  ALL NaN"
            else:
                ok.append(name)
                latest = df[name].dropna().iloc[-1]
                date = df[name].dropna().index[-1].strftime('%Y-%m-%d')
                status = f"✅ {latest:.2f} ({date})"
            
            if args.verbose or name in missing or name in all_nan:
                print(f"  {name:25} {status}")
        
        # Summary
        print("\n📈 Summary:")
        print(f"  ✅ OK:      {len(ok)}")
        print(f"  ⚠️  NaN:    {len(all_nan)}")
        print(f"  ❌ Missing: {len(missing)}")
        
        if missing:
            print(f"\n⚠️  Missing indicators: {missing}")
        if all_nan:
            print(f"\n⚠️  All-NaN indicators: {all_nan}")
    else:
        print("\n💡 Tip: Run with --fetch to test data retrieval")
    
    # ==========================================================================
    # Final result
    # ==========================================================================
    print("\n" + "=" * 60)
    print("✅ HEALTH CHECK COMPLETE")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
