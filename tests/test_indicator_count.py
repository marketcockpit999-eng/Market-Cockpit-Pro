# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Indicator Count Test (API必要)
====================================================
実データを使用した指標数検証テスト

⚠️ 注意: このテストはAPI呼び出しを行います
    オフラインテストには validate_structure.py か test_calculations.py を使用

使い方:
    python -m pytest tests/test_indicator_count.py -v
    または
    python tests/test_indicator_count.py
"""

import sys
import os

# Add parent directory to path for both direct execution and pytest
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_TEST_DIR)
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, _TEST_DIR)

from specs.expected_indicators import (
    EXPECTED_INDICATOR_COUNT,
    REQUIRED_DATAFRAME_COLUMNS,
    CALCULATION_RULES,
)


def test_dataframe_has_required_columns():
    """データフレームに必須列が存在することを確認 (API必要)"""
    from utils.data import get_market_data
    
    print("\n⚠️  API呼び出し中... (キャッシュがあれば即座に完了)")
    df, _ = get_market_data(_force_refresh=False)
    
    missing_columns = []
    for col in REQUIRED_DATAFRAME_COLUMNS:
        if col not in df.columns:
            missing_columns.append(col)
    
    if missing_columns:
        print(f"\n❌ 欠損している列: {missing_columns}")
        assert False, f"必須列が欠損: {missing_columns}"
    else:
        print(f"\n✅ 全必須列が存在 ({len(REQUIRED_DATAFRAME_COLUMNS)}個)")


def test_indicator_count():
    """指標数が期待値と一致することを確認 (API必要)"""
    from utils.data import get_market_data
    
    print("\n⚠️  API呼び出し中... (キャッシュがあれば即座に完了)")
    df, _ = get_market_data(_force_refresh=False)
    actual_count = len(df.columns)
    
    print(f"\n期待値: {EXPECTED_INDICATOR_COUNT}")
    print(f"実際値: {actual_count}")
    
    if actual_count < EXPECTED_INDICATOR_COUNT:
        print(f"❌ 指標が不足しています！ ({EXPECTED_INDICATOR_COUNT - actual_count}個足りない)")
        print(f"   これは意図しない変更の可能性があります。")
        assert False, f"指標数が期待値より少ない: {actual_count} < {EXPECTED_INDICATOR_COUNT}"
    
    if actual_count > EXPECTED_INDICATOR_COUNT:
        print(f"ℹ️  指標が増えています ({actual_count - EXPECTED_INDICATOR_COUNT}個多い)")
        print(f"   意図した追加なら expected_indicators.py を更新してください。")
    
    print(f"✅ 指標数チェック完了")


def test_net_liquidity_calculation():
    """Net Liquidity計算式が正しいことを確認 (API必要)"""
    from utils.data import get_market_data
    
    print("\n⚠️  API呼び出し中... (キャッシュがあれば即座に完了)")
    df, _ = get_market_data(_force_refresh=False)
    
    # 計算式: Fed_Assets - TGA - ON_RRP - SRF - FIMA
    required = ['Fed_Assets', 'TGA', 'ON_RRP', 'SRF', 'FIMA', 'Net_Liquidity']
    
    # 必要な列があるか確認
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"⚠️ 以下の列が存在しないためスキップ: {missing}")
        return
    
    # 最新の有効な行で検証
    df_valid = df.dropna(subset=required)
    if df_valid.empty:
        print("⚠️ 有効なデータがないためスキップ")
        return
    
    latest = df_valid.iloc[-1]
    
    expected = latest['Fed_Assets'] - latest['TGA'] - latest['ON_RRP'] - latest['SRF'] - latest['FIMA']
    actual = latest['Net_Liquidity']
    diff = abs(expected - actual)
    
    print(f"\n計算式: Fed_Assets - TGA - ON_RRP - SRF - FIMA")
    print(f"  Fed_Assets: {latest['Fed_Assets']:.2f}")
    print(f"  TGA:        {latest['TGA']:.2f}")
    print(f"  ON_RRP:     {latest['ON_RRP']:.2f}")
    print(f"  SRF:        {latest['SRF']:.2f}")
    print(f"  FIMA:       {latest['FIMA']:.2f}")
    print(f"  ---")
    print(f"  期待値:     {expected:.2f}")
    print(f"  実際値:     {actual:.2f}")
    print(f"  差分:       {diff:.2f}")
    
    tolerance = CALCULATION_RULES['Net_Liquidity']['tolerance']
    if diff > tolerance:
        print(f"❌ Net Liquidity計算式が正しくありません！")
        assert False, f"計算誤差が大きすぎる: {diff:.2f} > {tolerance}"
    else:
        print(f"✅ Net Liquidity計算式チェック完了 (誤差: {diff:.4f})")


def test_bills_ratio_calculation():
    """Bills Ratio計算式が正しいことを確認 (API必要)"""
    from utils.data import get_market_data
    
    print("\n⚠️  API呼び出し中... (キャッシュがあれば即座に完了)")
    df, _ = get_market_data(_force_refresh=False)
    
    # 計算式: (SOMA_Bills / SOMA_Total) * 100
    required = ['SOMA_Bills', 'SOMA_Total', 'SomaBillsRatio']
    
    # 必要な列があるか確認
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"⚠️ 以下の列が存在しないためスキップ: {missing}")
        return
    
    # 最新の有効な行で検証
    df_valid = df.dropna(subset=required)
    if df_valid.empty:
        print("⚠️ 有効なデータがないためスキップ")
        return
    
    latest = df_valid.iloc[-1]
    
    expected = (latest['SOMA_Bills'] / latest['SOMA_Total']) * 100
    actual = latest['SomaBillsRatio']
    diff = abs(expected - actual)
    
    print(f"\n計算式: (SOMA_Bills / SOMA_Total) * 100")
    print(f"  SOMA_Bills: {latest['SOMA_Bills']:.2f}")
    print(f"  SOMA_Total: {latest['SOMA_Total']:.2f}")
    print(f"  ---")
    print(f"  期待値:     {expected:.2f}%")
    print(f"  実際値:     {actual:.2f}%")
    print(f"  差分:       {diff:.2f}")
    
    tolerance = CALCULATION_RULES['SomaBillsRatio']['tolerance']
    if diff > tolerance:
        print(f"❌ Bills Ratio計算式が正しくありません！")
        assert False, f"計算誤差が大きすぎる: {diff:.2f} > {tolerance}"
    else:
        print(f"✅ Bills Ratio計算式チェック完了 (誤差: {diff:.4f})")


def run_all_tests():
    """全テストを実行"""
    print("=" * 60)
    print("Market Cockpit Pro - 回帰テスト (API必要)")
    print("=" * 60)
    print("\n💡 オフラインテストには以下を使用:")
    print("   python tests/validate_structure.py")
    print("   python tests/test_calculations.py")
    
    tests = [
        ("必須列チェック", test_dataframe_has_required_columns),
        ("指標数チェック", test_indicator_count),
        ("Net Liquidity計算チェック", test_net_liquidity_calculation),
        ("Bills Ratio計算チェック", test_bills_ratio_calculation),
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️ SKIPPED: {e}")
            skipped += 1
    
    print("\n" + "=" * 60)
    print(f"結果: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
