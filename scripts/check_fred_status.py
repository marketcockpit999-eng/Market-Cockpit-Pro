# -*- coding: utf-8 -*-
"""
FRED Series Status Checker
===========================
FREDシリーズの詳細メタデータを確認するスクリプト
（DISCONTINUEDステータス、リリース日、最終更新日など）

使い方:
    cd C:/Users/81802/.gemini/antigravity/scratch/market_monitor
    python scripts/check_fred_status.py

Note: fredapiパッケージを使用（pip install fredapi）
"""

import datetime
import sys
import os
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.indicators import INDICATORS

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"

def get_series_info(series_id):
    """FRED APIから直接シリーズ情報を取得"""
    url = f"https://api.stlouisfed.org/fred/series"
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if 'seriess' in data and len(data['seriess']) > 0:
                return data['seriess'][0]
        elif response.status_code == 404:
            return {'error': 'Series not found'}
        else:
            return {'error': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'error': str(e)}


def check_all_series():
    """全FREDシリーズのステータスをチェック"""
    print("=" * 90)
    print("FRED Series Status Report")
    print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)
    
    # FREDソースの指標のみ
    fred_indicators = {k: v for k, v in INDICATORS.items() if v['source'] == 'FRED'}
    
    discontinued = []
    not_found = []
    active = []
    
    for name, info in fred_indicators.items():
        series_id = info['id']
        print(f"Checking {name} ({series_id})...", end=" ")
        
        info_data = get_series_info(series_id)
        
        if 'error' in info_data:
            print(f"[X] {info_data['error']}")
            not_found.append({
                'name': name,
                'id': series_id,
                'error': info_data['error'],
                'notes': info.get('notes', '')
            })
        else:
            title = info_data.get('title', 'N/A')
            last_updated = info_data.get('last_updated', 'N/A')
            observation_start = info_data.get('observation_start', 'N/A')
            observation_end = info_data.get('observation_end', 'N/A')
            notes = info_data.get('notes', '')
            
            # DISCONTINUEDチェック
            is_discontinued = 'DISCONTINUED' in title.upper() or 'DISCONTINUED' in notes.upper()
            
            if is_discontinued:
                print(f"[!] DISCONTINUED - {title[:50]}")
                discontinued.append({
                    'name': name,
                    'id': series_id,
                    'title': title,
                    'observation_end': observation_end,
                    'app_notes': info.get('notes', '')
                })
            else:
                print(f"[OK] Active (ends {observation_end})")
                active.append({
                    'name': name,
                    'id': series_id,
                    'title': title,
                    'observation_end': observation_end
                })
    
    # サマリー
    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)
    print(f"Total FRED indicators: {len(fred_indicators)}")
    print(f"[OK] Active: {len(active)}")
    print(f"[!] Discontinued: {len(discontinued)}")
    print(f"[X] Not found/Error: {len(not_found)}")
    
    if discontinued:
        print("\n" + "-" * 50)
        print("DISCONTINUED SERIES (需要代替ID検討)")
        print("-" * 50)
        for item in discontinued:
            print(f"\n{item['name']} ({item['id']}):")
            print(f"  FRED Title: {item['title'][:80]}")
            print(f"  Last data: {item['observation_end']}")
            print(f"  App notes: {item['app_notes']}")
    
    if not_found:
        print("\n" + "-" * 50)
        print("NOT FOUND / ERROR (要緊急対応)")
        print("-" * 50)
        for item in not_found:
            print(f"\n{item['name']} ({item['id']}):")
            print(f"  Error: {item['error']}")
            print(f"  App notes: {item['notes']}")
    
    # 最終データ日付チェック（古いデータ警告）
    print("\n" + "-" * 50)
    print("DATA FRESHNESS CHECK")
    print("-" * 50)
    today = datetime.date.today()
    stale_items = []
    for item in active:
        try:
            end_date = datetime.datetime.strptime(item['observation_end'], '%Y-%m-%d').date()
            days_old = (today - end_date).days
            if days_old > 30:  # 30日以上古い
                stale_items.append({
                    'name': item['name'],
                    'id': item['id'],
                    'observation_end': item['observation_end'],
                    'days_old': days_old
                })
        except:
            pass
    
    if stale_items:
        stale_items.sort(key=lambda x: x['days_old'], reverse=True)
        print(f"[!] {len(stale_items)} series with data older than 30 days:")
        for item in stale_items[:15]:  # Top 15
            print(f"  {item['name']:20} {item['id']:20} - Last: {item['observation_end']} ({item['days_old']} days)")
    else:
        print("[OK] All series have recent data")
    
    print("\n" + "=" * 90)
    print("チェック完了")
    print("=" * 90)
    
    return len(discontinued) == 0 and len(not_found) == 0


if __name__ == '__main__':
    success = check_all_series()
    sys.exit(0 if success else 1)
