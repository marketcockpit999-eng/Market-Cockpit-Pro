# -*- coding: utf-8 -*-
"""
診断スクリプト: Missing Indicatorsの特定
実行方法: cd market_monitor && python diagnose_missing.py
"""

from utils.indicators import INDICATORS, get_freshness_rules

def diagnose():
    print("=" * 60)
    print("Market Cockpit Pro - Missing Indicators診断")
    print("=" * 60)
    
    # 1. INDICATORS定義数
    print(f"\n【1】INDICATORS定義数: {len(INDICATORS)}")
    
    # 2. ソース別の内訳
    sources = {}
    for k, v in INDICATORS.items():
        src = v.get('source', 'UNKNOWN')
        if src not in sources:
            sources[src] = []
        sources[src].append(k)
    
    print("\n【2】ソース別内訳:")
    for src, items in sources.items():
        print(f"  {src}: {len(items)}")
    
    # 3. DATA_FRESHNESS_RULES確認
    rules = get_freshness_rules()
    total_in_rules = sum(len(r['indicators']) for r in rules.values())
    print(f"\n【3】DATA_FRESHNESS_RULES合計: {total_in_rules}")
    for period, rule in rules.items():
        print(f"  {period}: {len(rule['indicators'])}")
    
    # 4. CALCULATEDソースのインディケーター
    calculated = [k for k, v in INDICATORS.items() if v.get('source') == 'CALCULATED']
    print(f"\n【4】CALCULATEDソース: {calculated}")
    
    # 5. 全インディケーター一覧（ソース別）
    print("\n【5】全インディケーター一覧:")
    for src, items in sorted(sources.items()):
        print(f"\n  === {src} ({len(items)}) ===")
        for item in sorted(items):
            info = INDICATORS[item]
            fred_id = info.get('id', '-')
            print(f"    {item}: {fred_id}")
    
    # 6. 重複チェック
    print("\n【6】同じFRED IDを使用している指標:")
    fred_ids = {}
    for k, v in INDICATORS.items():
        if v.get('source') == 'FRED':
            fid = v.get('id')
            if fid not in fred_ids:
                fred_ids[fid] = []
            fred_ids[fid].append(k)
    
    for fid, names in fred_ids.items():
        if len(names) > 1:
            print(f"  {fid}: {names}")
    
    print("\n" + "=" * 60)
    print("診断完了")
    print("=" * 60)

if __name__ == '__main__':
    diagnose()
