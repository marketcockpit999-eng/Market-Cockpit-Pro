# -*- coding: utf-8 -*-
"""
MARKET VERDICT - Sentiment Score Calculator
================================================================================
センチメントスコア（0-100）を計算するモジュール
Howard Marksの「極端を避ける」思想を反映

スコア構成 (3本柱):
  - VIXスコア（逆）× 35%            ← VIX高=Fear=低スコア
  - NFCI × 35%                       ← 金融環境指数（逆）
  - ConsumerSent × 30%               ← 消費者信頼感

使用方法:
  from utils.verdict_sentiment import calculate_sentiment_score
  score, details = calculate_sentiment_score(data_dict)
================================================================================
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, Any


def get_percentile_rank(series: pd.Series, current_value: float,
                        lookback_days: int = 504) -> float:
    """過去データに対する現在値のパーセンタイル順位（0-100）"""
    if series is None or len(series) < 30:
        return 50.0
    
    recent = series.tail(lookback_days).dropna()
    if len(recent) < 30:
        return 50.0
    
    rank = (recent < current_value).sum() / len(recent) * 100
    return float(rank)


def score_vix(vix_value: float, vix_series: Optional[pd.Series] = None) -> float:
    """
    VIXをスコア化（逆スコア：VIX高=Fear=低スコア）
    
    VIX基準:
    - < 12: 極端な低Volatility（Greed）→ 高スコア（90-100）
    - 12-20: 正常範囲 → 中立（50-70）
    - 20-30: 警戒域 → 低スコア（30-50）
    - > 30: 恐怖域 → 非常に低スコア（0-30）
    """
    if pd.isna(vix_value):
        return 50.0
    
    # VIXを0-100のスコアに変換（逆転）
    if vix_value < 12:
        score = 90 + (12 - vix_value) / 2  # 90-100
    elif vix_value < 20:
        score = 70 - (vix_value - 12) * 2.5  # 50-70
    elif vix_value < 30:
        score = 50 - (vix_value - 20) * 2  # 30-50
    else:
        score = max(0, 30 - (vix_value - 30))  # 0-30
    
    return float(np.clip(score, 0, 100))


def score_credit_spread(spread_value: float, 
                        spread_series: Optional[pd.Series] = None) -> float:
    """
    信用スプレッドをスコア化（逆スコア：スプレッド拡大=Fear=低スコア）
    
    スプレッド基準（%）:
    - < 3%: 楽観的 → 高スコア
    - 3-5%: 正常 → 中立
    - > 5%: 警戒 → 低スコア
    """
    if pd.isna(spread_value):
        return 50.0
    
    # パーセンタイルも考慮（あれば）
    if spread_series is not None and len(spread_series) > 30:
        percentile = get_percentile_rank(spread_series, spread_value)
        # パーセンタイルを逆転（低スプレッド=高スコア）
        return 100 - percentile
    
    # 固定基準でスコア化
    if spread_value < 3:
        score = 80 + (3 - spread_value) * 6.67  # 80-100
    elif spread_value < 5:
        score = 50 + (5 - spread_value) * 15  # 50-80
    else:
        score = max(0, 50 - (spread_value - 5) * 10)  # 0-50
    
    return float(np.clip(score, 0, 100))


def score_ma_deviation(price_series: pd.Series, ma_period: int = 200) -> Tuple[float, float]:
    """
    200日MA乖離率をスコア化
    
    乖離率:
    - +10%以上: 過熱（Greed）→ 高スコア（警告含む）
    - 0〜+10%: 健全な上昇 → まあまあ高スコア
    - -10%〜0%: 調整中 → 低め
    - -10%以下: 暴落 → 低スコア（逆張り機会）
    
    Returns:
        (score, deviation_pct)
    """
    if price_series is None or len(price_series) < ma_period:
        return 50.0, 0.0
    
    current = price_series.iloc[-1]
    ma = price_series.rolling(window=ma_period).mean().iloc[-1]
    
    if pd.isna(ma) or ma == 0:
        return 50.0, 0.0
    
    deviation_pct = ((current - ma) / ma) * 100
    
    # 乖離率をスコア化
    if deviation_pct > 20:
        score = 95  # 極端な過熱
    elif deviation_pct > 10:
        score = 75 + (deviation_pct - 10) * 2  # 75-95
    elif deviation_pct > 0:
        score = 55 + deviation_pct * 2  # 55-75
    elif deviation_pct > -10:
        score = 35 + (deviation_pct + 10) * 2  # 35-55
    else:
        score = max(10, 35 + deviation_pct)  # 10-35
    
    return float(np.clip(score, 0, 100)), deviation_pct


def score_consumer_sentiment(value: float, series: Optional[pd.Series] = None) -> float:
    """
    ミシガン大消費者信頼感をスコア化
    
    基準 (UMCSENT):
    - > 100: 非常に楽観的 → 高スコア
    - 80-100: 正常範囲 → 中立～やや高い
    - 60-80: 悲観的 → やや低い
    - < 60: 非常に悲観的 → 低スコア
    
    歴史的範囲: 約50-115
    """
    if pd.isna(value):
        return 50.0
    
    # パーセンタイルも考慮（あれば）
    if series is not None and len(series) > 30:
        return get_percentile_rank(series, value)
    
    # 固定基準でスコア化 (50-115 → 0-100にマップ)
    if value >= 100:
        score = 80 + (value - 100) * 1.33  # 80-100
    elif value >= 80:
        score = 50 + (value - 80) * 1.5  # 50-80
    elif value >= 60:
        score = 20 + (value - 60) * 1.5  # 20-50
    else:
        score = max(0, 20 - (60 - value))  # 0-20
    
    return float(np.clip(score, 0, 100))


def score_nfci(value: float, series: Optional[pd.Series] = None) -> float:
    """
    シカゴ連銀金融環境指数（NFCI）をスコア化（逆スコア）
    
    NFCI基準:
    - < -0.5: 緩和的 → 高スコア（市場に好環境）
    - -0.5 to 0: やや緩和～中立 → やや高い
    - 0 to 0.5: やや引き締め → やや低い
    - > 0.5: 引き締め → 低スコア（市場にストレス）
    - > 1.5: 危機レベル → 非常に低スコア
    
    逆スコア: NFCIが低い（緩和）ほど市場に好ましい = 高スコア
    """
    if pd.isna(value):
        return 50.0
    
    # 逆スコア化: -1.5 to +2.0 → 100 to 0
    # NFCI = 0 が中立(50点)
    if value < -1.0:
        score = 95  # 非常に緩和
    elif value < -0.5:
        score = 75 + (-0.5 - value) * 40  # 75-95
    elif value < 0:
        score = 50 + (-value) * 50  # 50-75
    elif value < 0.5:
        score = 50 - value * 40  # 30-50
    elif value < 1.5:
        score = 30 - (value - 0.5) * 20  # 10-30
    else:
        score = max(0, 10 - (value - 1.5) * 10)  # 0-10
    
    return float(np.clip(score, 0, 100))


def calculate_sentiment_score(data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    センチメントスコアを計算（3本柱）
    
    Args:
        data: データ辞書
            'VIX': VIX値またはSeries
            'ConsumerSent': ミシガン大消費者信頼感
            'NFCI': シカゴ連銀金融環境指数
    
    Returns:
        (総合スコア, 詳細辞書)
    """
    # 3本柱: VIX 35%, NFCI 35%, ConsumerSent 30%
    
    details = {
        'vix': {'value': None, 'score': None, 'weight': 0.35},
        'nfci': {'value': None, 'score': None, 'weight': 0.35},
        'consumer_sent': {'value': None, 'score': None, 'weight': 0.30},
        'components_available': 0,
        'data_quality': 'unknown'
    }
    
    weighted_sum = 0.0
    total_weight = 0.0
    
    # --- 1. VIX (35%) ---
    vix_data = data.get('VIX')
    if vix_data is not None:
        if isinstance(vix_data, pd.Series) and len(vix_data) > 0:
            vix_val = vix_data.iloc[-1]
            vix_series = vix_data
        elif isinstance(vix_data, (int, float)):
            vix_val = float(vix_data)
            vix_series = None
        else:
            vix_val = None
            vix_series = None
        
        if vix_val is not None and not pd.isna(vix_val):
            details['vix']['value'] = vix_val
            vix_score = score_vix(vix_val, vix_series)
            details['vix']['score'] = vix_score
            weighted_sum += vix_score * 0.35
            total_weight += 0.35
            details['components_available'] += 1
    
    # --- 2. NFCI (35%) ---
    nfci_data = data.get('NFCI')
    if nfci_data is not None:
        if isinstance(nfci_data, pd.Series) and len(nfci_data) > 0:
            nfci_val = nfci_data.iloc[-1]
            nfci_series = nfci_data
        elif isinstance(nfci_data, (int, float)):
            nfci_val = float(nfci_data)
            nfci_series = None
        else:
            nfci_val = None
            nfci_series = None
        
        if nfci_val is not None and not pd.isna(nfci_val):
            details['nfci']['value'] = nfci_val
            nfci_score = score_nfci(nfci_val, nfci_series)
            details['nfci']['score'] = nfci_score
            weighted_sum += nfci_score * 0.35
            total_weight += 0.35
            details['components_available'] += 1
    
    # --- 3. Consumer Sentiment (30%) ---
    cs_data = data.get('ConsumerSent')
    if cs_data is not None:
        if isinstance(cs_data, pd.Series) and len(cs_data) > 0:
            cs_val = cs_data.iloc[-1]
            cs_series = cs_data
        elif isinstance(cs_data, (int, float)):
            cs_val = float(cs_data)
            cs_series = None
        else:
            cs_val = None
            cs_series = None
        
        if cs_val is not None and not pd.isna(cs_val):
            details['consumer_sent']['value'] = cs_val
            cs_score = score_consumer_sentiment(cs_val, cs_series)
            details['consumer_sent']['score'] = cs_score
            weighted_sum += cs_score * 0.30
            total_weight += 0.30
            details['components_available'] += 1
    
    # --- 総合スコア計算 ---
    if total_weight > 0:
        # 利用可能なコンポーネントで正規化
        final_score = weighted_sum / total_weight
        final_score = np.clip(final_score, 0, 100)
    else:
        final_score = 50.0
    
    # データ品質判定（3本柱）
    if details['components_available'] >= 3:
        details['data_quality'] = 'good'
    elif details['components_available'] >= 2:
        details['data_quality'] = 'partial'
    else:
        details['data_quality'] = 'insufficient'
    
    return float(final_score), details


def interpret_sentiment_score(score: float) -> Dict[str, str]:
    """
    センチメントスコアを解釈（Howard Marks流）
    
    Returns:
        {'level': str, 'label': str, 'label_en': str, 'color': str, 'description': str}
    """
    if score >= 75:
        return {
            'level': 'greed',
            'label': '過熱警戒',
            'label_en': 'Greed (Caution)',
            'color': 'orange',
            'description': '市場は楽観的。Howard Marks流では逆張りを検討する局面。'
        }
    elif score >= 55:
        return {
            'level': 'optimistic',
            'label': '楽観',
            'label_en': 'Optimistic',
            'color': 'lightgreen',
            'description': 'ポジティブなセンチメント。トレンドフォローは妥当。'
        }
    elif score >= 45:
        return {
            'level': 'neutral',
            'label': '中立',
            'label_en': 'Neutral',
            'color': 'yellow',
            'description': 'センチメントはバランス状態。'
        }
    elif score >= 25:
        return {
            'level': 'pessimistic',
            'label': '悲観',
            'label_en': 'Pessimistic',
            'color': 'orange',
            'description': '市場は慎重。割安機会を探す局面かも。'
        }
    else:
        return {
            'level': 'fear',
            'label': '恐怖',
            'label_en': 'Fear',
            'color': 'red',
            'description': '極端な悲観。Howard Marks流では逆張り買いの好機かも。'
        }


# =============================================================================
# テスト用
# =============================================================================
if __name__ == '__main__':
    # テストデータ（実データのみ使用）
    dates = pd.date_range('2023-01-01', periods=300, freq='D')
    
    test_data = {
        'VIX': pd.Series(np.random.normal(18, 5, 300), index=dates),
        'ConsumerSent': pd.Series(np.random.normal(70, 10, 300), index=dates),
        'NFCI': pd.Series(np.random.normal(-0.2, 0.3, 300), index=dates),
    }
    
    score, details = calculate_sentiment_score(test_data)
    interpretation = interpret_sentiment_score(score)
    
    print(f"Sentiment Score: {score:.1f}")
    print(f"Interpretation: {interpretation['label']} ({interpretation['level']})")
    print(f"Components available: {details['components_available']}/3")
    print(f"Data quality: {details['data_quality']}")
