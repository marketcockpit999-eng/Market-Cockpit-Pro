"""
地方連銀製造業指数の合成検証スクリプト v2

修正点:
- ISM PMIの正しい系列ID (NAPM → ISMではなくMANEMPだった)
- ISM PMIはFREDに直接ないため、代替としてChicago Fed NAIを使用
- または、既存データソースからISM PMIを取得
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
import yfinance as yf

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# .envファイルからAPIキー取得
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

FRED_API_KEY = os.getenv('FRED_API_KEY')

# ============================================================
# FRED系列ID定義（修正版）
# ============================================================

# 地方連銀製造業指数
# 参考: https://fred.stlouisfed.org/tags/series?t=manufacturing%3Bsurvey
REGIONAL_FED_SERIES = {
    'NY Empire State': {
        'series_id': 'GACDISA066MSFRBNY',  # Empire State General Business Conditions
        'description': 'NY Fed Empire State Manufacturing Survey'
    },
    'Philadelphia': {
        'series_id': 'GACDFSA066MSFRBPHI',  # Philly Fed Diffusion Index
        'description': 'Philadelphia Fed Manufacturing Index'
    },
    'Richmond': {
        'series_id': 'RICSMPFC',  # Richmond Fed Manufacturing - Composite Index
        'description': 'Richmond Fed Manufacturing Composite'
    },
    'Kansas City': {
        'series_id': 'KCFSI',  # KC Fed - これは金融ストレス。製造業は別
        'alt_id': 'KANSASPHFFMI',  # 試してみる
        'description': 'Kansas City Fed Manufacturing Index'
    },
    'Dallas': {
        'series_id': 'DXRDFSA066MSFRBDAL',  # Dallas Fed General Business Activity
        'description': 'Dallas Fed Manufacturing Index'
    }
}

# 比較対象: Chicago Fed National Activity Index (製造業関連の全国指標)
# ISM PMIはFREDにないため、CFNAIの製造業成分または全体を使用
COMPARISON_SERIES = {
    'CFNAI': {
        'series_id': 'CFNAI',  # Chicago Fed National Activity Index
        'description': 'Chicago Fed National Activity Index (Overall)'
    },
    'CFNAI_Production': {
        'series_id': 'PCEDG',  # 代替：これは違う。Industrial Productionを使おう
        'description': 'Production component'
    },
    'Industrial_Production': {
        'series_id': 'INDPRO',  # Industrial Production Index
        'description': 'Industrial Production Index'
    }
}


def get_fred_data(fred: Fred, series_id: str, start_date: str = '2000-01-01') -> pd.Series:
    """FREDからデータを取得"""
    try:
        data = fred.get_series(series_id, observation_start=start_date)
        if data is not None and len(data) > 0:
            print(f"  ✓ {series_id}: {len(data)} points, range [{data.min():.1f}, {data.max():.1f}]")
            return data
    except Exception as e:
        print(f"  ✗ {series_id}: {e}")
    return None


def search_fred_series(fred: Fred, search_term: str, limit: int = 10):
    """FREDで系列を検索"""
    print(f"\nSearching FRED for: '{search_term}'")
    try:
        results = fred.search(search_term, limit=limit)
        if results is not None and len(results) > 0:
            print(f"Found {len(results)} series:")
            for idx, row in results.head(limit).iterrows():
                print(f"  {idx}: {row.get('title', 'N/A')[:60]}")
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return None


def fetch_regional_fed_data(fred: Fred) -> dict:
    """地方連銀データを取得"""
    print("\n" + "="*60)
    print("Step 1: 地方連銀製造業指数の取得")
    print("="*60)
    
    results = {}
    
    # まずNY, Philly, Dallasを取得（確実に動くはず）
    for name in ['NY Empire State', 'Philadelphia', 'Dallas']:
        config = REGIONAL_FED_SERIES[name]
        print(f"\n{name}:")
        data = get_fred_data(fred, config['series_id'])
        if data is not None:
            results[name] = {
                'series_id': config['series_id'],
                'data': data
            }
    
    # Richmond - 別の系列を試す
    print(f"\nRichmond:")
    richmond_candidates = ['RICSMPFC', 'RICDFSA066MSFRBRIC', 'RSXFS']
    for series_id in richmond_candidates:
        data = get_fred_data(fred, series_id)
        if data is not None:
            results['Richmond'] = {'series_id': series_id, 'data': data}
            break
    
    # Kansas City - 別の系列を試す
    print(f"\nKansas City:")
    kc_candidates = ['FRBKCCOMPMFG', 'GACDFSA066MSFRBKC', 'KCFSI']
    for series_id in kc_candidates:
        data = get_fred_data(fred, series_id)
        if data is not None:
            # KCFSIは金融ストレス指数なのでスキップ
            if series_id == 'KCFSI':
                print(f"    (KCFSI is Financial Stress Index, skipping)")
                continue
            results['Kansas City'] = {'series_id': series_id, 'data': data}
            break
    
    return results


def fetch_ism_pmi_proxy(fred: Fred) -> tuple:
    """
    ISM PMIの代替指標を取得
    
    ISM PMI自体はFREDにないため、以下で代替:
    1. Chicago Fed National Activity Index (CFNAI) - 全米の経済活動
    2. Industrial Production MoM% change - 製造業生産
    """
    print("\n" + "="*60)
    print("Step 2: 比較指標の取得")
    print("="*60)
    
    print("\n注意: ISM PMIはFREDに直接収録されていません")
    print("代替として Chicago Fed National Activity Index (CFNAI) を使用します")
    print("CFNAIは85の経済指標から構成され、0を平均として変動します\n")
    
    # CFNAI取得
    cfnai = get_fred_data(fred, 'CFNAI')
    
    # 参考: Industrial Production (YoY変化率に変換)
    indpro = get_fred_data(fred, 'INDPRO')
    if indpro is not None:
        indpro_yoy = indpro.pct_change(12) * 100  # 12ヶ月変化率
        print(f"  Industrial Production YoY: range [{indpro_yoy.min():.1f}%, {indpro_yoy.max():.1f}%]")
    else:
        indpro_yoy = None
    
    return cfnai, indpro_yoy


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
    
    # 単純平均を計算（最低2連銀のデータがある月）
    min_count = 2
    composite = df_monthly.mean(axis=1, skipna=True)
    valid_count = df_monthly.notna().sum(axis=1)
    composite = composite.where(valid_count >= min_count)
    
    print(f"\n合成指標 ({len(regional_data)}連銀平均):")
    valid_composite = composite.dropna()
    if len(valid_composite) > 0:
        print(f"  期間: {valid_composite.index[0].strftime('%Y-%m')} to {valid_composite.index[-1].strftime('%Y-%m')}")
        print(f"  データ点数: {len(valid_composite)}")
        print(f"  平均: {valid_composite.mean():.2f}")
        print(f"  標準偏差: {valid_composite.std():.2f}")
        print(f"  範囲: [{valid_composite.min():.2f}, {valid_composite.max():.2f}]")
    
    return composite


def analyze_correlation(composite: pd.Series, cfnai: pd.Series, indpro_yoy: pd.Series) -> dict:
    """相関分析"""
    print("\n" + "="*60)
    print("Step 4: 相関分析")
    print("="*60)
    
    results = {}
    
    # CFNAI（月次）
    cfnai_monthly = cfnai.resample('ME').last() if cfnai is not None else None
    
    # Industrial Production YoY（月次）
    indpro_monthly = indpro_yoy.resample('ME').last() if indpro_yoy is not None else None
    
    # --- CFNAI との相関 ---
    if cfnai_monthly is not None:
        df_cfnai = pd.DataFrame({
            'Composite': composite,
            'CFNAI': cfnai_monthly
        }).dropna()
        
        if len(df_cfnai) > 10:
            corr_cfnai = df_cfnai['Composite'].corr(df_cfnai['CFNAI'])
            print(f"\n【Regional Fed Composite vs CFNAI】")
            print(f"  共通期間: {df_cfnai.index[0].strftime('%Y-%m')} to {df_cfnai.index[-1].strftime('%Y-%m')}")
            print(f"  データ点数: {len(df_cfnai)}")
            print(f"  相関係数: {corr_cfnai:.4f}")
            results['cfnai'] = {'correlation': corr_cfnai, 'data': df_cfnai}
    
    # --- Industrial Production YoY との相関 ---
    if indpro_monthly is not None:
        df_indpro = pd.DataFrame({
            'Composite': composite,
            'INDPRO_YoY': indpro_monthly
        }).dropna()
        
        if len(df_indpro) > 10:
            corr_indpro = df_indpro['Composite'].corr(df_indpro['INDPRO_YoY'])
            print(f"\n【Regional Fed Composite vs Industrial Production YoY】")
            print(f"  共通期間: {df_indpro.index[0].strftime('%Y-%m')} to {df_indpro.index[-1].strftime('%Y-%m')}")
            print(f"  データ点数: {len(df_indpro)}")
            print(f"  相関係数: {corr_indpro:.4f}")
            results['indpro'] = {'correlation': corr_indpro, 'data': df_indpro}
    
    # 解釈
    print(f"\n【相関の解釈】")
    print(f"  0.7以上: 強い相関 → 合成指標は信頼できる")
    print(f"  0.5-0.7: 中程度 → 参考指標として有用")
    print(f"  0.5未満: 弱い → 独自の情報を持つ可能性")
    
    return results


def create_visualization(composite: pd.Series, cfnai: pd.Series, 
                        indpro_yoy: pd.Series, regional_data: dict, 
                        analysis_results: dict):
    """可視化"""
    print("\n" + "="*60)
    print("Step 5: チャート作成")
    print("="*60)
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # --- Chart 1: 合成指標 vs CFNAI ---
    ax1 = axes[0]
    
    # 合成指標（左軸）
    color1 = 'tab:blue'
    ax1.set_ylabel('Regional Fed Composite', color=color1)
    ax1.plot(composite.index, composite.values, color=color1, linewidth=2, 
             label=f'Regional Fed Composite ({len(regional_data)} Banks Avg)')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    
    # CFNAI（右軸）
    if cfnai is not None:
        ax1_r = ax1.twinx()
        color2 = 'tab:red'
        ax1_r.set_ylabel('CFNAI', color=color2)
        cfnai_monthly = cfnai.resample('ME').last()
        ax1_r.plot(cfnai_monthly.index, cfnai_monthly.values, color=color2, 
                   linewidth=2, label='Chicago Fed NAI', alpha=0.8)
        ax1_r.tick_params(axis='y', labelcolor=color2)
        ax1_r.axhline(y=0, color=color2, linestyle=':', alpha=0.3)
    
    corr_str = f"{analysis_results.get('cfnai', {}).get('correlation', 0):.3f}" if 'cfnai' in analysis_results else 'N/A'
    ax1.set_title(f'Regional Fed Composite vs Chicago Fed NAI\nCorrelation: {corr_str}', 
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    
    # レジェンド
    lines1, labels1 = ax1.get_legend_handles_labels()
    if cfnai is not None:
        lines2, labels2 = ax1_r.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    else:
        ax1.legend(loc='upper left')
    
    # --- Chart 2: 各地方連銀の時系列 ---
    ax2 = axes[1]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for i, (name, info) in enumerate(regional_data.items()):
        data = info['data'].resample('ME').last()
        ax2.plot(data.index, data.values, color=colors[i % len(colors)], 
                 linewidth=1.5, label=f"{name} ({info['series_id']})", alpha=0.7)
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax2.set_title('Individual Regional Fed Manufacturing Indices', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Index Value (0 = neutral)')
    ax2.legend(loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax2.xaxis.set_major_locator(mdates.YearLocator(2))
    
    # --- Chart 3: 散布図 (Composite vs CFNAI) ---
    ax3 = axes[2]
    if 'cfnai' in analysis_results:
        df = analysis_results['cfnai']['data']
        ax3.scatter(df['Composite'], df['CFNAI'], alpha=0.5, s=20)
        
        # 回帰直線
        z = np.polyfit(df['Composite'].values, df['CFNAI'].values, 1)
        p = np.poly1d(z)
        x_line = np.linspace(df['Composite'].min(), df['Composite'].max(), 100)
        ax3.plot(x_line, p(x_line), 'r--', linewidth=2, 
                 label=f'Linear Fit: y = {z[0]:.3f}x + {z[1]:.3f}')
        
        ax3.set_xlabel('Regional Fed Composite')
        ax3.set_ylabel('Chicago Fed NAI')
        ax3.set_title('Scatter Plot: Regional Fed Composite vs CFNAI', fontsize=14, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
        ax3.axvline(x=0, color='gray', linestyle=':', alpha=0.5)
    else:
        ax3.text(0.5, 0.5, 'Insufficient data for scatter plot', 
                 ha='center', va='center', transform=ax3.transAxes)
    
    plt.tight_layout()
    
    # 保存
    output_path = Path(__file__).parent / 'regional_fed_composite_chart_v2.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nチャート保存: {output_path}")
    
    plt.show()


def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("地方連銀製造業指数 合成検証スクリプト v2")
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
        print("\n⚠ 十分な地方連銀データを取得できませんでした")
        return
    
    print(f"\n取得成功: {len(regional_data)}/5 連銀")
    for name, info in regional_data.items():
        print(f"  {name}: {info['series_id']}")
    
    # Step 2: 比較指標取得
    cfnai, indpro_yoy = fetch_ism_pmi_proxy(fred)
    
    # Step 3: 合成指標作成
    composite = create_composite_index(regional_data)
    
    # Step 4: 相関分析
    analysis_results = analyze_correlation(composite, cfnai, indpro_yoy)
    
    # Step 5: 可視化
    create_visualization(composite, cfnai, indpro_yoy, regional_data, analysis_results)
    
    # 結論
    print("\n" + "="*60)
    print("【結論】")
    print("="*60)
    
    if 'cfnai' in analysis_results:
        corr = analysis_results['cfnai']['correlation']
        print(f"\n相関係数 (vs CFNAI): {corr:.4f}")
        
        if corr >= 0.7:
            print("★★★ 強い相関 - 合成指標は全米経済活動と連動")
        elif corr >= 0.5:
            print("★★☆ 中程度の相関 - 参考指標として有用")
        elif corr >= 0.3:
            print("★☆☆ 弱〜中程度 - 独自の情報を含む可能性")
        else:
            print("☆☆☆ 弱い相関 - 地域特有の動きを捉えている")
    
    if 'indpro' in analysis_results:
        corr = analysis_results['indpro']['correlation']
        print(f"相関係数 (vs Industrial Production YoY): {corr:.4f}")
    
    print("\n【次のステップ】")
    print("1. 相関が高い場合: Market Cockpitの「US Economic」タブに合成指標を追加")
    print("2. 相関が中程度の場合: 先行指標としての価値を検証（ラグ相関分析）")
    print("3. 相関が低い場合: 個別連銀の表示を検討、または地域特化分析に活用")


if __name__ == '__main__':
    main()
