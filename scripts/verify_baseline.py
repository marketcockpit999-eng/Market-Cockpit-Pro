# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Baseline Verification Script
================================================================================
Pre-commit hook用の自動検証スクリプト

目的:
- indicators.pyで定義された指標が、対応するページファイルで参照されているか検証
- 指標が「静かに消える」ことを防止

使い方:
    python scripts/verify_baseline.py

終了コード:
    0: すべての指標が正常に参照されている
    1: 未参照の指標がある（commit失敗）

================================================================================
"""

import os
import re
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.indicators import INDICATORS, get_indicators_for_page


# =============================================================================
# CONFIGURATION
# =============================================================================

# Pages to check (must match ui_page values in indicators.py)
PAGES_TO_CHECK = [
    '01_liquidity',
    '02_global_money', 
    '03_us_economic',
    '04_crypto',
    '08_sentiment',
    '09_banking',
    # Note: 05, 06, 07, 11, 12, 13 are special pages (AI, Monte Carlo, etc.)
    # They don't use standard indicator display patterns
]

# Indicators that are displayed via special methods (not show_metric_with_sparkline)
# These are still checked for presence in the file, but with relaxed patterns
SPECIAL_DISPLAY_INDICATORS = {
    # Calculated indicators displayed via custom charts
    'Net_Liquidity': 'composite_chart',
    
    # API-based indicators (not in main df)
    'SP500_PE': 'api',
    'NASDAQ_PE': 'api',
    'BTC_Funding_Rate': 'api',
    'BTC_Open_Interest': 'api',
    'BTC_Long_Short_Ratio': 'api',
    'ETH_Funding_Rate': 'api',
    'ETH_Open_Interest': 'api',
    'Stablecoin_Total': 'api',
    'Treasury_TVL': 'api',
    'Gold_TVL': 'api',
    'Crypto_Fear_Greed': 'api',
    'CNN_Fear_Greed': 'api',
    
    # Web scraping indicators
    'Richmond_Fed_Mfg': 'web_scrape',
    'Richmond_Fed_Services': 'web_scrape',
}

# Indicators that are intentionally not displayed on UI
# (e.g., only used for calculations or AI analysis)
EXCLUDED_FROM_UI_CHECK = [
    'Global_Liquidity_Proxy',  # Lab page only (10_market_lab)
    'M2_Velocity',             # Lab page only (10_market_lab)
    'Financial_Stress',        # Lab page only (10_market_lab)
    'ECB_Assets',              # Used in calculations, displayed on 02 via composite
]


# =============================================================================
# VERIFICATION LOGIC
# =============================================================================

def get_page_file_path(page_name: str) -> str:
    """Get the file path for a page"""
    return os.path.join(PROJECT_ROOT, 'pages', f'{page_name}.py')


def read_page_content(page_name: str) -> str:
    """Read the content of a page file"""
    path = get_page_file_path(page_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Page file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def is_indicator_referenced(indicator_name: str, page_content: str) -> bool:
    """
    Check if an indicator is referenced in the page content.
    
    Detects patterns like:
    - show_metric_with_sparkline(..., 'INDICATOR', ...)
    - df.get('INDICATOR')
    - df_original.get('INDICATOR')
    - 'INDICATOR' as a string literal
    - df['INDICATOR']
    - record_api_status('INDICATOR', ...)
    """
    # Pattern 1: show_metric_with_sparkline with indicator name
    pattern1 = rf"show_metric_with_sparkline\([^)]*['\"]({re.escape(indicator_name)})['\"]"
    
    # Pattern 2: df.get('INDICATOR') or df_original.get('INDICATOR')
    pattern2 = rf"df(?:_original)?\.get\(['\"]({re.escape(indicator_name)})['\"]"
    
    # Pattern 3: df['INDICATOR']
    pattern3 = rf"df(?:_original)?\[['\"]({re.escape(indicator_name)})['\"]"
    
    # Pattern 4: record_api_status('INDICATOR', ...)
    pattern4 = rf"record_api_status\(['\"]({re.escape(indicator_name)})['\"]"
    
    # Pattern 5: General string reference (as a fallback)
    pattern5 = rf"['\"]({re.escape(indicator_name)})['\"]"
    
    # Check all patterns
    for pattern in [pattern1, pattern2, pattern3, pattern4, pattern5]:
        if re.search(pattern, page_content):
            return True
    
    return False


def verify_page(page_name: str) -> tuple[list, list]:
    """
    Verify all indicators for a specific page.
    
    Returns:
        tuple: (missing_indicators, found_indicators)
    """
    try:
        page_content = read_page_content(page_name)
    except FileNotFoundError as e:
        print(f"[Warning] {e}")
        return [], []
    
    indicators = get_indicators_for_page(page_name)
    missing = []
    found = []
    
    for indicator_name, indicator_info in indicators.items():
        # Skip excluded indicators
        if indicator_name in EXCLUDED_FROM_UI_CHECK:
            continue
        
        # Check if indicator is referenced
        if is_indicator_referenced(indicator_name, page_content):
            found.append(indicator_name)
        else:
            # Check if it's a special display indicator
            if indicator_name in SPECIAL_DISPLAY_INDICATORS:
                # Relaxed check - just needs to be mentioned somehow
                if indicator_name in page_content:
                    found.append(indicator_name)
                else:
                    missing.append((indicator_name, indicator_info))
            else:
                missing.append((indicator_name, indicator_info))
    
    return missing, found


def run_verification() -> int:
    """
    Run verification on all pages.
    
    Returns:
        int: Exit code (0 = success, 1 = failure)
    """
    print("=" * 60)
    print("Market Cockpit Pro - Baseline Verification")
    print("=" * 60)
    print()
    
    total_missing = []
    total_found = []
    
    for page_name in PAGES_TO_CHECK:
        print(f"[Checking] {page_name}.py...")
        missing, found = verify_page(page_name)
        
        if found:
            print(f"   [Success] Found: {len(found)} indicators")
        
        if missing:
            print(f"   [Error] Missing: {len(missing)} indicators")
            for name, info in missing:
                print(f"      - {name} ({info.get('notes', 'No description')})")
            total_missing.extend([(page_name, name, info) for name, info in missing])
        
        total_found.extend(found)
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"[Success] Verified: {len(total_found)} indicators")
    print(f"[Error] Missing:  {len(total_missing)} indicators")
    print()
    
    if total_missing:
        print("[Warning] MISSING INDICATORS:")
        print("-" * 40)
        for page_name, indicator_name, info in total_missing:
            print(f"  [{page_name}] {indicator_name}")
            print(f"      Notes: {info.get('notes', 'N/A')}")
            print(f"      Pattern: {info.get('display_pattern', 'standard')}")
        print()
        print("❌ VERIFICATION FAILED")
        print()
        print("To fix:")
        print("1. Ensure the indicator is displayed in the page file")
        print("2. Or add to EXCLUDED_FROM_UI_CHECK if intentionally hidden")
        print("3. Or update SPECIAL_DISPLAY_INDICATORS if using custom display")
        return 1
    else:
        print("[Success] ALL INDICATORS VERIFIED")
        return 0


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    exit_code = run_verification()
    sys.exit(exit_code)
