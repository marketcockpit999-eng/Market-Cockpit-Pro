# -*- coding: utf-8 -*-
"""
FRED Data Verification Script
==============================
全FRED指標の有効性と最新データを検証するスクリプト

使い方:
    cd C:/Users/81802/.gemini/antigravity/scratch/market_monitor
    python scripts/verify_fred_data.py

チェック項目:
1. FRED IDが有効か（エラーなしでデータ取得可能か）
2. シリーズがDISCONTINUEDでないか
3. 最新データの日付（古すぎないか）
4. データ値が妥当な範囲か
"""

import pandas as pd
import pandas_datareader.data as web
import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.indicators import INDICATORS

# Config
FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"
END_DATE = datetime.datetime.now()
START_DATE = END_DATE - datetime.timedelta(days=365)

def check_fred_series(name, info):
    """単一のFREDシリーズをチェック"""
    fred_id = info['id']
    result = {
        'name': name,
        'fred_id': fred_id,
        'status': 'OK',
        'latest_date': None,
        'latest_value': None,
        'notes': info.get('notes', ''),
        'issues': []
    }
    
    try:
        # FREDからデータ取得
        df = web.DataReader(fred_id, 'fred', START_DATE, END_DATE, api_key=FRED_API_KEY)
        
        if df.empty:
            result['status'] = 'ERROR'
            result['issues'].append('No data returned')
            return result
        
        # 最新値を取得
        latest = df.dropna().iloc[-1]
        result['latest_date'] = str(latest.name.date())
        result['latest_value'] = float(latest.values[0])
        
        # divisorを適用して表示用の値を計算
        divisor = info.get('divisor', 1)
        display_value = result['latest_value'] / divisor if divisor != 1 else result['latest_value']
        result['display_value'] = display_value
        result['unit'] = info.get('unit', '')
        
        # データ古さチェック
        latest_date = latest.name.date()
        days_old = (datetime.date.today() - latest_date).days
        
        frequency = info.get('frequency', 'unknown')
        if frequency == 'daily' and days_old > 7:
            result['issues'].append(f'[!] Data is {days_old} days old (daily expected)')
        elif frequency == 'weekly' and days_old > 14:
            result['issues'].append(f'[!] Data is {days_old} days old (weekly expected)')
        elif frequency == 'monthly' and days_old > 45:
            result['issues'].append(f'[!] Data is {days_old} days old (monthly expected)')
        elif frequency == 'quarterly' and days_old > 100:
            result['issues'].append(f'[!] Data is {days_old} days old (quarterly expected)')
        
        # バリデーション範囲チェック
        if 'validation' in info:
            min_val, max_val = info['validation']
            if not (min_val <= display_value <= max_val):
                result['issues'].append(f'[!] Value {display_value:.2f} outside range ({min_val}, {max_val})')
        
    except Exception as e:
        result['status'] = 'ERROR'
        error_msg = str(e)
        if 'DISCONTINUED' in error_msg.upper():
            result['issues'].append('[X] Series DISCONTINUED')
        elif 'not found' in error_msg.lower() or '404' in error_msg:
            result['issues'].append('[X] Series not found')
        else:
            result['issues'].append(f'[X] {error_msg[:100]}')
    
    return result


def main():
    print("=" * 80)
    print("FRED Data Verification Report")
    print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # FREDソースの指標のみ抽出
    fred_indicators = {k: v for k, v in INDICATORS.items() if v['source'] == 'FRED'}
    print(f"\n検証対象: {len(fred_indicators)} FRED indicators\n")
    
    results = []
    errors = []
    warnings = []
    
    for i, (name, info) in enumerate(fred_indicators.items(), 1):
        print(f"[{i}/{len(fred_indicators)}] Checking {name} ({info['id']})...", end=" ")
        result = check_fred_series(name, info)
        results.append(result)
        
        if result['status'] == 'ERROR':
            print("[X] ERROR")
            errors.append(result)
        elif result['issues']:
            print("[!] WARNING")
            warnings.append(result)
        else:
            print("[OK] OK")
    
    # サマリー表示
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total: {len(results)}")
    print(f"[OK] OK: {len(results) - len(errors) - len(warnings)}")
    print(f"[!] Warnings: {len(warnings)}")
    print(f"[X] Errors: {len(errors)}")
    
    # エラー詳細
    if errors:
        print("\n" + "-" * 40)
        print("ERRORS (需要即時対応)")
        print("-" * 40)
        for r in errors:
            print(f"\n{r['name']} ({r['fred_id']}):")
            print(f"  Notes: {r['notes']}")
            for issue in r['issues']:
                print(f"  → {issue}")
    
    # 警告詳細
    if warnings:
        print("\n" + "-" * 40)
        print("WARNINGS (要確認)")
        print("-" * 40)
        for r in warnings:
            print(f"\n{r['name']} ({r['fred_id']}):")
            print(f"  Notes: {r['notes']}")
            print(f"  Latest: {r['latest_date']} = {r.get('display_value', r['latest_value']):.2f} {r.get('unit', '')}")
            for issue in r['issues']:
                print(f"  → {issue}")
    
    # 重複FRED IDチェック
    print("\n" + "-" * 40)
    print("DUPLICATE FRED ID CHECK")
    print("-" * 40)
    fred_id_map = {}
    for name, info in fred_indicators.items():
        fid = info['id']
        if fid not in fred_id_map:
            fred_id_map[fid] = []
        fred_id_map[fid].append(name)
    
    duplicates = {k: v for k, v in fred_id_map.items() if len(v) > 1}
    if duplicates:
        print("[!] Same FRED ID used by multiple indicators:")
        for fid, names in duplicates.items():
            print(f"  {fid}: {', '.join(names)}")
    else:
        print("[OK] No duplicates found")
    
    # 主要指標の実データ表示
    print("\n" + "-" * 40)
    print("KEY INDICATORS - ACTUAL VALUES")
    print("-" * 40)
    key_indicators = ['ON_RRP', 'Reserves', 'TGA', 'Fed_Assets', 'SOMA_Bills', 'SOMA_Treasury', 'EFFR', 'SOFR']
    for r in results:
        if r['name'] in key_indicators:
            if r['status'] == 'OK':
                print(f"{r['name']:20} {r['fred_id']:20} = {r.get('display_value', r['latest_value']):>12,.2f} {r.get('unit', ''):>3}  ({r['latest_date']})")
            else:
                print(f"{r['name']:20} {r['fred_id']:20} = ERROR")
    
    print("\n" + "=" * 80)
    print("検証完了")
    print("=" * 80)
    
    return len(errors) == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
