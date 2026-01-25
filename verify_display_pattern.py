# verify_display_pattern.py
import sys
import os

# Add current directory to path so we can import utils
sys.path.append(os.getcwd())

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
    else:
        print(f"✅ 全{len(INDICATORS)}項目にdisplay_pattern設定済み")

    # パターン別集計
    patterns = Counter(v.get('display_pattern') for v in INDICATORS.values())
    print("\nパターン別集計:")
    for pattern, count in sorted(patterns.items()):
        print(f"  {pattern}: {count}")

if __name__ == "__main__":
    verify()
