# -*- coding: utf-8 -*-
"""
Global M2 計算修正のテストスクリプト
実行: python test_global_m2_fix.py
"""

import pickle
import pandas as pd
import numpy as np
import os

CACHE_FILE = '.market_data_cache.pkl'

def test_global_m2_calculation():
    """キャッシュからデータを読み込み、修正前後のGlobal M2を比較"""
    
    if not os.path.exists(CACHE_FILE):
        print("❌ キャッシュファイルが見つかりません")
        print("   アプリを一度起動してデータを取得してください")
        return
    
    # Load cache
    with open(CACHE_FILE, 'rb') as f:
        data = pickle.load(f)
    
    df_original = data.get('df_original')
    if df_original is None:
        print("❌ df_original がキャッシュにありません")
        return
    
    df = df_original.copy()
    
    # Check required columns
    required_cols = ['M2SL', 'CN_M2', 'JP_M2', 'EU_M2', 'USDCNY', 'USDJPY', 'EURUSD']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"❌ 必要なカラムがありません: {missing}")
        return
    
    print("="*60)
    print("Global M2 計算テスト")
    print("="*60)
    
    # === OLD METHOD (without smoothing) ===
    cn_m2_usd_old = df['CN_M2'].ffill().bfill() / df['USDCNY'].ffill().bfill()
    jp_m2_usd_old = df['JP_M2'].ffill().bfill() / df['USDJPY'].ffill().bfill()
    eu_m2_usd_old = df['EU_M2'].ffill().bfill() * df['EURUSD'].ffill().bfill()
    us_m2 = df['M2SL'].ffill()
    global_m2_old = (us_m2 + cn_m2_usd_old + jp_m2_usd_old + eu_m2_usd_old).ffill()
    
    # === NEW METHOD (with 30-day rolling average) ===
    usdcny_smooth = df['USDCNY'].ffill().rolling(window=30, min_periods=1).mean()
    usdjpy_smooth = df['USDJPY'].ffill().rolling(window=30, min_periods=1).mean()
    eurusd_smooth = df['EURUSD'].ffill().rolling(window=30, min_periods=1).mean()
    
    cn_m2_usd_new = df['CN_M2'].ffill().bfill() / usdcny_smooth.bfill()
    jp_m2_usd_new = df['JP_M2'].ffill().bfill() / usdjpy_smooth.bfill()
    eu_m2_usd_new = df['EU_M2'].ffill().bfill() * eurusd_smooth.bfill()
    global_m2_new = (us_m2 + cn_m2_usd_new + jp_m2_usd_new + eu_m2_usd_new).ffill()
    
    # === Compare last 90 days ===
    print("\n📊 直近90日間の比較:")
    print("-"*60)
    
    comparison = pd.DataFrame({
        'OLD': global_m2_old,
        'NEW': global_m2_new,
        'DIFF': global_m2_new - global_m2_old,
        'DIFF%': ((global_m2_new - global_m2_old) / global_m2_old * 100)
    }).dropna().tail(90)
    
    # Show volatility (standard deviation of daily changes)
    old_daily_change = global_m2_old.diff().dropna().tail(90)
    new_daily_change = global_m2_new.diff().dropna().tail(90)
    
    print(f"旧方式 日次変動の標準偏差: {old_daily_change.std():.4f}T")
    print(f"新方式 日次変動の標準偏差: {new_daily_change.std():.4f}T")
    print(f"ボラティリティ削減: {(1 - new_daily_change.std()/old_daily_change.std())*100:.1f}%")
    
    # Show max daily swing
    print(f"\n旧方式 最大日次変動: {old_daily_change.abs().max():.4f}T")
    print(f"新方式 最大日次変動: {new_daily_change.abs().max():.4f}T")
    
    # Show last 5 values
    print("\n📈 直近5日間の値:")
    print("-"*60)
    print(comparison[['OLD', 'NEW', 'DIFF%']].tail(5).to_string())
    
    # Check for sudden drops (>1T change in a day)
    old_sudden_drops = (old_daily_change.abs() > 1).sum()
    new_sudden_drops = (new_daily_change.abs() > 1).sum()
    
    print(f"\n⚠️ 急激な変動 (>1T/日):")
    print(f"   旧方式: {old_sudden_drops} 回")
    print(f"   新方式: {new_sudden_drops} 回")
    
    if new_sudden_drops < old_sudden_drops:
        print("\n✅ 修正成功: 急激な変動が減少しました")
    elif new_sudden_drops == 0 and old_sudden_drops == 0:
        print("\n✅ 両方式とも急激な変動なし")
    else:
        print("\n⚠️ 要確認: 変動パターンを確認してください")
    
    print("\n" + "="*60)
    print("テスト完了")
    print("="*60)

if __name__ == '__main__':
    test_global_m2_calculation()
