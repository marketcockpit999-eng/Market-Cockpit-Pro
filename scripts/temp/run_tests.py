# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Test Runner
================================
全テストを実行する便利スクリプト

使い方:
    python run_tests.py           # オフラインテストのみ（推奨）
    python run_tests.py --all     # 全テスト（API含む）
    python run_tests.py --api     # APIテストのみ
"""

import subprocess
import sys
import os

def run_offline_tests():
    """オフラインテスト（即座に完了、API不要）"""
    print("=" * 60)
    print("🚀 オフラインテスト実行中...")
    print("=" * 60)
    
    results = []
    
    # 構造検証テスト
    print("\n📦 構造検証テスト...")
    result = subprocess.run(
        [sys.executable, "tests/validate_structure.py"],
        capture_output=False
    )
    results.append(("validate_structure.py", result.returncode == 0))
    
    # 計算ロジックテスト
    print("\n🔢 計算ロジックテスト...")
    result = subprocess.run(
        [sys.executable, "tests/test_calculations.py"],
        capture_output=False
    )
    results.append(("test_calculations.py", result.returncode == 0))
    
    return results


def run_api_tests():
    """APIテスト（API呼び出しあり）"""
    print("=" * 60)
    print("🌐 APIテスト実行中...")
    print("=" * 60)
    
    results = []
    
    print("\n📊 指標数検証テスト...")
    result = subprocess.run(
        [sys.executable, "tests/test_indicator_count.py"],
        capture_output=False
    )
    results.append(("test_indicator_count.py", result.returncode == 0))
    
    return results


def print_summary(results, title):
    """結果サマリーを表示"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    
    passed = sum(1 for _, ok in results if ok)
    failed = sum(1 for _, ok in results if not ok)
    
    for name, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n合計: {passed} passed, {failed} failed")
    return failed == 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Market Cockpit Pro テストランナー")
    parser.add_argument("--all", action="store_true", help="全テスト実行（API含む）")
    parser.add_argument("--api", action="store_true", help="APIテストのみ")
    args = parser.parse_args()
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    all_results = []
    
    if args.api:
        # APIテストのみ
        api_results = run_api_tests()
        all_results.extend(api_results)
    elif args.all:
        # 全テスト
        offline_results = run_offline_tests()
        api_results = run_api_tests()
        all_results = offline_results + api_results
    else:
        # デフォルト: オフラインのみ
        offline_results = run_offline_tests()
        all_results = offline_results
        print("\n💡 APIテストも実行するには: python run_tests.py --all")
    
    success = print_summary(all_results, "テスト結果サマリー")
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 全テスト成功！")
    else:
        print("⚠️  一部のテストが失敗しました")
    print(f"{'='*60}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
