# -*- coding: utf-8 -*-
"""
診断スクリプト: データ取得状況の確認
実行方法: streamlit run market_app_nav.py を起動後、データ取得ログを確認
または、このスクリプトを単独実行してFRED APIテスト
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.indicators import INDICATORS
import pandas as pd

def test_fred_api():
    """Test FRED API for specific indicators"""
    from fredapi import Fred
    
    fred_api_key = os.getenv('FRED_API_KEY')
    if not fred_api_key:
        print("❌ FRED_API_KEY not found in .env")
        return
    
    fred = Fred(api_key=fred_api_key)
    
    # Test indicators
    test_indicators = {
        'RetailSales': 'RSAFS',
        'PPI': 'PPIACO',
        'ISM_PMI': 'NAPM',
        'Leading_Index': 'USSLIND',
        'Housing_Starts': 'HOUST',
        'Building_Permits': 'PERMIT',
    }
    
    print("=" * 80)
    print("FRED API テスト")
    print("=" * 80)
    
    for name, series_id in test_indicators.items():
        try:
            data = fred.get_series(series_id, observation_start='2024-01-01')
            if data is not None and len(data) > 0:
                latest = data.iloc[-1]
                latest_date = data.index[-1]
                print(f"✅ {name} ({series_id})")
                print(f"   Latest: {latest:.2f} ({latest_date})")
                print(f"   Data points: {len(data)}")
            else:
                print(f"⚠️  {name} ({series_id}) - データなし")
        except Exception as e:
            print(f"❌ {name} ({series_id}) - エラー: {str(e)}")
        print()

def check_indicator_definitions():
    """Check indicator definitions in indicators.py"""
    print("=" * 80)
    print("US Economic Data 指標定義チェック")
    print("=" * 80)
    
    us_econ_indicators = {k: v for k, v in INDICATORS.items() 
                          if v.get('ui_page') == '03_us_economic'}
    
    print(f"\n合計: {len(us_econ_indicators)} 指標\n")
    
    for name, info in sorted(us_econ_indicators.items()):
        source = info.get('source', '?')
        series_id = info.get('id', '?')
        category = info.get('category', '?')
        notes = info.get('notes', '?')
        print(f"📊 {name}")
        print(f"   Source: {source} | ID: {series_id}")
        print(f"   Category: {category}")
        print(f"   Notes: {notes}")
        print()

def main():
    """Run all diagnostics"""
    print("\n")
    print("🔍 Market Cockpit Pro - データ取得診断")
    print()
    
    # 1. Check indicator definitions
    check_indicator_definitions()
    
    # 2. Test FRED API
    test_fred_api()
    
    print("=" * 80)
    print("診断完了")
    print("=" * 80)

if __name__ == '__main__':
    main()
