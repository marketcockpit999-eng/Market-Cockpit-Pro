# -*- coding: utf-8 -*-
"""
MARKET VERDICT - Liquidity Score Calculator
================================================================================
流動性スコア（0-100）を計算するモジュール

スコア構成:
  - Net Liquidity パーセンタイル × 40%
  - Reserves パーセンタイル × 30%
  - ON_RRP 逆パーセンタイル × 20%  (低いほど良い)
  - M2 YoY変化率スコア × 10%

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
        data: データ辞書（キー: 'Fed_Assets', 'TGA', 'ON_RRP', 'Reserves', 'M2SL'）
              各値は pd.Series または dict{'value': float, 'series': pd.Series}
    
    Returns:
        (総合スコア, 詳細辞書)
    """
    details = {
        'net_liquidity': {'value': None, 'percentile': None, 'weight': 0.40},
        'reserves': {'value': None, 'percentile': None, 'weight': 0.30},
        'on_rrp': {'value': None, 'percentile': None, 'weight': 0.20},
        'm2_yoy': {'value': None, 'score': None, 'weight': 0.10},
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
    fed_series, fed_val = extract_series_and_value('Fed_Assets')
    tga_series, tga_val = extract_series_and_value('TGA')
    rrp_series, rrp_val = extract_series_and_value('ON_RRP')
    res_series, res_val = extract_series_and_value('Reserves')
    m2_series, m2_val = extract_series_and_value('M2SL')
    
    weighted_sum = 0.0
    total_weight = 0.0
    
    # --- 1. Net Liquidity (40%) ---
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
        
        details['net_liquidity']['percentile'] = percentile
        weighted_sum += percentile * 0.40
        total_weight += 0.40
        details['components_available'] += 1
    
    # --- 2. Reserves (30%) ---
    if res_val is not None:
        details['reserves']['value'] = res_val
        percentile = get_percentile_rank(res_series, res_val) if res_series is not None else 50.0
        details['reserves']['percentile'] = percentile
        weighted_sum += percentile * 0.30
        total_weight += 0.30
        details['components_available'] += 1
    
    # --- 3. ON_RRP (20%) - 逆スコア（低いほど良い） ---
    if rrp_val is not None:
        details['on_rrp']['value'] = rrp_val
        percentile = get_percentile_rank(rrp_series, rrp_val) if rrp_series is not None else 50.0
        inverse_percentile = 100 - percentile  # 低いほどスコア高
        details['on_rrp']['percentile'] = inverse_percentile
        weighted_sum += inverse_percentile * 0.20
        total_weight += 0.20
        details['components_available'] += 1
    
    # --- 4. M2 YoY (10%) ---
    if m2_series is not None and len(m2_series) > 252:
        yoy_score = get_yoy_change_score(m2_series)
        details['m2_yoy']['score'] = yoy_score
        weighted_sum += yoy_score * 0.10
        total_weight += 0.10
        details['components_available'] += 1
    
    # --- 総合スコア計算 ---
    if total_weight > 0:
        final_score = weighted_sum / total_weight * (total_weight / 1.0)  # 欠損補正
        final_score = np.clip(final_score, 0, 100)
    else:
        final_score = 50.0  # データなし時は中立
    
    # データ品質判定
    if details['components_available'] >= 4:
        details['data_quality'] = 'good'
    elif details['components_available'] >= 2:
        details['data_quality'] = 'partial'
    else:
        details['data_quality'] = 'insufficient'
    
    return float(final_score), details


def interpret_liquidity_score(score: float) -> Dict[str, str]:
    """
    流動性スコアを解釈
    
    Returns:
        {'level': 'bullish', 'label': '潤沢', 'color': 'green', 'description': '...'}
    """
    if score >= 70:
        return {
            'level': 'bullish',
            'label': '潤沢',
            'label_en': 'Abundant',
            'color': 'green',
            'description': '流動性は十分。リスク資産に追い風。'
        }
    elif score >= 50:
        return {
            'level': 'neutral',
            'label': '中立',
            'label_en': 'Neutral',
            'color': 'yellow',
            'description': '流動性は平均的。方向感に注意。'
        }
    elif score >= 30:
        return {
            'level': 'cautious',
            'label': '注意',
            'label_en': 'Caution',
            'color': 'orange',
            'description': '流動性がやや低下。慎重な姿勢を。'
        }
    else:
        return {
            'level': 'bearish',
            'label': '警戒',
            'label_en': 'Tight',
            'color': 'red',
            'description': '流動性が枯渇気味。リスクオフ環境。'
        }


# =============================================================================
# テスト用
# =============================================================================
if __name__ == '__main__':
    # ダミーデータでテスト
    import numpy as np
    
    dates = pd.date_range('2022-01-01', periods=600, freq='D')
    test_data = {
        'Fed_Assets': pd.Series(np.random.normal(7500, 200, 600), index=dates),
        'TGA': pd.Series(np.random.normal(500, 100, 600), index=dates),
        'ON_RRP': pd.Series(np.random.normal(500, 200, 600), index=dates),
        'Reserves': pd.Series(np.random.normal(3200, 150, 600), index=dates),
        'M2SL': pd.Series(np.linspace(20000, 21000, 600), index=dates),
    }
    
    score, details = calculate_liquidity_score(test_data)
    interpretation = interpret_liquidity_score(score)
    
    print(f"Liquidity Score: {score:.1f}")
    print(f"Interpretation: {interpretation['label']} ({interpretation['level']})")
    print(f"Components available: {details['components_available']}/4")
    print(f"Data quality: {details['data_quality']}")
