# -*- coding: utf-8 -*-
"""
Retail Sales データ取得テスト
FREDから直接RetailSalesデータを取得できるかテスト
"""
import os
from dotenv import load_dotenv
from fredapi import Fred
import datetime

load_dotenv()

FRED_API_KEY = os.getenv('FRED_API_KEY')
if not FRED_API_KEY:
    print("❌ FRED_API_KEY not found in .env")
    exit(1)

print("=" * 60)
print("Retail Sales (RSAFS) データ取得テスト")
print("=" * 60)

fred = Fred(api_key=FRED_API_KEY)

try:
    print("\n📊 RSAFS (Retail Sales) を取得中...")
    data = fred.get_series('RSAFS', observation_start='2024-01-01')
    
    if data is not None and len(data) > 0:
        print(f"✅ データ取得成功！")
        print(f"   データ数: {len(data)}")
        print(f"   最新日付: {data.index[-1]}")
        print(f"   最新値: {data.iloc[-1]:,.1f}")
        print(f"\n最近のデータ:")
        print(data.tail(5))
    else:
        print("❌ データが空です")
        
except Exception as e:
    print(f"❌ エラー: {str(e)}")

print("\n" + "=" * 60)

# PPIもテスト
print("\n📊 PPIACO (PPI) を取得中...")
try:
    data_ppi = fred.get_series('PPIACO', observation_start='2024-01-01')
    
    if data_ppi is not None and len(data_ppi) > 0:
        print(f"✅ データ取得成功！")
        print(f"   データ数: {len(data_ppi)}")
        print(f"   最新日付: {data_ppi.index[-1]}")
        print(f"   最新値: {data_ppi.iloc[-1]:.2f}")
        print(f"\n最近のデータ:")
        print(data_ppi.tail(5))
    else:
        print("❌ データが空です")
        
except Exception as e:
    print(f"❌ エラー: {str(e)}")

print("\n" + "=" * 60)
print("診断完了")
print("=" * 60)
