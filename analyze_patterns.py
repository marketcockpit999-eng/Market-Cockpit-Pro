# -*- coding: utf-8 -*-
"""
パターン分類スクリプト
100項目を基本パターンに分類し、あふれるものを特定
"""

from utils.indicators import INDICATORS

# パターン定義
PATTERN_A = "日次/週次フル (10要素)"      # 60日推移あり + 長期チャート
PATTERN_B1 = "月次/四半期シンプル (9要素)" # 60日推移なし + 長期チャート1つ  
PATTERN_B2 = "月次MoM/YoY (特殊)"         # 前月比+前年比 + 2チャート
PATTERN_API = "API系 (別処理)"            # 外部API
PATTERN_OTHER = "その他/例外"

# 分類結果
results = {
    PATTERN_A: [],
    PATTERN_B1: [],
    PATTERN_B2: [],
    PATTERN_API: [],
    PATTERN_OTHER: [],
}

# 分類ロジック
for name, config in INDICATORS.items():
    freq = config.get('frequency', '')
    display = config.get('display_pattern', 'standard')
    source = config.get('source', '')
    df_stored = config.get('df_stored', True)
    
    # API系（dfに入らない）
    if df_stored == False or display == 'api':
        results[PATTERN_API].append(name)
    
    # MoM/YoY パターン
    elif display == 'mom_yoy':
        results[PATTERN_B2].append(name)
    
    # 日次/週次 → パターンA
    elif freq in ['daily', 'weekly'] and display == 'standard':
        results[PATTERN_A].append(name)
    
    # 月次/四半期 standard → パターンB1
    elif freq in ['monthly', 'quarterly'] and display == 'standard':
        results[PATTERN_B1].append(name)
    
    # その他
    else:
        results[PATTERN_OTHER].append(name)

# 出力
print("=" * 70)
print("📊 パターン分類結果")
print("=" * 70)

total = 0
for pattern, items in results.items():
    count = len(items)
    total += count
    print(f"\n### {pattern}: {count}項目")
    print("-" * 50)
    for name in sorted(items):
        config = INDICATORS[name]
        freq = config.get('frequency', '?')
        display = config.get('display_pattern', '?')
        notes = config.get('notes', '')[:30]
        print(f"  {name:<25} [{freq:<9}] {display:<12} {notes}")

print("\n" + "=" * 70)
print(f"合計: {total}項目")
print("=" * 70)

# サマリー
print("\n📋 サマリー")
print("-" * 30)
for pattern, items in results.items():
    print(f"  {pattern}: {len(items)}")
