# -*- coding: utf-8 -*-
"""
MARKET VERDICT - Cycle Position Calculator
================================================================================
サイクル位置スコア（0-100）を計算するモジュール

スコア構成:
  - イールドカーブ（T10Y2Y）× 35%
  - 失業率トレンド × 25%
  - 信用スプレッド × 25%
  - Leading Index × 15%

使用方法:
  from utils.verdict_cycle import calculate_cycle_score
  score, details = calculate_cycle_score(data_dict)
================================================================================
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, Any


def get_percentile_rank(series: pd.Series, current_value: float,
                        lookback_days: int = 504) -> float:
    """過去データに対する現在値のパーセンタイル順位"""
    if series is None or len(series) < 30:
        return 50.0
    
    recent = series.tail(lookback_days).dropna()
    if len(recent) < 30:
        return 50.0
    
    rank = (recent < current_value).sum() / len(recent) * 100
    return float(rank)


def score_yield_curve(value: float, series: Optional[pd.Series] = None) -> float:
    """
    イールドカーブ（T10Y2Y）をスコア化
    
    - 正常（正）= 経済拡大期 → 高スコア
    - 逆転（負）= 景気後退シグナル → 低スコア
    - 逆転からの回復 = 要注意（後退が近い可能性）
    """
    if pd.isna(value):
        return 50.0
    
    # -1.0% ～ +2.5% を 0～100にマップ
    # 0%付近 = 50点、深い逆転 = 低い、スティープ = 高い
    score = 50 + (value / 2.5) * 50
    return float(np.clip(score, 0, 100))


def score_unemployment_trend(series: pd.Series) -> float:
    """
    失業率のトレンドをスコア化
    
    - 低下中 → 経済好調 → 高スコア
    - 上昇中 → 景気悪化 → 低スコア
    """
    if series is None or len(series) < 60:
        return 50.0
    
    current = series.iloc[-1]
    three_month_ago = series.iloc[-63] if len(series) >= 63 else series.iloc[0]
    year_ago = series.iloc[-252] if len(series) >= 252 else series.iloc[0]
    
    if any(pd.isna(x) for x in [current, three_month_ago, year_ago]):
        return 50.0
    
    # 3ヶ月変化と1年変化を組み合わせ
    short_change = current - three_month_ago  # プラス = 悪化
    long_change = current - year_ago
    
    # 変化を逆スコア化（上昇 = 悪い = 低スコア）
    # ±1%変化を±50点にマップ
    short_score = 50 - (short_change * 50)
    long_score = 50 - (long_change * 25)
    
    combined = short_score * 0.6 + long_score * 0.4
    return float(np.clip(combined, 0, 100))


def score_credit_spread(value: float, series: Optional[pd.Series] = None) -> float:
    """
    信用スプレッドをスコア化（逆スコア）
    
    - スプレッド拡大 = リスクオフ → 低スコア
    - スプレッド縮小 = リスクオン → 高スコア
    """
    if pd.isna(value):
        return 50.0
    
    # 典型的な範囲: 1% ～ 6%
    # 2%以下 = 好調、4%以上 = 警戒
    # 逆スコア: 低いほど良い
    if value <= 2.0:
        score = 80 + (2.0 - value) * 10  # 2%以下は80-100
    elif value <= 4.0:
        score = 80 - (value - 2.0) * 20  # 2-4%は40-80
    else:
        score = 40 - (value - 4.0) * 10  # 4%以上は急落
    
    return float(np.clip(score, 0, 100))


def score_leading_index(value: float, series: Optional[pd.Series] = None) -> float:
    """
    Leading Indexをスコア化
    
    - 正 = 経済拡大見込み → 高スコア
    - 負 = 経済縮小見込み → 低スコア
    """
    if pd.isna(value):
        return 50.0
    
    # 典型的な範囲: -2 ～ +2
    # 0 = 中立(50点)、±2で0/100
    score = 50 + (value / 2.0) * 50
    return float(np.clip(score, 0, 100))


def calculate_cycle_score(data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    サイクル位置スコアを計算
    
    Args:
        data: データ辞書
            'T10Y2Y': イールドカーブ
            'UNRATE': 失業率
            'Credit_Spread': 信用スプレッド
            'Leading_Index': 先行指標
    
    Returns:
        (総合スコア, 詳細辞書)
    """
    details = {
        'yield_curve': {'value': None, 'score': None, 'weight': 0.35},
        'unemployment': {'value': None, 'score': None, 'weight': 0.25},
        'credit_spread': {'value': None, 'score': None, 'weight': 0.25},
        'leading_index': {'value': None, 'score': None, 'weight': 0.15},
        'components_available': 0,
        'data_quality': 'unknown'
    }
    
    def extract_series_and_value(key: str) -> Tuple[Optional[pd.Series], Optional[float]]:
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
    
    weighted_sum = 0.0
    total_weight = 0.0
    
    # --- 1. Yield Curve (35%) ---
    yc_series, yc_val = extract_series_and_value('T10Y2Y')
    if yc_val is not None:
        score = score_yield_curve(yc_val, yc_series)
        details['yield_curve']['value'] = yc_val
        details['yield_curve']['score'] = score
        weighted_sum += score * 0.35
        total_weight += 0.35
        details['components_available'] += 1
    
    # --- 2. Unemployment (25%) ---
    ur_series, ur_val = extract_series_and_value('UNRATE')
    if ur_series is not None and len(ur_series) > 60:
        score = score_unemployment_trend(ur_series)
        details['unemployment']['value'] = ur_val
        details['unemployment']['score'] = score
        weighted_sum += score * 0.25
        total_weight += 0.25
        details['components_available'] += 1
    
    # --- 3. Credit Spread (25%) ---
    cs_series, cs_val = extract_series_and_value('Credit_Spread')
    if cs_val is not None:
        score = score_credit_spread(cs_val, cs_series)
        details['credit_spread']['value'] = cs_val
        details['credit_spread']['score'] = score
        weighted_sum += score * 0.25
        total_weight += 0.25
        details['components_available'] += 1
    
    # --- 4. Leading Index (15%) ---
    li_series, li_val = extract_series_and_value('Leading_Index')
    if li_val is not None:
        score = score_leading_index(li_val, li_series)
        details['leading_index']['value'] = li_val
        details['leading_index']['score'] = score
        weighted_sum += score * 0.15
        total_weight += 0.15
        details['components_available'] += 1
    
    # --- 総合スコア ---
    if total_weight > 0:
        final_score = weighted_sum / total_weight * (total_weight / 1.0)
        final_score = np.clip(final_score, 0, 100)
    else:
        final_score = 50.0
    
    # データ品質
    if details['components_available'] >= 4:
        details['data_quality'] = 'good'
    elif details['components_available'] >= 2:
        details['data_quality'] = 'partial'
    else:
        details['data_quality'] = 'insufficient'
    
    return float(final_score), details


def interpret_cycle_score(score: float) -> Dict[str, str]:
    """サイクルスコアを解釈"""
    if score >= 65:
        return {
            'level': 'expansion',
            'label': '拡大期',
            'label_en': 'Expansion',
            'color': 'green',
            'description': '経済は成長中。リスクオン環境。'
        }
    elif score >= 45:
        return {
            'level': 'neutral',
            'label': '中立',
            'label_en': 'Neutral',
            'color': 'yellow',
            'description': 'サイクル転換点付近。方向感に注意。'
        }
    elif score >= 25:
        return {
            'level': 'slowdown',
            'label': '減速期',
            'label_en': 'Slowdown',
            'color': 'orange',
            'description': '経済減速の兆候。慎重姿勢を推奨。'
        }
    else:
        return {
            'level': 'contraction',
            'label': '後退期',
            'label_en': 'Contraction',
            'color': 'red',
            'description': '景気後退リスク。防御的ポジションを。'
        }


# =============================================================================
# テスト用
# =============================================================================
if __name__ == '__main__':
    # ダミーデータでテスト
    dates = pd.date_range('2022-01-01', periods=300, freq='D')
    test_data = {
        'T10Y2Y': pd.Series(np.random.normal(0.5, 0.3, 300), index=dates),
        'UNRATE': pd.Series(np.linspace(3.8, 4.1, 300), index=dates),
        'Credit_Spread': pd.Series(np.random.normal(2.5, 0.5, 300), index=dates),
        'Leading_Index': pd.Series(np.random.normal(0.2, 0.3, 300), index=dates),
    }
    
    score, details = calculate_cycle_score(test_data)
    interpretation = interpret_cycle_score(score)
    
    print(f"Cycle Score: {score:.1f}")
    print(f"Interpretation: {interpretation['label']} ({interpretation['level']})")
    print(f"Components: {details['components_available']}/4")
