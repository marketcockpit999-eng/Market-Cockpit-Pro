# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Structure Validation (API呼び出しなし)
==========================================================
コードの構造を検証するテスト（データ取得不要・即座に完了）

使い方:
    python tests/validate_structure.py
    または
    python -m pytest tests/validate_structure.py -v

Goals:
- ✅ Detect unintended changes when code is modified
- ✅ Run instantly without API calls
- ✅ Validate indicator count, required columns, calculations (定義のみ)
"""

import sys
import os
import re

# Add parent directory to path for both direct execution and pytest
_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_TEST_DIR)
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, _TEST_DIR)

from specs.expected_indicators import (
    EXPECTED_PAGE_FILES,
    EXPECTED_UTILS_MODULES,
    EXPECTED_FRED_KEYS,
    EXPECTED_YAHOO_KEYS,
    MIN_INDICATOR_COUNTS,
    CALCULATION_RULES,
    NET_LIQUIDITY_FORMULA,
)


class TestResults:
    """テスト結果を収集"""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, name, message=""):
        self.passed.append((name, message))
        print(f"  ✅ {name}" + (f": {message}" if message else ""))
    
    def add_fail(self, name, message):
        self.failed.append((name, message))
        print(f"  ❌ {name}: {message}")
    
    def add_warning(self, name, message):
        self.warnings.append((name, message))
        print(f"  ⚠️  {name}: {message}")
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"結果サマリー:")
        print(f"  ✅ PASSED: {len(self.passed)}")
        print(f"  ❌ FAILED: {len(self.failed)}")
        print(f"  ⚠️  WARNINGS: {len(self.warnings)}")
        print(f"{'='*60}")
        return len(self.failed) == 0


def test_constants_defined(results: TestResults):
    """constants.pyに必要な定義が存在するか"""
    print("\n--- constants.py 検証 ---")
    
    try:
        from utils.constants import (
            FRED_INDICATORS,
            YAHOO_INDICATORS,
            DATA_FRESHNESS_RULES,
        )
    except ImportError as e:
        results.add_fail("constants import", str(e))
        return
    
    # FRED指標数チェック
    fred_count = len(FRED_INDICATORS)
    if fred_count >= MIN_INDICATOR_COUNTS["FRED"]:
        results.add_pass("FRED_INDICATORS", f"{fred_count}個")
    else:
        results.add_fail("FRED_INDICATORS", f"{fred_count}個 < 最小{MIN_INDICATOR_COUNTS['FRED']}個")
    
    # Yahoo指標数チェック
    yahoo_count = len(YAHOO_INDICATORS)
    if yahoo_count >= MIN_INDICATOR_COUNTS["Yahoo"]:
        results.add_pass("YAHOO_INDICATORS", f"{yahoo_count}個")
    else:
        results.add_fail("YAHOO_INDICATORS", f"{yahoo_count}個 < 最小{MIN_INDICATOR_COUNTS['Yahoo']}個")
    
    # 監視対象指標数チェック
    all_monitored = []
    for freq, rules in DATA_FRESHNESS_RULES.items():
        all_monitored.extend(rules['indicators'])
    monitored_count = len(all_monitored)
    if monitored_count >= MIN_INDICATOR_COUNTS["Total_Monitored"]:
        results.add_pass("DATA_FRESHNESS_RULES", f"監視対象{monitored_count}個")
    else:
        results.add_fail("DATA_FRESHNESS_RULES", f"{monitored_count}個 < 最小{MIN_INDICATOR_COUNTS['Total_Monitored']}個")


def test_fred_keys_exist(results: TestResults):
    """期待されるFRED指標キーが存在するか"""
    print("\n--- FRED指標キー検証 ---")
    
    try:
        from utils.constants import FRED_INDICATORS
    except ImportError:
        results.add_fail("FRED_INDICATORS import", "インポート失敗")
        return
    
    missing = []
    for key in EXPECTED_FRED_KEYS:
        if key not in FRED_INDICATORS:
            missing.append(key)
    
    if not missing:
        results.add_pass("FRED keys", f"全{len(EXPECTED_FRED_KEYS)}キー存在")
    else:
        results.add_fail("FRED keys", f"欠損: {missing}")
    
    # 追加されたキーの警告
    extra = [k for k in FRED_INDICATORS.keys() if k not in EXPECTED_FRED_KEYS]
    if extra:
        results.add_warning("FRED extra keys", f"未登録キー: {extra[:5]}{'...' if len(extra) > 5 else ''}")


def test_yahoo_keys_exist(results: TestResults):
    """期待されるYahoo指標キーが存在するか"""
    print("\n--- Yahoo指標キー検証 ---")
    
    try:
        from utils.constants import YAHOO_INDICATORS
    except ImportError:
        results.add_fail("YAHOO_INDICATORS import", "インポート失敗")
        return
    
    missing = []
    for key in EXPECTED_YAHOO_KEYS:
        if key not in YAHOO_INDICATORS:
            missing.append(key)
    
    if not missing:
        results.add_pass("Yahoo keys", f"全{len(EXPECTED_YAHOO_KEYS)}キー存在")
    else:
        results.add_fail("Yahoo keys", f"欠損: {missing}")


def test_pages_exist(results: TestResults):
    """pagesフォルダに必要なファイルが存在するか"""
    print("\n--- pages/ 検証 ---")
    
    pages_dir = os.path.join(_PROJECT_ROOT, "pages")
    
    if not os.path.exists(pages_dir):
        results.add_fail("pages directory", "ディレクトリが存在しない")
        return
    
    missing = []
    for page in EXPECTED_PAGE_FILES:
        path = os.path.join(pages_dir, page)
        if not os.path.exists(path):
            missing.append(page)
    
    if not missing:
        results.add_pass("pages files", f"全{len(EXPECTED_PAGE_FILES)}ファイル存在")
    else:
        results.add_fail("pages files", f"欠損: {missing}")


def test_utils_modules(results: TestResults):
    """utilsモジュールが正しくインポートできるか"""
    print("\n--- utils/ 検証 ---")
    
    for module_name, expected_items in EXPECTED_UTILS_MODULES:
        try:
            module = __import__(module_name, fromlist=expected_items)
            missing_items = [item for item in expected_items if not hasattr(module, item)]
            if not missing_items:
                results.add_pass(module_name, f"全{len(expected_items)}項目")
            else:
                results.add_fail(module_name, f"欠損: {missing_items}")
        except ImportError as e:
            results.add_fail(module_name, f"インポート失敗: {e}")


def test_net_liquidity_formula_in_code(results: TestResults):
    """Net Liquidity計算式がコードに正しく定義されているか"""
    print("\n--- Net Liquidity 計算式検証 ---")
    
    data_path = os.path.join(_PROJECT_ROOT, "utils", "data.py")
    
    if not os.path.exists(data_path):
        results.add_fail("data.py", "ファイルが存在しない")
        return
    
    with open(data_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 計算式の構成要素をチェック
    components = ["Fed_Assets", "TGA", "ON_RRP", "SRF", "FIMA", "Net_Liquidity"]
    missing = [c for c in components if c not in content]
    
    if not missing:
        results.add_pass("Net Liquidity components", "全構成要素参照あり")
    else:
        results.add_fail("Net Liquidity components", f"欠損: {missing}")
    
    # 減算パターンの確認（簡易チェック）
    if "- TGA" in content or "-TGA" in content:
        results.add_pass("Net Liquidity formula", "減算パターン確認")
    else:
        results.add_warning("Net Liquidity formula", "減算パターンが見つからない（手動確認推奨）")


def test_calculation_rules_consistency(results: TestResults):
    """計算ルールとconstants.pyの整合性"""
    print("\n--- 計算ルール整合性検証 ---")
    
    try:
        from utils.constants import FRED_INDICATORS
    except ImportError:
        results.add_fail("constants import", "インポート失敗")
        return
    
    for calc_name, rule in CALCULATION_RULES.items():
        missing_components = []
        for comp in rule.get("components", []):
            # FRED_INDICATORSかYahoo_INDICATORSにあるか（またはdata.pyで計算される列か）
            if comp not in FRED_INDICATORS:
                # 計算列は許容
                if comp not in ["Net_Liquidity", "SomaBillsRatio"]:
                    # Yahooをチェック
                    try:
                        from utils.constants import YAHOO_INDICATORS
                        if comp not in YAHOO_INDICATORS:
                            missing_components.append(comp)
                    except:
                        missing_components.append(comp)
        
        if not missing_components:
            results.add_pass(f"{calc_name} components", "全構成要素定義済み")
        else:
            results.add_fail(f"{calc_name} components", f"未定義: {missing_components}")


def test_explanations_coverage(results: TestResults):
    """EXPLANATIONS辞書が主要指標をカバーしているか"""
    print("\n--- EXPLANATIONS カバレッジ検証 ---")
    
    try:
        from utils.constants import EXPLANATIONS
    except ImportError:
        try:
            from utils.config import EXPLANATIONS
        except ImportError:
            results.add_fail("EXPLANATIONS import", "インポート失敗")
            return
    
    # 重要指標の説明があるか
    critical_indicators = [
        "Net_Liquidity", "Reserves", "TGA", "ON_RRP", "VIX", 
        "SRF", "FIMA", "SOFR", "M2SL"
    ]
    
    missing_explanations = [ind for ind in critical_indicators if ind not in EXPLANATIONS]
    
    if not missing_explanations:
        results.add_pass("EXPLANATIONS coverage", f"重要指標{len(critical_indicators)}個カバー")
    else:
        results.add_warning("EXPLANATIONS coverage", f"説明なし: {missing_explanations}")


def test_data_freshness_rules_complete(results: TestResults):
    """DATA_FRESHNESS_RULESが全カテゴリを含むか"""
    print("\n--- DATA_FRESHNESS_RULES 完全性検証 ---")
    
    try:
        from utils.constants import DATA_FRESHNESS_RULES
    except ImportError:
        results.add_fail("DATA_FRESHNESS_RULES import", "インポート失敗")
        return
    
    expected_categories = ['daily', 'weekly', 'monthly', 'quarterly']
    missing = [cat for cat in expected_categories if cat not in DATA_FRESHNESS_RULES]
    
    if not missing:
        results.add_pass("DATA_FRESHNESS_RULES categories", f"全{len(expected_categories)}カテゴリ存在")
    else:
        results.add_fail("DATA_FRESHNESS_RULES categories", f"欠損: {missing}")
    
    # 各カテゴリに必須フィールドがあるか
    required_fields = ['fresh', 'stale', 'critical', 'indicators']
    for cat in DATA_FRESHNESS_RULES:
        missing_fields = [f for f in required_fields if f not in DATA_FRESHNESS_RULES[cat]]
        if missing_fields:
            results.add_fail(f"DATA_FRESHNESS_RULES[{cat}]", f"欠損フィールド: {missing_fields}")


def run_all():
    """全テストを実行"""
    print("=" * 60)
    print("Market Cockpit Pro - 構造検証テスト")
    print("(API呼び出しなし - 即座に完了)")
    print("=" * 60)
    
    results = TestResults()
    
    test_constants_defined(results)
    test_fred_keys_exist(results)
    test_yahoo_keys_exist(results)
    test_pages_exist(results)
    test_utils_modules(results)
    test_net_liquidity_formula_in_code(results)
    test_calculation_rules_consistency(results)
    test_explanations_coverage(results)
    test_data_freshness_rules_complete(results)
    
    return results.summary()


# pytest用テスト関数
def test_structure_validation():
    """pytest用: 全構造検証"""
    results = TestResults()
    
    test_constants_defined(results)
    test_fred_keys_exist(results)
    test_yahoo_keys_exist(results)
    test_pages_exist(results)
    test_utils_modules(results)
    test_net_liquidity_formula_in_code(results)
    test_calculation_rules_consistency(results)
    test_explanations_coverage(results)
    test_data_freshness_rules_complete(results)
    
    assert len(results.failed) == 0, f"Failed tests: {[f[0] for f in results.failed]}"


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
