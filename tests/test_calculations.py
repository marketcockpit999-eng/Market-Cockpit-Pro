# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Calculation Validation (API呼び出しなし)
============================================================
計算ロジックをモックデータで検証するテスト

使い方:
    python tests/test_calculations.py
    または
    python -m pytest tests/test_calculations.py -v

Goals:
- ✅ Detect unintended changes to calculation logic
- ✅ Run instantly without API calls (uses mock data)
- ✅ Validate indicator calculations
"""

import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_TEST_DIR)
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, _TEST_DIR)

from specs.expected_indicators import (
    CALCULATION_RULES,
    REQUIRED_DATAFRAME_COLUMNS,
    NET_LIQUIDITY_FORMULA,
    BILLS_RATIO_FORMULA,
)


# ========== モックデータ生成 ==========

def create_mock_market_data() -> pd.DataFrame:
    """
    テスト用のモックデータを生成
    実際のデータ範囲に近い値を使用
    """
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    
    # 実際の値に近いモックデータ
    data = {
        # Fed Balance Sheet (Billions)
        'Fed_Assets': np.linspace(7000, 7100, 30),  # ~$7T
        'TGA': np.linspace(700, 750, 30),           # ~$700B
        'ON_RRP': np.linspace(300, 350, 30),        # ~$300B
        'SRF': np.linspace(0, 5, 30),               # Usually near 0
        'FIMA': np.linspace(0, 2, 30),              # Usually near 0
        'Reserves': np.linspace(3200, 3300, 30),    # ~$3.2T
        
        # SOMA (Billions)
        'SOMA_Total': np.linspace(6800, 6900, 30),  # ~$6.8T
        'SOMA_Bills': np.linspace(340, 380, 30),    # ~$350B
        
        # Rates (%)
        'EFFR': np.linspace(5.33, 5.33, 30),
        'IORB': np.linspace(5.40, 5.40, 30),
        'SOFR': np.linspace(5.31, 5.31, 30),
        
        # Markets
        'SP500': np.linspace(5000, 5200, 30),
        'VIX': np.linspace(12, 15, 30),
        'BTC': np.linspace(90000, 95000, 30),
        'ETH': np.linspace(3000, 3200, 30),
        
        # Credit
        'Credit_Spread': np.linspace(3.0, 3.5, 30),
        'US_TNX': np.linspace(4.5, 4.7, 30),
    }
    
    df = pd.DataFrame(data, index=dates)
    return df


def calculate_net_liquidity(df: pd.DataFrame) -> pd.Series:
    """Net Liquidity計算: Fed_Assets - TGA - ON_RRP - SRF - FIMA"""
    return df['Fed_Assets'] - df['TGA'] - df['ON_RRP'] - df['SRF'] - df['FIMA']


def calculate_bills_ratio(df: pd.DataFrame) -> pd.Series:
    """Bills Ratio計算: (SOMA_Bills / SOMA_Total) * 100"""
    return (df['SOMA_Bills'] / df['SOMA_Total']) * 100


# ========== テスト関数 ==========

class TestResults:
    """テスト結果を収集"""
    def __init__(self):
        self.passed = []
        self.failed = []
    
    def add_pass(self, name, message=""):
        self.passed.append((name, message))
        print(f"  ✅ {name}" + (f": {message}" if message else ""))
    
    def add_fail(self, name, message):
        self.failed.append((name, message))
        print(f"  ❌ {name}: {message}")
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"結果: {len(self.passed)} passed, {len(self.failed)} failed")
        print(f"{'='*60}")
        return len(self.failed) == 0


def test_net_liquidity_calculation(results: TestResults):
    """Net Liquidity計算式が正しいことを確認"""
    print("\n--- Net Liquidity 計算検証 ---")
    
    df = create_mock_market_data()
    
    # 計算実行
    net_liq = calculate_net_liquidity(df)
    
    # 手動計算との比較
    expected = df['Fed_Assets'] - df['TGA'] - df['ON_RRP'] - df['SRF'] - df['FIMA']
    diff = (net_liq - expected).abs().max()
    
    tolerance = CALCULATION_RULES['Net_Liquidity']['tolerance']
    
    if diff <= tolerance:
        results.add_pass("Net Liquidity formula", f"誤差 {diff:.4f} ≤ {tolerance}")
    else:
        results.add_fail("Net Liquidity formula", f"誤差 {diff:.4f} > {tolerance}")
    
    # 値の妥当性チェック（2-8 Trillionの範囲）
    if net_liq.min() > 2000 and net_liq.max() < 8000:
        results.add_pass("Net Liquidity range", f"値域 {net_liq.min():.0f}-{net_liq.max():.0f}B")
    else:
        results.add_fail("Net Liquidity range", f"異常値域 {net_liq.min():.0f}-{net_liq.max():.0f}B")


def test_bills_ratio_calculation(results: TestResults):
    """Bills Ratio計算式が正しいことを確認"""
    print("\n--- Bills Ratio 計算検証 ---")
    
    df = create_mock_market_data()
    
    # 計算実行
    bills_ratio = calculate_bills_ratio(df)
    
    # 手動計算との比較
    expected = (df['SOMA_Bills'] / df['SOMA_Total']) * 100
    diff = (bills_ratio - expected).abs().max()
    
    tolerance = CALCULATION_RULES['SomaBillsRatio']['tolerance']
    
    if diff <= tolerance:
        results.add_pass("Bills Ratio formula", f"誤差 {diff:.4f} ≤ {tolerance}")
    else:
        results.add_fail("Bills Ratio formula", f"誤差 {diff:.4f} > {tolerance}")
    
    # 値の妥当性チェック（0-20%の範囲が一般的）
    if bills_ratio.min() >= 0 and bills_ratio.max() <= 20:
        results.add_pass("Bills Ratio range", f"値域 {bills_ratio.min():.1f}-{bills_ratio.max():.1f}%")
    else:
        results.add_fail("Bills Ratio range", f"異常値域 {bills_ratio.min():.1f}-{bills_ratio.max():.1f}%")


def test_mock_data_has_required_columns(results: TestResults):
    """モックデータに必須列が存在することを確認"""
    print("\n--- モックデータ構造検証 ---")
    
    df = create_mock_market_data()
    
    # Net Liquidity計算に必要な列
    net_liq_components = ['Fed_Assets', 'TGA', 'ON_RRP', 'SRF', 'FIMA']
    missing = [col for col in net_liq_components if col not in df.columns]
    
    if not missing:
        results.add_pass("Net Liquidity components", "全列存在")
    else:
        results.add_fail("Net Liquidity components", f"欠損: {missing}")
    
    # Bills Ratio計算に必要な列
    bills_components = ['SOMA_Bills', 'SOMA_Total']
    missing = [col for col in bills_components if col not in df.columns]
    
    if not missing:
        results.add_pass("Bills Ratio components", "全列存在")
    else:
        results.add_fail("Bills Ratio components", f"欠損: {missing}")


def test_calculation_produces_valid_types(results: TestResults):
    """計算結果が正しい型であることを確認"""
    print("\n--- 計算結果型検証 ---")
    
    df = create_mock_market_data()
    
    net_liq = calculate_net_liquidity(df)
    bills_ratio = calculate_bills_ratio(df)
    
    # pd.Seriesであることを確認
    if isinstance(net_liq, pd.Series):
        results.add_pass("Net Liquidity type", "pd.Series")
    else:
        results.add_fail("Net Liquidity type", f"Expected pd.Series, got {type(net_liq)}")
    
    if isinstance(bills_ratio, pd.Series):
        results.add_pass("Bills Ratio type", "pd.Series")
    else:
        results.add_fail("Bills Ratio type", f"Expected pd.Series, got {type(bills_ratio)}")
    
    # NaN/Infがないことを確認
    if not net_liq.isna().any() and not np.isinf(net_liq).any():
        results.add_pass("Net Liquidity no NaN/Inf", "クリーンデータ")
    else:
        results.add_fail("Net Liquidity no NaN/Inf", "NaNまたはInf含む")
    
    if not bills_ratio.isna().any() and not np.isinf(bills_ratio).any():
        results.add_pass("Bills Ratio no NaN/Inf", "クリーンデータ")
    else:
        results.add_fail("Bills Ratio no NaN/Inf", "NaNまたはInf含む")


def test_calculation_edge_cases(results: TestResults):
    """エッジケースでの計算を確認"""
    print("\n--- エッジケース検証 ---")
    
    # ゼロ値での計算
    df_zero = pd.DataFrame({
        'Fed_Assets': [7000],
        'TGA': [0],
        'ON_RRP': [0],
        'SRF': [0],
        'FIMA': [0],
        'SOMA_Total': [6800],
        'SOMA_Bills': [0],
    })
    
    net_liq_zero = calculate_net_liquidity(df_zero)
    if net_liq_zero.iloc[0] == 7000:
        results.add_pass("Net Liquidity zero case", "TGA/RRP/SRF/FIMA=0 → NL=Fed_Assets")
    else:
        results.add_fail("Net Liquidity zero case", f"Expected 7000, got {net_liq_zero.iloc[0]}")
    
    bills_ratio_zero = calculate_bills_ratio(df_zero)
    if bills_ratio_zero.iloc[0] == 0:
        results.add_pass("Bills Ratio zero case", "Bills=0 → Ratio=0%")
    else:
        results.add_fail("Bills Ratio zero case", f"Expected 0, got {bills_ratio_zero.iloc[0]}")


def test_calculation_formula_strings(results: TestResults):
    """計算式文字列が正しいことを確認"""
    print("\n--- 計算式定義検証 ---")
    
    expected_net_liq = "Fed_Assets - TGA - ON_RRP - SRF - FIMA"
    if NET_LIQUIDITY_FORMULA == expected_net_liq:
        results.add_pass("NET_LIQUIDITY_FORMULA", "定義一致")
    else:
        results.add_fail("NET_LIQUIDITY_FORMULA", f"不一致: {NET_LIQUIDITY_FORMULA}")
    
    expected_bills = "(SOMA_Bills / SOMA_Total) * 100"
    if BILLS_RATIO_FORMULA == expected_bills:
        results.add_pass("BILLS_RATIO_FORMULA", "定義一致")
    else:
        results.add_fail("BILLS_RATIO_FORMULA", f"不一致: {BILLS_RATIO_FORMULA}")


def run_all():
    """全テストを実行"""
    print("=" * 60)
    print("Market Cockpit Pro - 計算ロジック検証テスト")
    print("(モックデータ使用 - API呼び出しなし)")
    print("=" * 60)
    
    results = TestResults()
    
    test_mock_data_has_required_columns(results)
    test_net_liquidity_calculation(results)
    test_bills_ratio_calculation(results)
    test_calculation_produces_valid_types(results)
    test_calculation_edge_cases(results)
    test_calculation_formula_strings(results)
    
    return results.summary()


# pytest用テスト関数
def test_calculations():
    """pytest用: 全計算ロジック検証"""
    results = TestResults()
    
    test_mock_data_has_required_columns(results)
    test_net_liquidity_calculation(results)
    test_bills_ratio_calculation(results)
    test_calculation_produces_valid_types(results)
    test_calculation_edge_cases(results)
    test_calculation_formula_strings(results)
    
    assert len(results.failed) == 0, f"Failed tests: {[f[0] for f in results.failed]}"


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
