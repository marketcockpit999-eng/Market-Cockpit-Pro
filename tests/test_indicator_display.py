# -*- coding: utf-8 -*-
"""
指標表示回帰テスト
================================================================================
各ページの show_metric_with_sparkline 呼び出し数をカウントし、
期待値を下回ったらテスト失敗。

これにより「修正で指標が消える」問題を事前に検出。

Usage:
    pytest tests/test_indicator_display.py -v
    python tests/test_indicator_display.py
================================================================================
"""

import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =============================================================================
# 期待される指標呼び出し数（最小値）
# =============================================================================
# 
# ここが「保険」の役割を果たす。
# 各ページで show_metric_with_sparkline が最低何回呼ばれるべきかを定義。
# この数を下回る変更は「何かが消えた」可能性が高い。
#
# 【重要】新機能を追加したら、この数を更新する
# 【重要】削除は極めて慎重に（本当に不要か確認）
# =============================================================================

# =============================================================================
# 期待される指標呼び出し数（最小値）
# =============================================================================
# 
# 2026-01-25 実測値から設定
# 各ページの show_metric_with_sparkline 呼び出し数
#
# 【更新ルール】
# - 新指標追加時: この数を +1 する
# - 指標削除時: この数を減らす前に「本当に削除が正しいか」確認
# - 安全マージン: 実測値の80%を最小値として設定
# =============================================================================

EXPECTED_MIN_METRICS = {
    # 01_liquidity.py: 実測17回 → 最小14回（80%）
    '01_liquidity.py': {
        'show_metric_with_sparkline': 14,
    },
    # 02_global_money.py: 確認後設定
    '02_global_money.py': {
        'show_metric_with_sparkline': 2,
    },
    # 03_us_economic.py: 実測13回 → 最小10回（80%）
    '03_us_economic.py': {
        'show_metric_with_sparkline': 10,
    },
    # 04_crypto.py: 確認後設定
    '04_crypto.py': {
        'show_metric_with_sparkline': 0,
    },
    # 08_sentiment.py: 確認後設定
    '08_sentiment.py': {
        'show_metric_with_sparkline': 0,
    },
    # 09_banking.py: 確認後設定
    '09_banking.py': {
        'show_metric_with_sparkline': 4,
    },
}


def count_function_calls(filepath, function_name):
    """ファイル内の関数呼び出し回数をカウント"""
    if not os.path.exists(filepath):
        return 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # コメント行を除外してカウント
    lines = content.split('\n')
    count = 0
    for line in lines:
        stripped = line.strip()
        # コメント行をスキップ
        if stripped.startswith('#'):
            continue
        # 関数呼び出しをカウント
        if function_name + '(' in line:
            count += 1
    
    return count


def test_liquidity_page_metrics():
    """01_liquidity.py の指標数テスト"""
    filepath = os.path.join(PROJECT_ROOT, 'pages', '01_liquidity.py')
    expected = EXPECTED_MIN_METRICS.get('01_liquidity.py', {})
    
    for func, min_count in expected.items():
        actual = count_function_calls(filepath, func)
        assert actual >= min_count, (
            f"[WARN] 01_liquidity.py: {func}() が減少！\n"
            f"   期待: {min_count}回以上\n"
            f"   実際: {actual}回\n"
            f"   → 何か指標が削除された可能性があります"
        )


def test_global_money_page_metrics():
    """02_global_money.py の指標数テスト"""
    filepath = os.path.join(PROJECT_ROOT, 'pages', '02_global_money.py')
    expected = EXPECTED_MIN_METRICS.get('02_global_money.py', {})
    
    for func, min_count in expected.items():
        actual = count_function_calls(filepath, func)
        assert actual >= min_count, (
            f"[WARN] 02_global_money.py: {func}() が減少！\n"
            f"   期待: {min_count}回以上\n"
            f"   実際: {actual}回\n"
            f"   → 何か指標が削除された可能性があります"
        )


def test_us_economic_page_metrics():
    """03_us_economic.py の指標数テスト"""
    filepath = os.path.join(PROJECT_ROOT, 'pages', '03_us_economic.py')
    expected = EXPECTED_MIN_METRICS.get('03_us_economic.py', {})
    
    for func, min_count in expected.items():
        actual = count_function_calls(filepath, func)
        assert actual >= min_count, (
            f"[WARN] 03_us_economic.py: {func}() が減少！\n"
            f"   期待: {min_count}回以上\n"
            f"   実際: {actual}回\n"
            f"   → 何か指標が削除された可能性があります"
        )


def test_crypto_page_metrics():
    """04_crypto.py の指標数テスト"""
    filepath = os.path.join(PROJECT_ROOT, 'pages', '04_crypto.py')
    expected = EXPECTED_MIN_METRICS.get('04_crypto.py', {})
    
    for func, min_count in expected.items():
        actual = count_function_calls(filepath, func)
        assert actual >= min_count, (
            f"[WARN] 04_crypto.py: {func}() が減少！\n"
            f"   期待: {min_count}回以上\n"
            f"   実際: {actual}回\n"
            f"   → 何か指標が削除された可能性があります"
        )


def test_sentiment_page_metrics():
    """08_sentiment.py の指標数テスト"""
    filepath = os.path.join(PROJECT_ROOT, 'pages', '08_sentiment.py')
    expected = EXPECTED_MIN_METRICS.get('08_sentiment.py', {})
    
    for func, min_count in expected.items():
        actual = count_function_calls(filepath, func)
        assert actual >= min_count, (
            f"[WARN] 08_sentiment.py: {func}() が減少！\n"
            f"   期待: {min_count}回以上\n"
            f"   実際: {actual}回\n"
            f"   → 何か指標が削除された可能性があります"
        )


def test_banking_page_metrics():
    """09_banking.py の指標数テスト"""
    filepath = os.path.join(PROJECT_ROOT, 'pages', '09_banking.py')
    expected = EXPECTED_MIN_METRICS.get('09_banking.py', {})
    
    for func, min_count in expected.items():
        actual = count_function_calls(filepath, func)
        assert actual >= min_count, (
            f"[WARN] 09_banking.py: {func}() が減少！\n"
            f"   期待: {min_count}回以上\n"
            f"   実際: {actual}回\n"
            f"   → 何か指標が削除された可能性があります"
        )


# =============================================================================
# サマリーレポート
# =============================================================================

def print_metrics_summary():
    """全ページの指標数サマリーを表示"""
    print("\n" + "=" * 60)
    print("[SUMMARY] INDICATOR COUNT SUMMARY")
    print("=" * 60)
    
    pages_dir = os.path.join(PROJECT_ROOT, 'pages')
    
    for page_file in sorted(os.listdir(pages_dir)):
        if not page_file.endswith('.py'):
            continue
        
        filepath = os.path.join(pages_dir, page_file)
        metric_count = count_function_calls(filepath, 'show_metric_with_sparkline')
        expected = EXPECTED_MIN_METRICS.get(page_file, {}).get('show_metric_with_sparkline', '?')
        
        status = '[OK]' if metric_count >= (expected if isinstance(expected, int) else 0) else '[WARN]'
        print(f"  {status} {page_file}: {metric_count} calls (min: {expected})")
    
    print("=" * 60)


# =============================================================================
# 直接実行
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("[REGRESSION] INDICATOR DISPLAY TEST")
    print("=" * 60)
    
    all_passed = True
    
    tests = [
        ('01_liquidity.py', test_liquidity_page_metrics),
        ('02_global_money.py', test_global_money_page_metrics),
        ('03_us_economic.py', test_us_economic_page_metrics),
        ('04_crypto.py', test_crypto_page_metrics),
        ('08_sentiment.py', test_sentiment_page_metrics),
        ('09_banking.py', test_banking_page_metrics),
    ]
    
    for page, test_func in tests:
        try:
            test_func()
            print(f"  [OK] {page}")
        except AssertionError as e:
            print(f"  [NG] {page}")
            print(f"       {e}")
            all_passed = False
        except Exception as e:
            print(f"  [NG] {page}: {type(e).__name__}: {e}")
            all_passed = False
    
    print_metrics_summary()
    
    if all_passed:
        print("\n[SUCCESS] ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n[FAIL] SOME TESTS FAILED")
        sys.exit(1)
