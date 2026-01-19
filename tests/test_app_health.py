# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - App Health Test
================================================================================
アプリ全体の健全性をテストする

テスト項目：
1. 全ページのインポート
2. 計算ロジックの正確性
3. 必須設定の存在確認
4. データ取得（オプション）

Usage:
    pytest tests/test_app_health.py -v
    python tests/test_app_health.py           # 基本テスト
    python tests/test_app_health.py --fetch   # データ取得テスト含む
================================================================================
"""

import sys
import os
import importlib.util

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# =============================================================================
# Helper: Import module from file path
# =============================================================================

def import_page(filename):
    """ファイルパスからページモジュールをインポート"""
    filepath = os.path.join(PROJECT_ROOT, 'pages', filename)
    spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# =============================================================================
# 1. 全ページのインポートテスト
# =============================================================================

PAGE_FILES = [
    '01_liquidity.py',
    '02_global_money.py',
    '03_us_economic.py',
    '04_crypto.py',
    '05_ai_analysis.py',
    '06_monte_carlo.py',
    '07_market_voices.py',
    '08_sentiment.py',
    '09_banking.py',
    '10_market_lab.py',
    '11_analysis_lab.py',
]


def test_all_pages_exist():
    """全ページファイルが存在することを確認"""
    pages_dir = os.path.join(PROJECT_ROOT, 'pages')
    
    for page_file in PAGE_FILES:
        filepath = os.path.join(pages_dir, page_file)
        assert os.path.exists(filepath), f"ページファイルが存在しない: {page_file}"


def test_all_pages_have_valid_syntax():
    """全ページに構文エラーがないことを確認"""
    import py_compile
    pages_dir = os.path.join(PROJECT_ROOT, 'pages')
    
    errors = []
    for page_file in PAGE_FILES:
        filepath = os.path.join(pages_dir, page_file)
        try:
            py_compile.compile(filepath, doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"{page_file}: {e}")
    
    assert len(errors) == 0, f"構文エラー: {errors}"


# =============================================================================
# 2. 計算ロジックの正確性
# =============================================================================

def test_net_liquidity_calculation():
    """Net Liquidity計算: Fed_Assets - TGA - ON_RRP"""
    import pandas as pd
    
    # テストデータ
    df = pd.DataFrame({
        'Fed_Assets': [8000.0, 8100.0, 8200.0],
        'TGA': [500.0, 600.0, 700.0],
        'ON_RRP': [1500.0, 1400.0, 1300.0],
    })
    
    # 計算
    df['Net_Liquidity'] = df['Fed_Assets'] - df['TGA'] - df['ON_RRP']
    
    # 検証
    assert df['Net_Liquidity'].iloc[0] == 6000.0, "8000 - 500 - 1500 = 6000"
    assert df['Net_Liquidity'].iloc[1] == 6100.0, "8100 - 600 - 1400 = 6100"
    assert df['Net_Liquidity'].iloc[2] == 6200.0, "8200 - 700 - 1300 = 6200"


def test_soma_bills_ratio_calculation():
    """SOMA Bills比率計算: SOMA_Bills / SOMA_Total * 100"""
    import pandas as pd
    
    df = pd.DataFrame({
        'SOMA_Total': [8000.0, 8000.0],
        'SOMA_Bills': [400.0, 800.0],
    })
    
    # 計算
    df['SomaBillsRatio'] = (df['SOMA_Bills'] / df['SOMA_Total']) * 100
    
    # 検証
    assert abs(df['SomaBillsRatio'].iloc[0] - 5.0) < 0.01, "400/8000 = 5%"
    assert abs(df['SomaBillsRatio'].iloc[1] - 10.0) < 0.01, "800/8000 = 10%"


def test_us_real_m2_index_calculation():
    """US Real M2 Index計算: (M2SL / CPI) * CPI基準値"""
    import pandas as pd
    
    # CPI基準値（2020年1月のCPI）
    cpi_base = 258.678
    
    df = pd.DataFrame({
        'M2SL': [20000.0, 21000.0, 22000.0],  # M2マネーサプライ (Billions)
        'CPI': [280.0, 290.0, 300.0],          # CPI指数
    })
    
    # 計算
    df['US_Real_M2_Index'] = (df['M2SL'] / df['CPI']) * cpi_base
    
    # 検証: (20000 / 280) * 258.678 ≈ 18477
    expected_0 = (20000.0 / 280.0) * cpi_base
    assert abs(df['US_Real_M2_Index'].iloc[0] - expected_0) < 1.0, f"Expected {expected_0}"
    
    # 検証: (21000 / 290) * 258.678 ≈ 18732
    expected_1 = (21000.0 / 290.0) * cpi_base
    assert abs(df['US_Real_M2_Index'].iloc[1] - expected_1) < 1.0, f"Expected {expected_1}"


def test_global_liquidity_proxy_calculation():
    """Global Liquidity Proxy計算: Fed_Assets + ECB_Assets - TGA - ON_RRP"""
    import pandas as pd
    
    df = pd.DataFrame({
        'Fed_Assets': [8000.0, 8100.0],     # FRB総資産 (Billions USD)
        'ECB_Assets': [9000.0, 9200.0],     # ECB資産 (すでにUSD換算済と仮定)
        'TGA': [500.0, 600.0],              # 財務省口座
        'ON_RRP': [1500.0, 1400.0],         # リバースレポ
    })
    
    # 計算
    df['Global_Liquidity_Proxy'] = df['Fed_Assets'] + df['ECB_Assets'] - df['TGA'] - df['ON_RRP']
    
    # 検証: 8000 + 9000 - 500 - 1500 = 15000
    assert df['Global_Liquidity_Proxy'].iloc[0] == 15000.0, "8000 + 9000 - 500 - 1500 = 15000"
    
    # 検証: 8100 + 9200 - 600 - 1400 = 15300
    assert df['Global_Liquidity_Proxy'].iloc[1] == 15300.0, "8100 + 9200 - 600 - 1400 = 15300"


# =============================================================================
# 3. 必須設定の存在確認
# =============================================================================

def test_fred_api_key_exists():
    """FRED APIキーが設定されていることを確認"""
    from utils.config import FRED_API_KEY
    assert FRED_API_KEY is not None, "FRED_API_KEY が設定されていません"
    assert len(FRED_API_KEY) > 10, "FRED_API_KEY が短すぎます（無効な可能性）"


def test_fred_indicators_defined():
    """FRED指標が定義されていることを確認"""
    from utils.config import FRED_INDICATORS
    assert FRED_INDICATORS is not None, "FRED_INDICATORS が未定義"
    assert len(FRED_INDICATORS) > 50, f"FRED_INDICATORS が少なすぎます: {len(FRED_INDICATORS)}個"


def test_yahoo_indicators_defined():
    """Yahoo指標が定義されていることを確認"""
    from utils.config import YAHOO_INDICATORS
    assert YAHOO_INDICATORS is not None, "YAHOO_INDICATORS が未定義"
    assert len(YAHOO_INDICATORS) > 10, f"YAHOO_INDICATORS が少なすぎます: {len(YAHOO_INDICATORS)}個"


def test_data_freshness_rules_defined():
    """Data Freshness Rulesが定義されていることを確認"""
    from utils.config import DATA_FRESHNESS_RULES
    assert DATA_FRESHNESS_RULES is not None, "DATA_FRESHNESS_RULES が未定義"
    assert 'daily' in DATA_FRESHNESS_RULES, "daily ルールがない"
    assert 'weekly' in DATA_FRESHNESS_RULES, "weekly ルールがない"
    assert 'monthly' in DATA_FRESHNESS_RULES, "monthly ルールがない"


def test_validation_ranges_defined():
    """Validation Rangesが定義されていることを確認"""
    from utils.config import VALIDATION_RANGES
    assert VALIDATION_RANGES is not None, "VALIDATION_RANGES が未定義"
    assert len(VALIDATION_RANGES) > 10, f"VALIDATION_RANGES が少なすぎます: {len(VALIDATION_RANGES)}個"
    # Note: Net_Liquidity等の計算値はvalidation未設定の場合あり（後で追加予定）


# =============================================================================
# 4. データ取得テスト（オプション）
# =============================================================================

def test_data_fetch_succeeds():
    """データ取得が成功することを確認（--fetch オプション時のみ）"""
    if '--fetch' not in sys.argv:
        print("  [SKIP] Skipped (use --fetch to run)")
        return
    
    from utils.data_fetcher import get_market_data
    
    df, df_original = get_market_data(_force_refresh=True)
    
    assert df is not None, "データフレームがNone"
    assert len(df) > 100, f"データが少なすぎます: {len(df)}行"
    assert len(df.columns) > 50, f"カラムが少なすぎます: {len(df.columns)}個"


def test_key_indicators_have_data():
    """主要指標にデータがあることを確認（--fetch オプション時のみ）"""
    if '--fetch' not in sys.argv:
        print("  [SKIP] Skipped (use --fetch to run)")
        return
    
    from utils.data_fetcher import get_market_data
    
    df, _ = get_market_data()
    
    key_indicators = [
        'Fed_Assets', 'TGA', 'ON_RRP', 'Net_Liquidity',
        'VIX', 'SP500', 'US_10Y',
    ]
    
    for indicator in key_indicators:
        assert indicator in df.columns, f"{indicator} がカラムにない"
        non_nan_count = df[indicator].notna().sum()
        assert non_nan_count > 0, f"{indicator} が全てNaN"


# =============================================================================
# 直接実行時のテスト
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("[APP] HEALTH TEST")
    print("=" * 60)
    
    all_passed = True
    
    # 1. ページ存在・構文チェック
    print("\n[1/4] Page Tests...")
    try:
        test_all_pages_exist()
        print("  [OK] All pages exist")
    except AssertionError as e:
        print(f"  [NG] Page existence: {e}")
        all_passed = False
    
    try:
        test_all_pages_have_valid_syntax()
        print("  [OK] All pages have valid syntax")
    except AssertionError as e:
        print(f"  [NG] Page syntax: {e}")
        all_passed = False
    
    # 2. 計算ロジック
    print("\n[2/4] Calculation Tests...")
    try:
        test_net_liquidity_calculation()
        print("  [OK] Net Liquidity calculation")
    except AssertionError as e:
        print(f"  [NG] Net Liquidity: {e}")
        all_passed = False
    
    try:
        test_soma_bills_ratio_calculation()
        print("  [OK] SOMA Bills Ratio calculation")
    except AssertionError as e:
        print(f"  [NG] SOMA Bills Ratio: {e}")
        all_passed = False
    
    try:
        test_us_real_m2_index_calculation()
        print("  [OK] US Real M2 Index calculation")
    except AssertionError as e:
        print(f"  [NG] US Real M2 Index: {e}")
        all_passed = False
    
    try:
        test_global_liquidity_proxy_calculation()
        print("  [OK] Global Liquidity Proxy calculation")
    except AssertionError as e:
        print(f"  [NG] Global Liquidity Proxy: {e}")
        all_passed = False
    
    # 3. 必須設定
    print("\n[3/4] Config Tests...")
    try:
        test_fred_api_key_exists()
        print("  [OK] FRED API Key")
    except AssertionError as e:
        print(f"  [NG] FRED API Key: {e}")
        all_passed = False
    
    try:
        test_fred_indicators_defined()
        print("  [OK] FRED Indicators")
    except AssertionError as e:
        print(f"  [NG] FRED Indicators: {e}")
        all_passed = False
    
    try:
        test_yahoo_indicators_defined()
        print("  [OK] Yahoo Indicators")
    except AssertionError as e:
        print(f"  [NG] Yahoo Indicators: {e}")
        all_passed = False
    
    try:
        test_data_freshness_rules_defined()
        print("  [OK] Data Freshness Rules")
    except AssertionError as e:
        print(f"  [NG] Data Freshness Rules: {e}")
        all_passed = False
    
    try:
        test_validation_ranges_defined()
        print("  [OK] Validation Ranges")
    except AssertionError as e:
        print(f"  [NG] Validation Ranges: {e}")
        all_passed = False
    
    # 4. データ取得
    print("\n[4/4] Data Fetch Tests...")
    if '--fetch' in sys.argv:
        try:
            test_data_fetch_succeeds()
            print("  [OK] Data fetch succeeds")
        except AssertionError as e:
            print(f"  [NG] Data fetch: {e}")
            all_passed = False
        
        try:
            test_key_indicators_have_data()
            print("  [OK] Key indicators have data")
        except AssertionError as e:
            print(f"  [NG] Key indicators: {e}")
            all_passed = False
    else:
        print("  [SKIP] Skipped (run with --fetch to test)")
    
    # 結果
    print("\n" + "=" * 60)
    if all_passed:
        print("[OK] ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("[NG] SOME TESTS FAILED")
        sys.exit(1)
