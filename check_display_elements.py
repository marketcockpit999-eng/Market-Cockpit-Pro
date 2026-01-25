# -*- coding: utf-8 -*-
"""
Display Elements Checker
========================
各指標が標準9要素を満たしているかチェック
"""

import sys
sys.path.insert(0, '.')

from utils.indicators import INDICATORS
from utils.i18n import TRANSLATIONS

def check_help_texts():
    """HELPテキストの欠損をチェック"""
    help_en = TRANSLATIONS.get('en', {})
    help_ja = TRANSLATIONS.get('ja', {})
    
    missing_help = []
    
    for name, info in INDICATORS.items():
        # help_key の命名規則を確認
        possible_keys = [
            f'help_{name.lower()}',
            f'{name.lower()}_help',
            f'HELP_{name}',
        ]
        
        # 英語HELPの存在確認
        found_en = any(k in help_en for k in possible_keys)
        found_ja = any(k in help_ja for k in possible_keys)
        
        if not found_en and not found_ja:
            missing_help.append({
                'name': name,
                'pattern': info.get('display_pattern', 'standard'),
                'page': info.get('ui_page', 'unknown'),
            })
    
    return missing_help


def check_notes():
    """notesの欠損をチェック"""
    missing_notes = []
    
    for name, info in INDICATORS.items():
        if not info.get('notes'):
            missing_notes.append({
                'name': name,
                'pattern': info.get('display_pattern', 'standard'),
                'page': info.get('ui_page', 'unknown'),
            })
    
    return missing_notes


def count_by_pattern():
    """パターン別の件数を集計"""
    patterns = {}
    for name, info in INDICATORS.items():
        pattern = info.get('display_pattern', 'standard')
        if pattern not in patterns:
            patterns[pattern] = []
        patterns[pattern].append(name)
    
    return patterns


def main():
    print("=" * 60)
    print("Display Elements Checker")
    print("=" * 60)
    
    # パターン別件数
    print("\n📊 パターン別件数:")
    patterns = count_by_pattern()
    total = 0
    for pattern, indicators in sorted(patterns.items()):
        print(f"  {pattern}: {len(indicators)}件")
        total += len(indicators)
    print(f"  ----------")
    print(f"  合計: {total}件")
    
    # Notes欠損チェック
    print("\n📝 notes欠損:")
    missing_notes = check_notes()
    if missing_notes:
        for item in missing_notes:
            print(f"  ❌ {item['name']} ({item['pattern']}, {item['page']})")
    else:
        print("  ✅ 全項目にnotesあり")
    
    # HELPテキスト欠損チェック（参考情報）
    print("\n❓ HELPテキスト欠損（参考）:")
    missing_help = check_help_texts()
    print(f"  ※ 現在の実装ではHELPはi18n.pyで別管理")
    print(f"  ※ 欠損数: {len(missing_help)}件（詳細は後で対応）")
    
    # パターン別詳細
    print("\n📋 パターン別詳細:")
    for pattern in ['mom_yoy', 'manual_calc', 'web_scrape', 'calculated', 'api']:
        if pattern in patterns:
            print(f"\n  【{pattern}】({len(patterns[pattern])}件)")
            for name in patterns[pattern]:
                info = INDICATORS[name]
                notes = info.get('notes', '❌なし')[:30]
                print(f"    - {name}: {notes}")


if __name__ == '__main__':
    main()
