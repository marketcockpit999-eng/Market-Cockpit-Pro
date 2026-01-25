# -*- coding: utf-8 -*-
"""
display_pattern 検証スクリプト
実行: python scripts/verify_display_pattern.py
"""
import sys
sys.path.insert(0, '.')

from utils.indicators import INDICATORS
from collections import Counter

def verify():
    # 全項目にdisplay_patternがあるか確認
    missing = []
    for name, info in INDICATORS.items():
        if 'display_pattern' not in info:
            missing.append(name)

    if missing:
        print(f"❌ display_pattern未設定: {len(missing)}項目")
        for name in missing:
            print(f"  - {name}")
        return False
    else:
        print(f"✅ 全{len(INDICATORS)}項目にdisplay_pattern設定済み")

    # パターン別集計
    patterns = Counter(v.get('display_pattern') for v in INDICATORS.values())
    print("\nパターン別集計:")
    for pattern, count in sorted(patterns.items()):
        print(f"  {pattern}: {count}")
    
    # 期待値チェック
    expected = {
        'standard': 73,
        'mom_yoy': 6,
        'manual_calc': 6,
        'web_scrape': 2,
        'calculated': 1,
        'api': 12,
    }
    
    print("\n期待値との比較:")
    all_ok = True
    for pattern, expected_count in expected.items():
        actual = patterns.get(pattern, 0)
        if actual == expected_count:
            print(f"  ✅ {pattern}: {actual} (期待: {expected_count})")
        else:
            print(f"  ❌ {pattern}: {actual} (期待: {expected_count})")
            all_ok = False
    
    return all_ok and len(missing) == 0

if __name__ == '__main__':
    success = verify()
    sys.exit(0 if success else 1)
