#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Display Checker
====================
Validates that all indicators have required display elements.

Based on DISPLAY_SPEC.md (the "book" = source of truth)

Usage:
    python scripts/test_display_checker.py
    python scripts/test_display_checker.py --verbose
    python scripts/test_display_checker.py --real-data
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.indicators import INDICATORS
from utils.display_checker import (
    DisplayChecker, 
    run_display_check,
    run_static_check,
    get_failed_indicators,
    get_indicators_needing_attention,
    PATTERN_SPECS,
    MANUAL_CALC_SPECS,
    CALCULATED_SPECS,
)


def test_structure():
    """Test checker structure without actual data"""
    print("=" * 70)
    print("TEST: Display Checker Structure")
    print("=" * 70)
    
    # Check patterns are defined for all indicators
    patterns_used = set()
    missing_pattern = []
    
    for name, config in INDICATORS.items():
        pattern = config.get('display_pattern')
        if pattern is None:
            missing_pattern.append(name)
        else:
            patterns_used.add(pattern)
    
    print(f"\nPatterns used: {sorted(patterns_used)}")
    print(f"Patterns defined: {sorted(PATTERN_SPECS.keys())}")
    
    if missing_pattern:
        print(f"\n[FAIL] Missing display_pattern: {missing_pattern}")
        return False
    else:
        print("\n[OK] All indicators have display_pattern")
    
    # Check all used patterns are defined
    undefined = patterns_used - set(PATTERN_SPECS.keys())
    if undefined:
        print(f"[FAIL] Undefined patterns: {undefined}")
        return False
    else:
        print("[OK] All used patterns are defined")
    
    # Count by pattern
    print("\n--- Indicator Count by Pattern ---")
    pattern_counts = {}
    for name, config in INDICATORS.items():
        pattern = config.get('display_pattern', 'unknown')
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    total = 0
    for pattern, count in sorted(pattern_counts.items()):
        print(f"  {pattern}: {count}")
        total += count
    print(f"  ---")
    print(f"  TOTAL: {total}")
    
    # Check manual_calc specs
    print("\n--- Manual Calc Coverage ---")
    manual_calc_indicators = [name for name, config in INDICATORS.items() 
                              if config.get('display_pattern') == 'manual_calc']
    
    all_covered = True
    for name in manual_calc_indicators:
        if name in MANUAL_CALC_SPECS:
            print(f"  [OK] {name}: {MANUAL_CALC_SPECS[name]['check_type']}")
        else:
            print(f"  [FAIL] {name}: No spec defined!")
            all_covered = False
    
    # Check calculated specs
    print("\n--- Calculated Indicator Coverage ---")
    calculated_indicators = [name for name, config in INDICATORS.items() 
                             if config.get('display_pattern') == 'calculated']
    
    for name in calculated_indicators:
        if name in CALCULATED_SPECS:
            print(f"  [OK] {name}: {CALCULATED_SPECS[name]['formula']}")
        else:
            print(f"  [FAIL] {name}: No spec defined!")
            all_covered = False
    
    return all_covered


def test_static_check():
    """Test static check (label, help_text, notes)"""
    print("\n" + "=" * 70)
    print("TEST: Static Check (no data required)")
    print("=" * 70)
    
    checker = DisplayChecker()
    checker.check_all()
    
    # Don't print full report here, just summary
    summary = checker.get_summary()
    
    print(f"\nTotal: {summary['total']}")
    print(f"Passed: {summary['passed']} ({summary['pass_rate']})")
    print(f"Failed: {summary['failed']}")
    print(f"Warnings: {summary['warnings']}")
    
    # Show pattern breakdown
    print("\n--- By Pattern ---")
    for pattern, stats in summary['by_pattern'].items():
        status = '[OK]' if stats['failed'] == 0 else '[FAIL]'
        print(f"  {status} {pattern}: {stats['passed']}/{stats['total']}")
    
    # Show missing help texts
    missing_help = checker.get_missing_help_texts()
    if missing_help:
        print(f"\n[WARN] Missing Help Texts ({len(missing_help)} items):")
        for name in missing_help[:5]:
            print(f"   - help_{name}")
        if len(missing_help) > 5:
            print(f"   ... and {len(missing_help) - 5} more")
    
    # Show missing notes  
    missing_notes = checker.get_missing_notes()
    if missing_notes:
        print(f"\n[NOTE] Missing Notes ({len(missing_notes)} items):")
        for name in missing_notes[:5]:
            print(f"   - {name}")
        if len(missing_notes) > 5:
            print(f"   ... and {len(missing_notes) - 5} more")
    
    return summary['failed'] == 0


def test_with_mock_data():
    """Test checker with mock data"""
    import pandas as pd
    import numpy as np
    from datetime import datetime
    
    print("\n" + "=" * 70)
    print("TEST: Display Checker with Mock Data")
    print("=" * 70)
    
    # Create mock DataFrame with enough data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    
    # Add columns for common indicators
    df = pd.DataFrame(index=dates)
    df['ON_RRP'] = np.random.uniform(50, 100, len(dates))
    df['Reserves'] = np.random.uniform(3000, 4000, len(dates))
    df['TGA'] = np.random.uniform(400, 800, len(dates))
    df['Fed_Assets'] = np.random.uniform(7000, 8000, len(dates))
    df['ECB_Assets'] = np.random.uniform(6000, 7000, len(dates))
    
    # Add mom_yoy indicators
    df['CPI'] = np.random.uniform(300, 320, len(dates))
    
    # Add manual_calc indicators
    df['NFP'] = np.cumsum(np.random.uniform(-50, 150, len(dates))) + 150000
    df['UNRATE'] = np.random.uniform(3.5, 4.5, len(dates))
    
    # Create df_original
    df_original = {col: df[col].copy() for col in df.columns}
    
    # Run checker
    checker = DisplayChecker(df, df_original)
    checker.check_all()
    
    summary = checker.get_summary()
    print(f"\nTotal: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Note: Mock data has only {len(df.columns)} columns")
    
    return True


def test_with_real_data():
    """Test checker with real cached data (if available)"""
    import pickle
    
    print("\n" + "=" * 70)
    print("TEST: Display Checker with Real Data")
    print("=" * 70)
    
    cache_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '.market_data_cache.pkl'
    )
    
    if not os.path.exists(cache_path):
        print("[WARN] [SKIP] No cache file found.")
        print(f"   Expected: {cache_path}")
        return True
    
    try:
        with open(cache_path, 'rb') as f:
            cache = pickle.load(f)
        
        df = cache.get('df')
        df_original = cache.get('df_original', {})
        
        if df is None:
            print("[WARN] [SKIP] Cache exists but no DataFrame found")
            return True
        
        print(f"Loaded cache with {len(df.columns)} columns")
        
        # Run checker with full report
        checker = run_display_check(df, df_original, verbose=False)
        
        # Get failed indicators
        failed = get_failed_indicators(checker)
        if failed:
            print(f"\n[FAIL] {len(failed)} indicators failed mandatory checks")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error loading cache: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Test Display Checker')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--real-data', '-r', action='store_true', help='Test with real cached data')
    args = parser.parse_args()
    
    print("=" * 70)
    print("Display Checker Test Suite")
    print("Based on DISPLAY_SPEC.md (the 'book')")
    print("=" * 70)
    
    all_passed = True
    
    # Test 1: Structure
    if not test_structure():
        all_passed = False
    
    # Test 2: Static check
    if not test_static_check():
        all_passed = False
    
    # Test 3: Mock data
    if not test_with_mock_data():
        all_passed = False
    
    # Test 4: Real data (optional)
    if args.real_data:
        if not test_with_real_data():
            all_passed = False
    
    # Final summary
    print("\n" + "=" * 70)
    if all_passed:
        print("[OK] All tests passed!")
    else:
        print("[FAIL] Some tests failed!")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
