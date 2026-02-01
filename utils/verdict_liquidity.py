# -*- coding: utf-8 -*-
"""
MARKET VERDICT - Liquidity Score Calculator
================================================================================
流動性スコア（0-100）を計算するモジュール

スコア構成:
  - Net Liquidity パーセンタイル × 50%
  - Reserves パーセンタイル × 30%
  - M2 YoY変化率スコア × 20%

使用方法:
  from utils.verdict_liquidity import calculate_liquidity_score
  score, details = calculate_liquidity_score(data_dict)
================================================================================
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, Any


def get_percentile_rank(series: pd.Series, current_value: float, 
                        lookback_days: int = 504) -> float:
    """
    過去データに対する現在値のパーセンタイル順位を計算
    
    Args:
        series: 時系列データ
        current_value: 現在の値
        lookback_days: 参照期間（デフォルト504日≒2年）
    
    Returns:
        0-100のパーセンタイル値
    """
    if series is None or len(series) < 30:
        return 50.0  # データ不足時は中立値
    
    # 直近N日分を取得
    recent = series.tail(lookback_days).dropna()
    if len(recent) < 30:
        return 50.0
    
    # パーセンタイル計算
    rank = (recent < current_value).sum() / len(recent) * 100
    return float(rank)


def get_yoy_change_score(series: pd.Series) -> float:
    """
    前年比変化率をスコア化（-100～+100を0～100に変換）
    
    Args:
        series: 時系列データ
    
    Returns:
        0-100のスコア（50=変化なし、100=大幅増、0=大幅減）
    """
    if series is None or len(series) < 252:
        return 50.0
    
    current = series.iloc[-1]
    year_ago = series.iloc[-252] if len(series) >= 252 else series.iloc[0]
    
    if year_ago == 0 or pd.isna(year_ago) or pd.isna(current):
        return 50.0
    
    yoy_pct = ((current - year_ago) / abs(year_ago)) * 100
    
    # -20%～+20%を0～100にマップ（クリップ付き）
    score = 50 + (yoy_pct / 20) * 50
    return float(np.clip(score, 0, 100))


def calculate_net_liquidity(fed_assets: float, tga: float, on_rrp: float) -> float:
    """
    Net Liquidity = Fed Assets - TGA - ON_RRP
    """
    if any(pd.isna(x) for x in [fed_assets, tga, on_rrp]):
        return np.nan
    return fed_assets - tga - on_rrp


def calculate_liquidity_score(data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    流動性スコアを計算
    
    Args:
        data: データ辞書（キー: 'SOMA_Total', 'TGA', 'ON_RRP', 'Reserves', 'M2SL'）
              各値は pd.Series または dict{'value': float, 'series': pd.Series}
    
    Returns:
        (総合スコア, 詳細辞書)
    """
    details = {
        'fed_assets': {'value': None, 'score': None, 'weight': 0.00},  # 参考情報
        'tga': {'value': None, 'score': None, 'weight': 0.00},  # 参考情報
        'net_liquidity': {'value': None, 'score': None, 'weight': 0.50},
        'reserves': {'value': None, 'score': None, 'weight': 0.30},
        'm2_growth': {'value': None, 'score': None, 'weight': 0.20},
        'components_available': 0,
        'data_quality': 'unknown'
    }
    
    # --- データ抽出ヘルパー ---
    def extract_series_and_value(key: str) -> Tuple[Optional[pd.Series], Optional[float]]:
        """データ辞書から series と current value を抽出"""
        item = data.get(key)
        if item is None:
            return None, None
        
        if isinstance(item, pd.Series):
            return item, item.iloc[-1] if len(item) > 0 else None
        elif isinstance(item, dict):
            series = item.get('series') or item.get('data')
            value = item.get('value') or item.get('latest')
            if series is not None and value is None and len(series) > 0:
                value = series.iloc[-1]
            return series, value
        elif isinstance(item, (int, float)):
            return None, float(item)
        return None, None
    
    # --- 各指標の取得 ---
    fed_series, fed_val = extract_series_and_value('SOMA_Total')
    tga_series, tga_val = extract_series_and_value('TGA')
    rrp_series, rrp_val = extract_series_and_value('ON_RRP')
    res_series, res_val = extract_series_and_value('Reserves')
    m2_series, m2_val = extract_series_and_value('M2SL')
    
    weighted_sum = 0.0
    total_weight = 0.0
    
    # --- 参考情報: Fed Assets, TGA ---
    if fed_val is not None:
        details['fed_assets']['value'] = fed_val
        fed_pct = get_percentile_rank(fed_series, fed_val) if fed_series is not None else 50.0
        details['fed_assets']['score'] = fed_pct
    
    if tga_val is not None:
        details['tga']['value'] = tga_val
        # TGA は低いほど良い（逆スコア）
        tga_pct = get_percentile_rank(tga_series, tga_val) if tga_series is not None else 50.0
        details['tga']['score'] = 100 - tga_pct  # 低TGA = 高スコア
    
    # --- 1. Net Liquidity (50%) ---
    if all(v is not None for v in [fed_val, tga_val, rrp_val]):
        net_liq = calculate_net_liquidity(fed_val, tga_val, rrp_val)
        details['net_liquidity']['value'] = net_liq
        
        # Net Liquidity の時系列を構築（可能な場合）
        if all(s is not None for s in [fed_series, tga_series, rrp_series]):
            try:
                # 共通インデックスで揃える
                combined = pd.concat([fed_series, tga_series, rrp_series], axis=1)
                combined.columns = ['fed', 'tga', 'rrp']
                combined = combined.dropna()
                net_series = combined['fed'] - combined['tga'] - combined['rrp']
                percentile = get_percentile_rank(net_series, net_liq)
            except:
                percentile = 50.0
        else:
            percentile = 50.0
        
        details['net_liquidity']['score'] = percentile
        weighted_sum += percentile * 0.50
        total_weight += 0.50
        details['components_available'] += 1
    
    # --- 2. Reserves (30%) ---
    if res_val is not None:
        details['reserves']['value'] = res_val
        percentile = get_percentile_rank(res_series, res_val) if res_series is not None else 50.0
        details['reserves']['score'] = percentile
        weighted_sum += percentile * 0.30
        total_weight += 0.30
        details['components_available'] += 1
    
    # --- 3. M2 Growth (20%) ---
    if m2_series is not None and len(m2_series) > 252:
        yoy_score = get_yoy_change_score(m2_series)
        # YoY変化率も計算してvalueに保存
        current = m2_series.iloc[-1]
        year_ago = m2_series.iloc[-252] if len(m2_series) >= 252 else m2_series.iloc[0]
        if year_ago != 0 and not pd.isna(year_ago):
            yoy_pct = ((current - year_ago) / abs(year_ago)) * 100
            details['m2_growth']['value'] = yoy_pct
        details['m2_growth']['score'] = yoy_score
        weighted_sum += yoy_score * 0.20
        total_weight += 0.20
        details['components_available'] += 1
    
    # --- 総合スコア計算 ---
    if total_weight > 0:
        final_score = weighted_sum / total_weight * (total_weight / 1.0)  # 欠損補正
        final_score = np.clip(final_score, 0, 100)
    else:
        final_score = 50.0  # データなし時は中立
    
    # データ品質判定
    if details['components_available'] >= 3:
        details['data_quality'] = 'good'
    elif details['components_available'] >= 2:
        details['data_quality'] = 'partial'
    else:
        details['data_quality'] = 'insufficient'
    
    return float(final_score), details


def interpret_liquidity_score(score: float) -> Dict[str, str]:
    """
    流動性スコアを解釈（Michael Howell / CrossBorder Capital の分析手法を参考）
    
    Returns:
        {'level': 'bullish', 'label': '潤沢', 'color': 'green', 'description': '...'}
    """
    if score >= 70:
        return {
            'level': 'abundant',
            'label': '潤沢',
            'label_en': 'Abundant',
            'color': 'green',
            'description': '流動性サイクル上昇期。リスクオン環境、成長株・シクリカルに追い風。'
        }
    elif score >= 50:
        return {
            'level': 'neutral',
            'label': '中立',
            'label_en': 'Neutral',
            'color': 'yellow',
            'description': '流動性は平均的水準。セクター選別が重要な局面。'
        }
    elif score >= 30:
        return {
            'level': 'tightening',
            'label': 'タイト化',
            'label_en': 'Tightening',
            'color': 'orange',
            'description': '流動性縮小局面。テック→防御セクター/コモディティへのシフト期。'
        }
    else:
        return {
            'level': 'tight',
            'label': 'タイト',
            'label_en': 'Tight',
            'color': 'red',
            'description': '流動性枯渇。リスクオフ環境、短期債・現金選好。'
        }


# =============================================================================
# V2 スコア計算関数（Tier 1）
# =============================================================================

def score_fed_assets_change(soma_series: pd.Series) -> Tuple[float, Dict[str, Any]]:
    """
    Fed資産の月次変化率をスコア化（0-15点）
    
    金融的根拠:
      - Fed資産増加 = 市場への流動性供給（QE効果）
      - Fed資産減少 = 市場からの流動性吸収（QT効果）
      - 月次±3%は歴史的に大きな変動
    
    スコア変換:
      +3%以上 → 15点（QE的拡大）
      +1%～+3% → 12点（穏やかな拡大）
      -1%～+1% → 8点（横ばい）
      -3%～-1% → 4点（穏やかなQT）
      -3%以下 → 0点（積極的QT）
    """
    MAX_POINTS = 15
    NEUTRAL_SCORE = MAX_POINTS / 2  # 7.5
    
    if soma_series is None or len(soma_series) < 30:
        return NEUTRAL_SCORE, {'value': None, 'status': 'insufficient_data'}
    
    current = soma_series.iloc[-1]
    one_month_ago = soma_series.iloc[-22] if len(soma_series) >= 22 else soma_series.iloc[0]
    
    if pd.isna(current) or pd.isna(one_month_ago) or one_month_ago == 0:
        return NEUTRAL_SCORE, {'value': None, 'status': 'nan'}
    
    mom_pct = (current - one_month_ago) / one_month_ago * 100
    
    # 線形補間でスコア計算
    if mom_pct >= 3:
        score = 15
    elif mom_pct >= 1:
        score = 12 + (mom_pct - 1) / 2 * 3
    elif mom_pct >= -1:
        score = 8 + (mom_pct + 1) / 2 * 4
    elif mom_pct >= -3:
        score = 4 + (mom_pct + 3) / 2 * 4
    else:
        score = max(0, 4 + (mom_pct + 3) / 2 * 4)
    
    return float(np.clip(score, 0, MAX_POINTS)), {
        'value': mom_pct,
        'status': 'ok'
    }


def score_rrp_depletion(rrp_series: pd.Series) -> Tuple[float, Dict[str, Any]]:
    """
    ON RRP枯渇度をスコア化（0-15点）
    
    金融的根拠:
      - ON_RRP高水準 = 余剰流動性の滞留（市場に出ていない）
      - ON_RRP枯渇 = 滞留していた資金が市場に出る
      - 枯渇完了後は準備金の減少圧力が高まる
    
    スコア変換:
      枯渇度95%以上 → 15点（枯渇完了、流動性逼迫リスク）
      枯渇度80-95% → 12点（枯渇進行中）
      枯渇度50-80% → 9点（中間段階）
      枯渇度20-50% → 6点（まだ余力あり）
      枯渇度20%未満 → 3点（RRP潤沢）
    """
    MAX_POINTS = 15
    NEUTRAL_SCORE = MAX_POINTS / 2  # 7.5
    RRP_PEAK = 2554.0  # 2022年12月の歴史的ピーク（固定値）
    
    if rrp_series is None or len(rrp_series) == 0:
        return NEUTRAL_SCORE, {'value': None, 'status': 'insufficient_data'}
    
    current = rrp_series.iloc[-1]
    
    if pd.isna(current):
        return NEUTRAL_SCORE, {'value': None, 'status': 'nan'}
    
    # 負の値は0として扱う
    current = max(0, current)
    
    # 枯渇度計算
    depletion_pct = (RRP_PEAK - current) / RRP_PEAK * 100
    depletion_pct = np.clip(depletion_pct, 0, 100)
    
    # スコア変換
    if depletion_pct >= 95:
        score = 15
    elif depletion_pct >= 80:
        score = 12 + (depletion_pct - 80) / 15 * 3
    elif depletion_pct >= 50:
        score = 9 + (depletion_pct - 50) / 30 * 3
    elif depletion_pct >= 20:
        score = 6 + (depletion_pct - 20) / 30 * 3
    else:
        score = 3 + (depletion_pct / 20) * 3
    
    return float(np.clip(score, 0, MAX_POINTS)), {
        'value': current,
        'depletion_pct': depletion_pct,
        'status': 'ok'
    }


def score_tga_pressure(tga_series: pd.Series) -> Tuple[float, Dict[str, Any]]:
    """
    TGA圧力指数をスコア化（0-20点）
    水準スコア（10点）+ 速度スコア（10点）の2軸評価
    
    金融的根拠:
      - TGA = 財務省の「財布」
      - TGA低下 = 財務省が支出 → 市場に流動性供給
      - TGA上昇 = 財務省が蓄積 → 市場から流動性吸収
      - 債務上限問題時にTGAは極端に変動する
    """
    MAX_POINTS = 20
    NEUTRAL_SCORE = MAX_POINTS / 2  # 10
    
    if tga_series is None or len(tga_series) < 30:
        return NEUTRAL_SCORE, {'value': None, 'status': 'insufficient_data'}
    
    current = tga_series.iloc[-1]
    one_month_ago = tga_series.iloc[-22] if len(tga_series) >= 22 else tga_series.iloc[0]
    
    if pd.isna(current):
        return NEUTRAL_SCORE, {'value': None, 'status': 'nan'}
    
    # 1. 水準スコア（0-10点）
    # TGA < 400B → 10点, 400-600B → 8点, 600-800B → 6点, 800-1200B → 4点, >1200B → 2点
    if current < 400:
        level_score = 10
    elif current < 600:
        level_score = 8 + (600 - current) / 200 * 2
    elif current < 800:
        level_score = 6 + (800 - current) / 200 * 2
    elif current < 1200:
        level_score = 4 - (current - 800) / 400 * 2
    else:
        level_score = max(0, 2 - (current - 1200) / 400 * 2)
    
    level_score = np.clip(level_score, 0, 10)
    
    # 2. 速度スコア（0-10点）
    # MoM変化: -200B以下 → 10点 ... +100B以上 → 0点
    if not pd.isna(one_month_ago):
        mom_change = current - one_month_ago
        if mom_change <= -200:
            speed_score = 10
        elif mom_change <= -100:
            speed_score = 8 + (-100 - mom_change) / 100 * 2
        elif mom_change <= -50:
            speed_score = 6 + (-50 - mom_change) / 50 * 2
        elif mom_change <= 50:
            speed_score = 4 + (-mom_change) / 50 * 2
        elif mom_change <= 100:
            speed_score = 2 - (mom_change - 50) / 50 * 2
        else:
            speed_score = max(0, 2 - (mom_change - 50) / 50 * 2)
        speed_score = np.clip(speed_score, 0, 10)
    else:
        speed_score = 5  # 中立
        mom_change = None
    
    total = level_score + speed_score
    
    return float(np.clip(total, 0, MAX_POINTS)), {
        'value': current,
        'level_score': float(level_score),
        'speed_score': float(speed_score),
        'mom_change': mom_change,
        'status': 'ok'
    }


def calculate_liquidity_score_v2(data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    流動性スコアv2を計算（0-100点）
    
    スコア構成:
      【Tier 1】マクロ流動性環境（50点）
        ├─ Fed資産増減率:      15点
        ├─ ON RRP枯渇度:       15点
        └─ TGA圧力指数:        20点
      
      【Tier 2】システミック指標（35点）- スレッド4で実装予定
        ├─ 銀行準備金偏差:     12点
        ├─ SOFR適正性:         10点
        └─ M2実質成長率:       13点
      
      【Tier 3】市場シグナル（15点）- スレッド5で実装予定
        ├─ CP Spread:          5点
        ├─ MOVE Index:         5点
        └─ Credit Spread:      5点
    
    Args:
        data: データ辞書（キー: 'SOMA_Total', 'TGA', 'ON_RRP' 等）
    
    Returns:
        (総合スコア, 詳細辞書)
    """
    details = {
        'tier1': {
            'fed_assets_change': {'score': None, 'max': 15, 'details': {}},
            'rrp_depletion': {'score': None, 'max': 15, 'details': {}},
            'tga_pressure': {'score': None, 'max': 20, 'details': {}},
            'subtotal': 0,
            'max_points': 50
        },
        'tier2': {
            'reserves_deviation': {'score': None, 'max': 12, 'details': {}},
            'sofr_appropriateness': {'score': None, 'max': 10, 'details': {}},
            'real_m2_growth': {'score': None, 'max': 13, 'details': {}},
            'subtotal': 0,
            'max_points': 35
        },
        'tier3': {
            'cp_spread': {'score': None, 'max': 5, 'details': {}},
            'move_index': {'score': None, 'max': 5, 'details': {}},
            'credit_spread': {'score': None, 'max': 5, 'details': {}},
            'subtotal': 0,
            'max_points': 15
        },
        'total_score': 0,
        'data_quality': 'unknown',
        'components_available': 0
    }
    
    # --- データ抽出ヘルパー ---
    def extract_series(key: str) -> Optional[pd.Series]:
        """データ辞書から series を抽出"""
        item = data.get(key)
        if item is None:
            return None
        if isinstance(item, pd.Series):
            return item
        elif isinstance(item, dict):
            return item.get('series') or item.get('data')
        return None
    
    # =================================================================
    # Tier 1: マクロ流動性環境（50点）
    # =================================================================
    tier1_total = 0
    tier1_components = 0
    
    # 1.1 Fed資産増減率（15点）
    soma_series = extract_series('SOMA_Total')
    score, meta = score_fed_assets_change(soma_series)
    details['tier1']['fed_assets_change']['score'] = score
    details['tier1']['fed_assets_change']['details'] = meta
    if meta.get('status') == 'ok':
        tier1_total += score
        tier1_components += 1
    else:
        tier1_total += score  # 中立スコアも加算
    
    # 1.2 RRP枯渇度（15点）
    rrp_series = extract_series('ON_RRP')
    score, meta = score_rrp_depletion(rrp_series)
    details['tier1']['rrp_depletion']['score'] = score
    details['tier1']['rrp_depletion']['details'] = meta
    if meta.get('status') == 'ok':
        tier1_total += score
        tier1_components += 1
    else:
        tier1_total += score
    
    # 1.3 TGA圧力指数（20点）
    tga_series = extract_series('TGA')
    score, meta = score_tga_pressure(tga_series)
    details['tier1']['tga_pressure']['score'] = score
    details['tier1']['tga_pressure']['details'] = meta
    if meta.get('status') == 'ok':
        tier1_total += score
        tier1_components += 1
    else:
        tier1_total += score
    
    details['tier1']['subtotal'] = tier1_total
    details['components_available'] += tier1_components
    
    # =================================================================
    # Tier 2: システミック指標（35点）- スレッド4で実装予定
    # =================================================================
    # 中立スコアで埋める（Tier 2の50%）
    tier2_neutral = 35 / 2  # 17.5
    details['tier2']['subtotal'] = tier2_neutral
    details['tier2']['reserves_deviation']['score'] = 6  # 12の半分
    details['tier2']['sofr_appropriateness']['score'] = 5  # 10の半分
    details['tier2']['real_m2_growth']['score'] = 6.5  # 13の半分
    
    # =================================================================
    # Tier 3: 市場シグナル（15点）- スレッド5で実装予定
    # =================================================================
    # 中立スコアで埋める（Tier 3の50%）
    tier3_neutral = 15 / 2  # 7.5
    details['tier3']['subtotal'] = tier3_neutral
    details['tier3']['cp_spread']['score'] = 2.5
    details['tier3']['move_index']['score'] = 2.5
    details['tier3']['credit_spread']['score'] = 2.5
    
    # =================================================================
    # 総合スコア計算
    # =================================================================
    total_score = (
        details['tier1']['subtotal'] +
        details['tier2']['subtotal'] +
        details['tier3']['subtotal']
    )
    
    details['total_score'] = float(np.clip(total_score, 0, 100))
    
    # データ品質判定（現在はTier 1の3指標のみ）
    if tier1_components >= 3:
        details['data_quality'] = 'good'
    elif tier1_components >= 2:
        details['data_quality'] = 'partial'
    else:
        details['data_quality'] = 'insufficient'
    
    return details['total_score'], details


# =============================================================================
# テスト用
# =============================================================================
if __name__ == '__main__':
    # ダミーデータでテスト
    import numpy as np
    
    dates = pd.date_range('2022-01-01', periods=600, freq='D')
    test_data = {
        'SOMA_Total': pd.Series(np.random.normal(7500, 200, 600), index=dates),
        'TGA': pd.Series(np.random.normal(500, 100, 600), index=dates),
        'ON_RRP': pd.Series(np.random.normal(500, 200, 600), index=dates),
        'Reserves': pd.Series(np.random.normal(3200, 150, 600), index=dates),
        'M2SL': pd.Series(np.linspace(20000, 21000, 600), index=dates),
    }
    
    score, details = calculate_liquidity_score(test_data)
    interpretation = interpret_liquidity_score(score)
    
    print(f"Liquidity Score (v1): {score:.1f}")
    print(f"Interpretation: {interpretation['label']} ({interpretation['level']})")
    print(f"Components available: {details['components_available']}/3")
    print(f"Data quality: {details['data_quality']}")
    
    print("\n" + "="*50)
    print("V2 Score Test (Tier 1 only)")
    print("="*50)
    
    # V2テスト
    score_v2, details_v2 = calculate_liquidity_score_v2(test_data)
    interpretation_v2 = interpret_liquidity_score(score_v2)
    
    print(f"Liquidity Score (v2): {score_v2:.1f}")
    print(f"Interpretation: {interpretation_v2['label']} ({interpretation_v2['level']})")
    print(f"Data quality: {details_v2['data_quality']}")
    print(f"\nTier 1 Details:")
    t1 = details_v2['tier1']
    print(f"  Fed Assets Change: {t1['fed_assets_change']['score']:.1f}/15")
    print(f"    -> MoM%: {t1['fed_assets_change']['details'].get('value', 'N/A')}")
    print(f"  RRP Depletion: {t1['rrp_depletion']['score']:.1f}/15")
    print(f"    -> Value: {t1['rrp_depletion']['details'].get('value', 'N/A')}B")
    print(f"    -> Depletion: {t1['rrp_depletion']['details'].get('depletion_pct', 'N/A')}%")
    print(f"  TGA Pressure: {t1['tga_pressure']['score']:.1f}/20")
    print(f"    -> Value: {t1['tga_pressure']['details'].get('value', 'N/A')}B")
    print(f"    -> Level: {t1['tga_pressure']['details'].get('level_score', 'N/A')}/10")
    print(f"    -> Speed: {t1['tga_pressure']['details'].get('speed_score', 'N/A')}/10")
    print(f"  Subtotal: {t1['subtotal']:.1f}/50")
    print(f"\nTier 2 (placeholder): {details_v2['tier2']['subtotal']:.1f}/35")
    print(f"Tier 3 (placeholder): {details_v2['tier3']['subtotal']:.1f}/15")
