# -*- coding: utf-8 -*-
"""
MARKET VERDICT - Sentiment Score Calculator
================================================================================
センチメントスコア（0-100）を計算するモジュール
Howard Marksの「極端を避ける」思想を反映

スコア構成:
  - VIXスコア（逆）× 25%          ← VIX高=Fear=低スコア
  - Credit Spreadスコア（逆）× 25% ← スプレッド拡大=Fear=低スコア
  - MA乖離スコア × 25%             ← MA上=Greed=高スコア
  - AAII Bull-Bear Spread × 25%    ← 強気多い=高スコア

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


def score_aaii_spread(bull_bear_spread: float) -> float:
    """
    AAII Bull-Bear Spreadをスコア化
    
    Howard Marksの逆張り思考:
    - 極端に強気（>30%）: 皆が強気の時こそ注意 → 高スコアだが警告
    - 強気（10-30%）: 楽観的 → まあまあ高スコア
    - 中立（-10〜+10%）: バランス → 中立スコア
    - 弱気（<-10%）: 悲観的 → 逆張り機会 → 低スコア
    """
    if pd.isna(bull_bear_spread):
        return 50.0
    
    # Bull-Bear SpreadをそのままスコアにマップT
    # 範囲: -40% 〜 +40% を 0-100 にマップ
    score = 50 + bull_bear_spread * 1.25  # -40→0, 0→50, +40→100
    
    return float(np.clip(score, 0, 100))


def calculate_sentiment_score(data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """
    センチメントスコアを計算
    
    Args:
        data: データ辞書
            'VIX': VIX値またはSeries
            'Credit_Spread': 信用スプレッド値またはSeries
            'SP500': S&P500価格Series（MA乖離計算用）
            'AAII': {'bullish': float, 'bearish': float} または bull_bear_spread
    
    Returns:
        (総合スコア, 詳細辞書)
    """
    details = {
        'vix': {'value': None, 'score': None, 'weight': 0.25},
        'credit_spread': {'value': None, 'score': None, 'weight': 0.25},
        'ma_deviation': {'value': None, 'score': None, 'weight': 0.25},
        'aaii_spread': {'value': None, 'score': None, 'weight': 0.25},
        'components_available': 0,
        'data_quality': 'unknown'
    }
    
    weighted_sum = 0.0
    total_weight = 0.0
    
    # --- 1. VIX (25%) ---
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
            weighted_sum += vix_score * 0.25
            total_weight += 0.25
            details['components_available'] += 1
    
    # --- 2. Credit Spread (25%) ---
    spread_data = data.get('Credit_Spread')
    if spread_data is not None:
        if isinstance(spread_data, pd.Series) and len(spread_data) > 0:
            spread_val = spread_data.iloc[-1]
            spread_series = spread_data
        elif isinstance(spread_data, (int, float)):
            spread_val = float(spread_data)
            spread_series = None
        else:
            spread_val = None
            spread_series = None
        
        if spread_val is not None and not pd.isna(spread_val):
            details['credit_spread']['value'] = spread_val
            spread_score = score_credit_spread(spread_val, spread_series)
            details['credit_spread']['score'] = spread_score
            weighted_sum += spread_score * 0.25
            total_weight += 0.25
            details['components_available'] += 1
    
    # --- 3. MA Deviation (25%) ---
    sp500_data = data.get('SP500')
    if sp500_data is not None and isinstance(sp500_data, pd.Series) and len(sp500_data) >= 200:
        ma_score, deviation_pct = score_ma_deviation(sp500_data)
        details['ma_deviation']['value'] = deviation_pct
        details['ma_deviation']['deviation_pct'] = deviation_pct
        details['ma_deviation']['score'] = ma_score
        weighted_sum += ma_score * 0.25
        total_weight += 0.25
        details['components_available'] += 1
    
    # --- 4. AAII Bull-Bear Spread (25%) ---
    aaii_data = data.get('AAII')
    if aaii_data is not None:
        if isinstance(aaii_data, dict):
            bullish = aaii_data.get('bullish', 0)
            bearish = aaii_data.get('bearish', 0)
            bull_bear = bullish - bearish
        elif isinstance(aaii_data, (int, float)):
            bull_bear = float(aaii_data)
        else:
            bull_bear = None
        
        if bull_bear is not None:
            details['aaii_spread']['value'] = bull_bear
            aaii_score = score_aaii_spread(bull_bear)
            details['aaii_spread']['score'] = aaii_score
            weighted_sum += aaii_score * 0.25
            total_weight += 0.25
            details['components_available'] += 1
    
    # --- 総合スコア計算 ---
    if total_weight > 0:
        final_score = weighted_sum / total_weight * (total_weight / 1.0)
        final_score = np.clip(final_score, 0, 100)
    else:
        final_score = 50.0
    
    # データ品質判定
    if details['components_available'] >= 4:
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
    # ダミーデータでテスト
    dates = pd.date_range('2023-01-01', periods=300, freq='D')
    
    test_data = {
        'VIX': pd.Series(np.random.normal(18, 5, 300), index=dates),
        'Credit_Spread': pd.Series(np.random.normal(4, 1, 300), index=dates),
        'SP500': pd.Series(np.cumsum(np.random.randn(300) * 0.5 + 0.1) + 4500, index=dates),
        'AAII': {'bullish': 38.5, 'bearish': 28.3},
    }
    
    score, details = calculate_sentiment_score(test_data)
    interpretation = interpret_sentiment_score(score)
    
    print(f"Sentiment Score: {score:.1f}")
    print(f"Interpretation: {interpretation['label']} ({interpretation['level']})")
    print(f"Components available: {details['components_available']}/4")
    print(f"Data quality: {details['data_quality']}")
