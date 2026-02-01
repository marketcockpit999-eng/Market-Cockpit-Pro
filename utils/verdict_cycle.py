# -*- coding: utf-8 -*-
"""
MARKET VERDICT - Cycle Position Calculator
================================================================================
サイクル位置スコア（0-100）を計算するモジュール

スコア構成 (7本柱):
  - イールドカーブ（T10Y2Y）× 25%
  - 失業率トレンド × 15%
  - 信用スプレッド × 15%
  - SLOOS融資基準 × 15%         ← 信用サイクル先行指標
  - Leading Index × 10%
  - Manufacturing Composite × 10% (地区連銀製造業)
  - Services Composite × 10% (地区連銀サービス業)

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


def score_sloos_standards(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    SLOOS融資基準のCompositeスコア（逆スコア）
    
    CI_Std_Large + CI_Std_Small の平均を使用
    - 正の値 = 融資基準引き締め → 低スコア（経済に悪影響）
    - 負の値 = 融資基準緩和 → 高スコア（経済に好影響）
    - ゼロ = 変化なし → 中立
    
    典型的な範囲: -40 ～ +80 (危機時は80超も)
    """
    sloos_keys = ['CI_Std_Large', 'CI_Std_Small']
    values = []
    
    for key in sloos_keys:
        item = data.get(key)
        if item is None:
            continue
        if isinstance(item, pd.Series) and len(item) > 0:
            val = item.iloc[-1]
        elif isinstance(item, (int, float)):
            val = float(item)
        else:
            continue
        if not pd.isna(val):
            values.append(val)
    
    if len(values) == 0:
        return None, {'available': 0, 'average': None}
    
    avg = np.mean(values)
    
    # 逆スコア化: 引き締め（正）= 低スコア、緩和（負）= 高スコア
    # -40 ～ +80 を 100 ～ 0 にマップ (0 → 66.7)
    # 0 = 中立(67点くらい)、+40% = 低、-30% = 高
    if avg <= -30:
        score = 95  # 大幅緩和
    elif avg <= 0:
        score = 65 + (-avg / 30) * 30  # 65-95
    elif avg <= 40:
        score = 65 - (avg / 40) * 40  # 25-65
    else:
        score = max(0, 25 - (avg - 40) / 2)  # 0-25
    
    score = float(np.clip(score, 0, 100))
    
    return score, {'available': len(values), 'average': avg}


def score_manufacturing_composite(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    地区連銀製造業指数のCompositeスコア
    
    各指数: 0超=拡大、0未満=縮小
    範囲: 約-40 ～ +40 を 0-100 にマップ
    """
    mfg_keys = ['Empire_State_Mfg', 'Philly_Fed_Mfg', 'Dallas_Fed_Mfg', 'Richmond_Fed_Mfg']
    values = []
    
    for key in mfg_keys:
        item = data.get(key)
        if item is None:
            continue
        if isinstance(item, pd.Series) and len(item) > 0:
            val = item.iloc[-1]
        elif isinstance(item, (int, float)):
            val = float(item)
        else:
            continue
        if not pd.isna(val):
            values.append(val)
    
    if len(values) == 0:
        return None, {'available': 0, 'average': None}
    
    avg = np.mean(values)
    # -40 ～ +40 を 0-100 にマップ（0 → 50）
    score = 50 + (avg / 40) * 50
    score = float(np.clip(score, 0, 100))
    
    return score, {'available': len(values), 'average': avg}


def score_services_composite(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    地区連銀サービス業指数のCompositeスコア
    """
    svc_keys = ['NY_Fed_Services', 'Philly_Fed_Services', 'Dallas_Fed_Services', 'Richmond_Fed_Services']
    values = []
    
    for key in svc_keys:
        item = data.get(key)
        if item is None:
            continue
        if isinstance(item, pd.Series) and len(item) > 0:
            val = item.iloc[-1]
        elif isinstance(item, (int, float)):
            val = float(item)
        else:
            continue
        if not pd.isna(val):
            values.append(val)
    
    if len(values) == 0:
        return None, {'available': 0, 'average': None}
    
    avg = np.mean(values)
    score = 50 + (avg / 40) * 50
    score = float(np.clip(score, 0, 100))
    
    return score, {'available': len(values), 'average': avg}


# =============================================================================
# NEW CYCLE V2 FUNCTIONS (4-Tier Structure)
# =============================================================================

def score_indpro(value: float, series: Optional[pd.Series] = None) -> float:
    """
    工業生産指数をスコア化（月次変化率ベース）
    
    Args:
        value: 現在値（使用しない、seriesから計算）
        series: INDPROの時系列データ
    
    Returns:
        0-100のスコア（月次変化率をスコア化）
    """
    if series is None or len(series) < 2:
        return 50.0
    
    try:
        # 前月比変化率を計算
        current = series.iloc[-1]
        previous = series.iloc[-2]
        
        if pd.isna(current) or pd.isna(previous) or previous == 0:
            return 50.0
        
        mom_change = (current - previous) / previous * 100
        
        # ±2%変化を±50点にマップ
        score = 50 + (mom_change / 2.0) * 50
        return float(np.clip(score, 0, 100))
    
    except Exception:
        return 50.0


def score_neworder(value: float, series: Optional[pd.Series] = None) -> float:
    """
    製造業新規受注をスコア化（先行性重視）
    
    Args:
        value: 現在値（使用しない、seriesから計算）
        series: NEWORDERの時系列データ
    
    Returns:
        0-100のスコア（月次変化率をスコア化）
    """
    if series is None or len(series) < 2:
        return 50.0
    
    try:
        # 前月比変化率
        current = series.iloc[-1]
        previous = series.iloc[-2]
        
        if pd.isna(current) or pd.isna(previous) or previous == 0:
            return 50.0
        
        mom_change = (current - previous) / previous * 100
        
        # ±3%変化を±50点にマップ（製造業はボラティリティ高い）
        score = 50 + (mom_change / 3.0) * 50
        return float(np.clip(score, 0, 100))
    
    except Exception:
        return 50.0


def score_nfci(value: float, series: Optional[pd.Series] = None) -> float:
    """
    NFCI金融環境指数をスコア化（逆スコア）
    
    Args:
        value: NFCIの現在値
        series: 時系列データ（オプション）
    
    Returns:
        0-100のスコア（負=金融緩和的=高スコア）
    """
    if pd.isna(value):
        return 50.0
    
    try:
        # NFCI: 負=金融緩和的、正=金融引締的
        # -1.0 ～ +1.0 を 100 ～ 0 にマップ（逆スコア）
        score = 50 - (value * 50)
        return float(np.clip(score, 0, 100))
    
    except Exception:
        return 50.0


def calculate_tier1_score(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    Tier 1: 経済成長サイクル - 生産と需要の実績 (45点)
    
    構成:
    - INDPRO（工業生産実績）: 10点
    - NEWORDER（新規受注・先行）: 8点
    - Services Composite（サービス業活動）: 6点
    - Yield Curve（金利環境）: 7点
    - SLOOS Lending（銀行融資態度）: 7点
    - Credit Spread（リスク選好）: 7点
    [合計: 45点]
    """
    tier_details = {
        'indpro': {'score': None, 'weight': 10, 'value': None},
        'neworder': {'score': None, 'weight': 8, 'value': None},
        'services': {'score': None, 'weight': 6, 'value': None},
        'yield_curve': {'score': None, 'weight': 7, 'value': None},
        'sloos': {'score': None, 'weight': 7, 'value': None},
        'credit_spread': {'score': None, 'weight': 7, 'value': None},
        'components_available': 0,
        'max_points': 45
    }
    
    weighted_sum = 0.0
    total_weight = 0.0
    
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
    
    # 1. INDPRO (10点)
    indpro_series, indpro_val = extract_series_and_value('INDPRO')
    if indpro_series is not None and len(indpro_series) >= 2:
        score = score_indpro(indpro_val, indpro_series)
        tier_details['indpro']['score'] = score
        tier_details['indpro']['value'] = indpro_val
        weighted_sum += score * 10
        total_weight += 10
        tier_details['components_available'] += 1
    
    # 2. NEWORDER (8点)
    neworder_series, neworder_val = extract_series_and_value('NEWORDER')
    if neworder_series is not None and len(neworder_series) >= 2:
        score = score_neworder(neworder_val, neworder_series)
        tier_details['neworder']['score'] = score
        tier_details['neworder']['value'] = neworder_val
        weighted_sum += score * 8
        total_weight += 8
        tier_details['components_available'] += 1
    
    # 3. Services Composite (6点)
    svc_score, svc_info = score_services_composite(data)
    if svc_score is not None:
        tier_details['services']['score'] = svc_score
        tier_details['services']['value'] = svc_info['average']
        tier_details['services']['available'] = svc_info['available']
        weighted_sum += svc_score * 6
        total_weight += 6
        tier_details['components_available'] += 1
    
    # 4. Yield Curve (7点)
    yc_series, yc_val = extract_series_and_value('T10Y2Y')
    if yc_val is not None:
        score = score_yield_curve(yc_val, yc_series)
        tier_details['yield_curve']['score'] = score
        tier_details['yield_curve']['value'] = yc_val
        weighted_sum += score * 7
        total_weight += 7
        tier_details['components_available'] += 1
    
    # 5. SLOOS Lending (7点)
    sloos_score, sloos_info = score_sloos_standards(data)
    if sloos_score is not None:
        tier_details['sloos']['score'] = sloos_score
        tier_details['sloos']['value'] = sloos_info['average']
        tier_details['sloos']['available'] = sloos_info['available']
        weighted_sum += sloos_score * 7
        total_weight += 7
        tier_details['components_available'] += 1
    
    # 6. Credit Spread (7点)
    cs_series, cs_val = extract_series_and_value('Credit_Spread')
    if cs_val is not None:
        score = score_credit_spread(cs_val, cs_series)
        tier_details['credit_spread']['score'] = score
        tier_details['credit_spread']['value'] = cs_val
        weighted_sum += score * 7
        total_weight += 7
        tier_details['components_available'] += 1
    
    # Tier1スコア計算（45点満点）
    if total_weight > 0:
        # 重み付き平均を計算し、45点満点にスケール
        avg_score = weighted_sum / total_weight
        tier1_score = (avg_score / 100.0) * 45.0
        tier1_score = float(np.clip(tier1_score, 0, 45))
    else:
        tier1_score = None
    
    return tier1_score, tier_details


def calculate_tier2_score(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    Tier 2: 労働・インフレ・金融環境 - 持続可能性 (35点)
    
    構成:
    - Unemployment Trend（失業率トレンド）: 15点 ⭐ 強化
    - Leading Index（先行指標複合）: 10点 ⭐ 強化  
    - Manufacturing Composite（製造業複合）: 10点 ⭐ 強化
    [合計: 35点]
    """
    tier_details = {
        'unemployment': {'score': None, 'weight': 15, 'value': None},
        'leading_index': {'score': None, 'weight': 10, 'value': None},
        'manufacturing': {'score': None, 'weight': 10, 'value': None},
        'components_available': 0,
        'max_points': 35
    }
    
    weighted_sum = 0.0
    total_weight = 0.0
    
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
    
    # 1. Unemployment Trend (15点) ⭐ 強化
    ur_series, ur_val = extract_series_and_value('UNRATE')
    if ur_series is not None and len(ur_series) > 60:
        score = score_unemployment_trend(ur_series)
        tier_details['unemployment']['score'] = score
        tier_details['unemployment']['value'] = ur_val
        weighted_sum += score * 15
        total_weight += 15
        tier_details['components_available'] += 1
    
    # 2. Leading Index (10点) ⭐ 強化
    li_series, li_val = extract_series_and_value('Leading_Index')
    if li_val is not None:
        score = score_leading_index(li_val, li_series)
        tier_details['leading_index']['score'] = score
        tier_details['leading_index']['value'] = li_val
        weighted_sum += score * 10
        total_weight += 10
        tier_details['components_available'] += 1
    
    # 3. Manufacturing Composite (10点) ⭐ 強化
    mfg_score, mfg_info = score_manufacturing_composite(data)
    if mfg_score is not None:
        tier_details['manufacturing']['score'] = mfg_score
        tier_details['manufacturing']['value'] = mfg_info['average']
        tier_details['manufacturing']['available'] = mfg_info['available']
        weighted_sum += mfg_score * 10
        total_weight += 10
        tier_details['components_available'] += 1
    
    # Tier2スコア計算（35点満点）
    if total_weight > 0:
        # 重み付き平均を計算し、35点満点にスケール
        avg_score = weighted_sum / total_weight
        tier2_score = (avg_score / 100.0) * 35.0
        tier2_score = float(np.clip(tier2_score, 0, 35))
    else:
        tier2_score = None
    
    return tier2_score, tier_details


def score_vix_risk(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    VIX + リスク指標をスコア化（逆スコア）
    
    VIXが高い = 市場不安 → 低スコア
    VIXが低い = 市場安定 → 高スコア
    """
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
    
    vix_series, vix_val = extract_series_and_value('VIX')
    
    if vix_val is None or pd.isna(vix_val):
        return None, {'available': 0, 'vix_value': None}
    
    try:
        # VIX逆スコア化: 10-50を100-0にマップ
        # 10以下 = 極低ボラ = 100点
        # 20 = 標準 = 75点
        # 30 = 不安 = 50点
        # 50以上 = 極度不安 = 0点
        if vix_val <= 10:
            score = 100.0
        elif vix_val <= 20:
            score = 100 - (vix_val - 10) * 2.5  # 100-75
        elif vix_val <= 30:
            score = 75 - (vix_val - 20) * 2.5   # 75-50
        elif vix_val <= 50:
            score = 50 - (vix_val - 30) * 2.5   # 50-0
        else:
            score = 0.0
        
        score = float(np.clip(score, 0, 100))
        
        return score, {'available': 1, 'vix_value': vix_val}
    
    except Exception:
        return None, {'available': 0, 'vix_value': vix_val}


def score_consumer_sentiment(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    Consumer Sentimentをスコア化
    
    消費者センチメント高 = 経済好調 → 高スコア
    """
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
    
    cs_series, cs_val = extract_series_and_value('ConsumerSent')
    
    if cs_val is None or pd.isna(cs_val):
        return None, {'available': 0, 'sentiment_value': None}
    
    try:
        # Consumer Sentiment: 範囲 60-120くらい
        # 100 = 標準 = 80点
        # 110以上 = 非常に好調 = 100点
        # 70以下 = 悲観 = 0点
        if cs_val >= 110:
            score = 100.0
        elif cs_val >= 100:
            score = 80 + (cs_val - 100) * 2.0   # 80-100
        elif cs_val >= 70:
            score = (cs_val - 70) * 2.67        # 0-80
        else:
            score = 0.0
        
        score = float(np.clip(score, 0, 100))
        
        return score, {'available': 1, 'sentiment_value': cs_val}
    
    except Exception:
        return None, {'available': 0, 'sentiment_value': cs_val}


def calculate_tier3_score(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    Tier 3: センチメント・期待値 - 市場心理 (15点)
    
    構成:
    - VIX + リスク指標: 8点
    - Consumer Sentiment: 4点
    - NFCI（金融環境指数）: 3点 ⭐ NEW
    [合計: 15点]
    """
    tier_details = {
        'vix_risk': {'score': None, 'weight': 8, 'value': None},
        'consumer_sentiment': {'score': None, 'weight': 4, 'value': None},
        'nfci': {'score': None, 'weight': 3, 'value': None},
        'components_available': 0,
        'max_points': 15
    }
    
    weighted_sum = 0.0
    total_weight = 0.0
    
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
    
    # 1. VIX + リスク指標 (8点)
    vix_score, vix_info = score_vix_risk(data)
    if vix_score is not None:
        tier_details['vix_risk']['score'] = vix_score
        tier_details['vix_risk']['value'] = vix_info['vix_value']
        tier_details['vix_risk']['available'] = vix_info['available']
        weighted_sum += vix_score * 8
        total_weight += 8
        tier_details['components_available'] += 1
    
    # 2. Consumer Sentiment (4点)
    cs_score, cs_info = score_consumer_sentiment(data)
    if cs_score is not None:
        tier_details['consumer_sentiment']['score'] = cs_score
        tier_details['consumer_sentiment']['value'] = cs_info['sentiment_value']
        tier_details['consumer_sentiment']['available'] = cs_info['available']
        weighted_sum += cs_score * 4
        total_weight += 4
        tier_details['components_available'] += 1
    
    # 3. NFCI (3点) ⭐ 統合
    nfci_series, nfci_val = extract_series_and_value('NFCI')
    if nfci_val is not None:
        score = score_nfci(nfci_val, nfci_series)
        tier_details['nfci']['score'] = score
        tier_details['nfci']['value'] = nfci_val
        weighted_sum += score * 3
        total_weight += 3
        tier_details['components_available'] += 1
    
    # Tier3スコア計算（15点満点）
    if total_weight > 0:
        # 重み付き平均を計算し、15点満点にスケール
        avg_score = weighted_sum / total_weight
        tier3_score = (avg_score / 100.0) * 15.0
        tier3_score = float(np.clip(tier3_score, 0, 15))
    else:
        tier3_score = None
    
    return tier3_score, tier_details


def score_200ma_divergence(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    200日MA乖離をスコア化
    
    上方乖離 = トレンド好調 → 高スコア
    下方乖離 = トレンド悪化 → 低スコア
    """
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
    
    # SPXを取得して200日MAとの乖離を計算
    spx_series, spx_val = extract_series_and_value('SPX')
    
    if spx_series is None or len(spx_series) < 200:
        return None, {'available': 0, 'divergence_pct': None, 'current_price': None}
    
    try:
        # 200日移動平均を計算
        ma200 = spx_series.rolling(window=200).mean().iloc[-1]
        
        if pd.isna(ma200) or ma200 == 0:
            return None, {'available': 0, 'divergence_pct': None, 'current_price': spx_val}
        
        # 乖離率を計算
        divergence_pct = (spx_val - ma200) / ma200 * 100
        
        # 乖離率をスコア化
        # -20%以下 = 0点, 0% = 50点, +20%以上 = 100点
        if divergence_pct <= -20:
            score = 0.0
        elif divergence_pct >= 20:
            score = 100.0
        else:
            score = 50 + (divergence_pct / 20.0) * 50
        
        score = float(np.clip(score, 0, 100))
        
        return score, {
            'available': 1,
            'divergence_pct': divergence_pct,
            'current_price': spx_val,
            'ma200': ma200
        }
    
    except Exception:
        return None, {'available': 0, 'divergence_pct': None, 'current_price': spx_val}


def score_rsi_trend(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    RSI動向をスコア化
    
    RSI > 70 = 買い過ぎ = 低スコア
    RSI < 30 = 売られ過ぎ = 低スコア
    RSI 30-70 = 中立域 = 高スコア
    """
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
    
    # SPXからRSIを計算
    spx_series, spx_val = extract_series_and_value('SPX')
    
    if spx_series is None or len(spx_series) < 15:  # RSI計算には最低15日必要
        return None, {'available': 0, 'rsi_value': None}
    
    try:
        # RSI計算 (14期間)
        delta = spx_series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        rsi_val = rsi.iloc[-1]
        
        if pd.isna(rsi_val):
            return None, {'available': 0, 'rsi_value': None}
        
        # RSIをスコア化
        # 30-70が中立域（高スコア）
        # 範囲外は極端（低スコア）
        if 30 <= rsi_val <= 70:
            # 中立域は線形スコア (30=80点, 50=100点, 70=80点)
            if rsi_val <= 50:
                score = 80 + (rsi_val - 30) * 1.0  # 80-100
            else:
                score = 100 - (rsi_val - 50) * 1.0  # 100-80
        elif rsi_val < 30:
            # 売られ過ぎ域
            score = max(0, rsi_val * 2.67)  # 0-80
        else:  # rsi_val > 70
            # 買い過ぎ域
            score = max(0, 80 - (rsi_val - 70) * 2.67)  # 80-0
        
        score = float(np.clip(score, 0, 100))
        
        return score, {'available': 1, 'rsi_value': rsi_val}
    
    except Exception:
        return None, {'available': 0, 'rsi_value': None}


def calculate_tier4_score(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    Tier 4: テクニカル・トレンド - 方向性確認 (5点)
    
    構成:
    - 200日MA乖離: 3点
    - RSI動向: 2点
    [合計: 5点]
    """
    tier_details = {
        'ma200_divergence': {'score': None, 'weight': 3, 'value': None},
        'rsi_trend': {'score': None, 'weight': 2, 'value': None},
        'components_available': 0,
        'max_points': 5
    }
    
    weighted_sum = 0.0
    total_weight = 0.0
    
    # 1. 200日MA乖離 (3点)
    ma_score, ma_info = score_200ma_divergence(data)
    if ma_score is not None:
        tier_details['ma200_divergence']['score'] = ma_score
        tier_details['ma200_divergence']['value'] = ma_info['divergence_pct']
        tier_details['ma200_divergence']['available'] = ma_info['available']
        tier_details['ma200_divergence']['current_price'] = ma_info['current_price']
        tier_details['ma200_divergence']['ma200'] = ma_info.get('ma200')
        weighted_sum += ma_score * 3
        total_weight += 3
        tier_details['components_available'] += 1
    
    # 2. RSI動向 (2点)
    rsi_score, rsi_info = score_rsi_trend(data)
    if rsi_score is not None:
        tier_details['rsi_trend']['score'] = rsi_score
        tier_details['rsi_trend']['value'] = rsi_info['rsi_value']
        tier_details['rsi_trend']['available'] = rsi_info['available']
        weighted_sum += rsi_score * 2
        total_weight += 2
        tier_details['components_available'] += 1
    
    # Tier4スコア計算（5点満点）
    if total_weight > 0:
        # 重み付き平均を計算し、5点満点にスケール
        avg_score = weighted_sum / total_weight
        tier4_score = (avg_score / 100.0) * 5.0
        tier4_score = float(np.clip(tier4_score, 0, 5))
    else:
        tier4_score = None
    
    return tier4_score, tier_details


# =============================================================================
# 新4-TIER統合ロジック
# =============================================================================

# 新旧切り替えフラグ
USE_NEW_CYCLE_LOGIC = True  # True: 新4-Tier方式, False: 旧7本柱方式


def calculate_new_cycle_score(data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    新4-Tier方式でサイクルスコアを計算（100点満点）
    
    構成:
    - Tier 1: 経済成長サイクル (45点)
    - Tier 2: 労働・インフレ・金融環境 (35点)
    - Tier 3: センチメント・期待値 (15点)
    - Tier 4: テクニカル・トレンド (5点)
    [合計: 100点]
    """
    details = {
        'tier1': {'score': None, 'details': None, 'weight': 45},
        'tier2': {'score': None, 'details': None, 'weight': 35},
        'tier3': {'score': None, 'details': None, 'weight': 15},
        'tier4': {'score': None, 'details': None, 'weight': 5},
        'total_score': 0.0,
        'tiers_available': 0,
        'data_quality': 'unknown',
        'method': 'new_4tier'
    }
    
    total_score = 0.0
    tiers_available = 0
    
    # Tier 1: 経済成長サイクル (45点)
    tier1_score, tier1_details = calculate_tier1_score(data)
    if tier1_score is not None:
        details['tier1']['score'] = tier1_score
        details['tier1']['details'] = tier1_details
        total_score += tier1_score
        tiers_available += 1
    
    # Tier 2: 労働・インフレ・金融環境 (35点)
    tier2_score, tier2_details = calculate_tier2_score(data)
    if tier2_score is not None:
        details['tier2']['score'] = tier2_score
        details['tier2']['details'] = tier2_details
        total_score += tier2_score
        tiers_available += 1
    
    # Tier 3: センチメント・期待値 (15点)
    tier3_score, tier3_details = calculate_tier3_score(data)
    if tier3_score is not None:
        details['tier3']['score'] = tier3_score
        details['tier3']['details'] = tier3_details
        total_score += tier3_score
        tiers_available += 1
    
    # Tier 4: テクニカル・トレンド (5点)
    tier4_score, tier4_details = calculate_tier4_score(data)
    if tier4_score is not None:
        details['tier4']['score'] = tier4_score
        details['tier4']['details'] = tier4_details
        total_score += tier4_score
        tiers_available += 1
    
    # 総合スコア設定
    details['total_score'] = float(np.clip(total_score, 0, 100))
    details['tiers_available'] = tiers_available
    
    # データ品質評価
    if tiers_available >= 3:
        details['data_quality'] = 'good'
    elif tiers_available >= 2:
        details['data_quality'] = 'partial'
    else:
        details['data_quality'] = 'insufficient'
    
    return details['total_score'], details


# OLD LOGIC: 7本柱方式（削除予定）
# def calculate_old_cycle_score(data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
#     """
#     サイクル位置スコアを計算 (7本柱)
#     
#     DEPRECATED: 旧方式のため削除予定
#     新4-Tier方式（calculate_new_cycle_score）に移行済み
#     
#     Args:
#         data: データ辞書
#             'T10Y2Y': イールドカーブ
#             'UNRATE': 失業率
#             'Credit_Spread': 信用スプレッド
#             'Leading_Index': 先行指標
#             'CI_Std_Large': SLOOS C&I基準（大企業）
#             'CI_Std_Small': SLOOS C&I基準（小企業）
#             + 地区連銀製造業・サービス業
#     
#     Returns:
#         (総合スコア, 詳細辞書)
#     """
#     pass  # 削除済み


def calculate_cycle_score(data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    サイクル位置スコアを計算
    
    新4-Tier方式で統一（100点満点）
    - Tier 1: 経済成長サイクル (45点)
    - Tier 2: 労働・インフレ・金融環境 (35点) 
    - Tier 3: センチメント・期待値 (15点)
    - Tier 4: テクニカル・トレンド (5点)
    """
    return calculate_new_cycle_score(data)


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
    # ダミーデータでテスト（新4-Tier方式のみ）
    dates = pd.date_range('2022-01-01', periods=300, freq='D')
    test_data = {
        'T10Y2Y': pd.Series(np.random.normal(0.5, 0.3, 300), index=dates),
        'UNRATE': pd.Series(np.linspace(3.8, 4.1, 300), index=dates),
        'Credit_Spread': pd.Series(np.random.normal(2.5, 0.5, 300), index=dates),
        'Leading_Index': pd.Series(np.random.normal(0.2, 0.3, 300), index=dates),
        'CI_Std_Large': pd.Series(np.random.normal(10, 15, 300), index=dates),
        'CI_Std_Small': pd.Series(np.random.normal(15, 15, 300), index=dates),
        # 新指標追加
        'INDPRO': pd.Series(np.linspace(100, 105, 300), index=dates),
        'NEWORDER': pd.Series(np.random.normal(50000, 5000, 300), index=dates),
        'NFCI': pd.Series(np.random.normal(-0.2, 0.3, 300), index=dates),
        'VIX': pd.Series(np.random.normal(20, 5, 300), index=dates),
        'ConsumerSent': pd.Series(np.random.normal(100, 10, 300), index=dates),
        'SPX': pd.Series(np.cumsum(np.random.normal(0.05, 1, 300)) + 4500, index=dates),
    }
    
    # 新方式（4-Tier）テスト
    score, details = calculate_cycle_score(test_data)
    interpretation = interpret_cycle_score(score)
    
    print("=== 新4-Tier方式 ===")
    print(f"Cycle Score: {score:.1f}")
    print(f"Interpretation: {interpretation['label']} ({interpretation['level']})")
    print(f"Tiers Available: {details['tiers_available']}/4")
    print(f"Data Quality: {details['data_quality']}")
    
    # Tier別詳細
    for tier_name in ['tier1', 'tier2', 'tier3', 'tier4']:
        tier_info = details[tier_name]
        if tier_info['score'] is not None:
            print(f"  {tier_name.upper()}: {tier_info['score']:.1f}/{tier_info['weight']:.0f} points")
        else:
            print(f"  {tier_name.upper()}: N/A")
    
    # 個別関数テスト
    print("\n=== 新関数個別テスト ===")
    indpro_score = score_indpro(None, test_data['INDPRO'])
    neworder_score = score_neworder(None, test_data['NEWORDER'])
    nfci_score = score_nfci(test_data['NFCI'].iloc[-1])
    vix_score, vix_info = score_vix_risk(test_data)
    cs_score, cs_info = score_consumer_sentiment(test_data)
    
    print(f"INDPRO Score: {indpro_score:.1f}")
    print(f"NEWORDER Score: {neworder_score:.1f}")
    print(f"NFCI Score: {nfci_score:.1f}")
    print(f"VIX Score: {vix_score:.1f} (VIX: {vix_info['vix_value']:.1f})")
    print(f"Consumer Sentiment Score: {cs_score:.1f} (CS: {cs_info['sentiment_value']:.1f})")
    
    print("\n✅ 新4-Tier方式への移行完了")
