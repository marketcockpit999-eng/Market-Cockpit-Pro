# -*- coding: utf-8 -*-
"""
クイック診断: RetailSalesとPPIの状態確認
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.indicators import INDICATORS, FRED_INDICATORS

print("=" * 60)
print("RetailSales と PPI の診断")
print("=" * 60)

# 1. INDICATORSに存在するか
print("\n【1】INDICATORS定義の確認:")
for name in ['RetailSales', 'PPI']:
    if name in INDICATORS:
        info = INDICATORS[name]
        print(f"✅ {name}")
        print(f"   Source: {info.get('source')}")
        print(f"   ID: {info.get('id')}")
        print(f"   UI Page: {info.get('ui_page')}")
        print(f"   Category: {info.get('category')}")
    else:
        print(f"❌ {name} - 定義なし")

# 2. FRED_INDICATORSに存在するか
print("\n【2】FRED_INDICATORS辞書の確認:")
for name in ['RetailSales', 'PPI']:
    if name in FRED_INDICATORS:
        series_id = FRED_INDICATORS[name]
        print(f"✅ {name} → {series_id}")
    else:
        print(f"❌ {name} - FRED_INDICATORSに未登録")

# 3. US Economic Dataページの指標一覧
print("\n【3】US Economic Data ページの全指標:")
us_econ = [k for k, v in INDICATORS.items() if v.get('ui_page') == '03_us_economic']
print(f"合計: {len(us_econ)} 指標")
for name in sorted(us_econ):
    source = INDICATORS[name].get('source')
    series_id = INDICATORS[name].get('id')
    print(f"  - {name} ({source}: {series_id})")

print("\n" + "=" * 60)
