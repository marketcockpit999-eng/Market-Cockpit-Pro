"""
地方連銀製造業指数の合成検証スクリプト

目的: 5連銀の製造業指数を合成し、ISM製造業PMIとの相関を検証
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fredapi import Fred

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 既存のconfig.pyからAPIキー取得
from utils.config import FRED_API_KEY

# ============================================================
# FRED系列ID定義
# ============================================================

# 地方連銀製造業指数（General Activity / Diffusion Index）
# NOTE: Richmond Fed is web-scraped, not available on FRED
REGIONAL_FED_SERIES = {
    'NY Empire State': {
        'candidates': ['GACDISA066MSFRBNY'],  # General Business Conditions (Seasonally Adjusted)
        'description': 'NY Fed Empire State Manufacturing Survey'
    },
    'Philadelphia': {
        'candidates': ['GACDFSA066MSFRBPHI'],  # General Activity (Seasonally Adjusted)
        'description': 'Philadelphia Fed Manufacturing Index'
    },
    'Dallas': {
        'candidates': ['BACTSAMFRBDAL'],  # Business Activity (Seasonally Adjusted) - CORRECT ID
        'description': 'Dallas Fed Manufacturing Index'
    }
    # NOTE: Richmond Fed and Kansas City Fed are NOT available on FRED
    # Richmond is web-scraped in Market Cockpit Pro
    # Kansas City discontinued their manufacturing survey
}

# ISM製造業PMI
ISM_SERIES = {
    'candidates': ['MANEMP', 'NAPM'],  # ISM Manufacturing PMI (NAPM discontinued, try MANEMP first)
    'description': 'ISM Manufacturing PMI'
}


def get_fred_data(fred: Fred, series_id: str, start_date: str = '2000-01-01') -> pd.Series:
    """FREDからデータを取得"""
    try:
        data = fred.get_series(series_id, observation_start=start_date)
        if data is not None and len(data) > 0:
            print(f"  [OK] {series_id}: {len(data)} data points ({data.index[0].strftime('%Y-%m')} to {data.index[-1].strftime('%Y-%m')})")
            return data
    except Exception as e:
        print(f"  [X] {series_id}: {e}")
    return None


def fetch_regional_fed_data(fred: Fred) -> dict:
    """地方連銀データを取得"""
    print("\n" + "="*60)
    print("Step 1: 地方連銀製造業指数の取得")
    print("="*60)
    
    results = {}
    
    for name, config in REGIONAL_FED_SERIES.items():
        print(f"\n{name}:")
        for series_id in config['candidates']:
            data = get_fred_data(fred, series_id)
            if data is not None:
                results[name] = {
                    'series_id': series_id,
                    'data': data
                }
                break
        
        if name not in results:
            print(f"  [WARNING] データ取得失敗")
    
    return results


def fetch_ism_data(fred: Fred) -> pd.Series:
    """ISM製造業PMIを取得"""
    print("\n" + "="*60)
    print("Step 2: ISM製造業PMIの取得")
    print("="*60)
    
    for series_id in ISM_SERIES['candidates']:
        data = get_fred_data(fred, series_id)
        if data is not None:
            return data
    
    print("  [WARNING] ISMデータ取得失敗")
    return None


def create_composite_index(regional_data: dict) -> pd.Series:
    """合成指標を作成（単純平均）"""
    print("\n" + "="*60)
    print("Step 3: 合成指標の作成")
    print("="*60)
    
    # DataFrameに変換
    df = pd.DataFrame()
    for name, info in regional_data.items():
        df[name] = info['data']
    
    # 月次にリサンプリング（月末）
    df_monthly = df.resample('ME').last()
    
    # 欠損値の確認
    print(f"\n各連銀のデータ期間:")
    for col in df_monthly.columns:
        valid = df_monthly[col].dropna()
        if len(valid) > 0:
            print(f"  {col}: {valid.index[0].strftime('%Y-%m')} to {valid.index[-1].strftime('%Y-%m')} ({len(valid)} months)")
    
    # 単純平均を計算（最低2連銀のデータがある月のみ）
    min_count = 2
    composite = df_monthly.mean(axis=1, skipna=True)
    valid_count = df_monthly.notna().sum(axis=1)
    composite = composite.where(valid_count >= min_count)
    
    print(f"\n合成指標:")
    valid_composite = composite.dropna()
    print(f"  期間: {valid_composite.index[0].strftime('%Y-%m')} to {valid_composite.index[-1].strftime('%Y-%m')}")
    print(f"  データ点数: {len(valid_composite)}")
    print(f"  平均: {valid_composite.mean():.2f}")
    print(f"  標準偏差: {valid_composite.std():.2f}")
    print(f"  最小: {valid_composite.min():.2f}")
    print(f"  最大: {valid_composite.max():.2f}")
    
    return composite


def analyze_correlation(composite: pd.Series, ism: pd.Series) -> dict:
    """相関分析"""
    print("\n" + "="*60)
    print("Step 4: 相関分析")
    print("="*60)
    
    # ISMも月次にリサンプリング
    ism_monthly = ism.resample('ME').last()
    
    # 共通期間で揃える
    df = pd.DataFrame({
        'Composite': composite,
        'ISM': ism_monthly
    }).dropna()
    
    print(f"\n共通期間: {df.index[0].strftime('%Y-%m')} to {df.index[-1].strftime('%Y-%m')}")
    print(f"データ点数: {len(df)}")
    
    # 相関係数を計算
    correlation = df['Composite'].corr(df['ISM'])
    
    print(f"\n【相関係数】: {correlation:.4f}")
    
    # 解釈
    if correlation >= 0.7:
        interpretation = "★★★ 強い相関 - 合成指標は十分信頼できる"
    elif correlation >= 0.5:
        interpretation = "★★☆ 中程度の相関 - 参考指標として有用"
    else:
        interpretation = "★☆☆ 弱い相関 - 合成の意味が薄い可能性"
    
    print(f"\n【解釈】: {interpretation}")
    
    # 追加分析：ラグ相関
    print(f"\n【ラグ相関分析】:")
    for lag in range(-3, 4):
        if lag < 0:
            shifted_ism = df['ISM'].shift(lag)
            lag_corr = df['Composite'].corr(shifted_ism)
            print(f"  Composite vs ISM (ISM {abs(lag)}ヶ月先行): {lag_corr:.4f}")
        elif lag > 0:
            shifted_composite = df['Composite'].shift(lag)
            lag_corr = shifted_composite.corr(df['ISM'])
            print(f"  Composite vs ISM (Composite {lag}ヶ月先行): {lag_corr:.4f}")
        else:
            print(f"  Composite vs ISM (同時): {correlation:.4f}")
    
    return {
        'correlation': correlation,
        'interpretation': interpretation,
        'data': df
    }


def create_visualization(composite: pd.Series, ism: pd.Series, 
                        regional_data: dict, analysis_result: dict):
    """可視化"""
    print("\n" + "="*60)
    print("Step 5: チャート作成")
    print("="*60)
    
    # ISMを月次にリサンプリング
    ism_monthly = ism.resample('ME').last()
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # --- Chart 1: 合成指標 vs ISM ---
    ax1 = axes[0]
    ax1.plot(composite.index, composite.values, 'b-', linewidth=2, label='Regional Fed Composite (3 Banks Avg)', alpha=0.9)
    ax1.plot(ism_monthly.index, ism_monthly.values, 'r-', linewidth=2, label='ISM Manufacturing PMI', alpha=0.9)
    ax1.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='Expansion/Contraction Line (50)')
    ax1.axhline(y=0, color='gray', linestyle=':', alpha=0.5, label='Zero Line (Regional Fed)')
    ax1.set_title(f'Regional Fed Composite vs ISM Manufacturing PMI\nCorrelation: {analysis_result["correlation"]:.4f}', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Index Value')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    
    # --- Chart 2: 各地方連銀の時系列 ---
    ax2 = axes[1]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for i, (name, info) in enumerate(regional_data.items()):
        data = info['data'].resample('ME').last()
        ax2.plot(data.index, data.values, color=colors[i], linewidth=1.5, label=name, alpha=0.7)
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax2.set_title('Individual Regional Fed Manufacturing Indices', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Index Value')
    ax2.legend(loc='upper left', ncol=2)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator(2))
    
    # --- Chart 3: 散布図 ---
    ax3 = axes[2]
    df = analysis_result['data']
    ax3.scatter(df['Composite'], df['ISM'], alpha=0.5, s=20)
    
    # 回帰直線
    z = np.polyfit(df['Composite'].values, df['ISM'].values, 1)
    p = np.poly1d(z)
    x_line = np.linspace(df['Composite'].min(), df['Composite'].max(), 100)
    ax3.plot(x_line, p(x_line), 'r--', linewidth=2, label=f'Linear Fit: y = {z[0]:.2f}x + {z[1]:.2f}')
    
    ax3.set_xlabel('Regional Fed Composite')
    ax3.set_ylabel('ISM Manufacturing PMI')
    ax3.set_title('Scatter Plot: Regional Fed Composite vs ISM PMI', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存
    output_path = Path(__file__).parent / 'regional_fed_composite_chart.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nチャート保存: {output_path}")
    
    # plt.show()  # Disabled to prevent hanging in non-interactive mode
    plt.close()


def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("地方連銀製造業指数 合成検証スクリプト")
    print("="*60)
    
    # FRED API接続
    if not FRED_API_KEY:
        print("エラー: FRED_API_KEYが設定されていません")
        return
    
    fred = Fred(api_key=FRED_API_KEY)
    print(f"FRED API接続OK")
    
    # Step 1: 地方連銀データ取得
    regional_data = fetch_regional_fed_data(fred)
    
    if len(regional_data) < 2:
        print("\n[WARNING] 十分な地方連銀データを取得できませんでした（最低2行必要）")
        print("FRED系列IDを確認してください")
        return
    
    print(f"\n取得成功: {len(regional_data)}/3 連銀（NY, Philly, Dallas）")
    
    # Step 2: ISMデータ取得
    ism_data = fetch_ism_data(fred)
    
    if ism_data is None:
        print("\n[WARNING] ISMデータを取得できませんでした")
        return
    
    # Step 3: 合成指標作成
    composite = create_composite_index(regional_data)
    
    # Step 4: 相関分析
    analysis_result = analyze_correlation(composite, ism_data)
    
    # Step 5: 可視化
    create_visualization(composite, ism_data, regional_data, analysis_result)
    
    # 結論
    print("\n" + "="*60)
    print("【結論】")
    print("="*60)
    print(f"\n相関係数: {analysis_result['correlation']:.4f}")
    print(f"解釈: {analysis_result['interpretation']}")
    
    if analysis_result['correlation'] >= 0.5:
        print("\n→ Market Cockpitへの実装を推奨")
        print("  地方連銀合成指標は、ISMの補完/先行指標として価値あり")
    else:
        print("\n→ 実装は保留")
        print("  個別の地方連銀指標を表示する方が良い可能性")


if __name__ == '__main__':
    main()
