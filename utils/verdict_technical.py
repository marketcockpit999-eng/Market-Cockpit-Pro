# -*- coding: utf-8 -*-
"""
MARKET VERDICT - Technical Score Calculator
================================================================================
テクニカルスコア（0-100）を計算するモジュール

スコア構成:
  - 200日MA乖離率 × 40%
  - RSI(14) × 30%
  - 52週レンジ位置 × 30%

使用方法:
  from utils.verdict_technical import calculate_technical_score
  score, details = calculate_technical_score(price_series)
================================================================================
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, Any


def calculate_sma(series: pd.Series, window: int) -> pd.Series:
    """単純移動平均を計算"""
    return series.rolling(window=window, min_periods=window).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> float:
    """RSI(Relative Strength Index)を計算"""
    if series is None or len(series) < period + 1:
        return 50.0
    
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    # 最新値を取得
    last_gain = avg_gain.iloc[-1]
    last_loss = avg_loss.iloc[-1]
    
    if pd.isna(last_gain) or pd.isna(last_loss) or last_loss == 0:
        return 50.0
    
    rs = last_gain / last_loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)


def score_ma_deviation(series: pd.Series, ma_period: int = 200) -> Tuple[float, float]:
    """
    200日MA乖離率をスコア化
    
    Returns:
        (score, deviation_pct)
    """
    if series is None or len(series) < ma_period:
        return 50.0, 0.0
    
    current = series.iloc[-1]
    ma = calculate_sma(series, ma_period).iloc[-1]
    
    if pd.isna(current) or pd.isna(ma) or ma == 0:
        return 50.0, 0.0
    
    deviation_pct = ((current - ma) / ma) * 100
    
    # 乖離率をスコア化
    # -20% ～ +20% を 0 ～ 100 にマップ
    # 0% = 50点、+20%以上 = 100点、-20%以下 = 0点
    score = 50 + (deviation_pct / 20) * 50
    return float(np.clip(score, 0, 100)), float(deviation_pct)


def score_rsi(rsi_value: float) -> float:
    """
    RSIをスコア化
    
    - RSI < 30: 売られすぎ（逆張り買いチャンス）→ 高スコア
    - RSI > 70: 買われすぎ（逆張り売りシグナル）→ 低スコア
    - RSI 30-70: 中立圏
    
    ※逆張り思考: 極端なRSIは逆方向にスコア
    """
    if pd.isna(rsi_value):
        return 50.0
    
    # 逆張りロジック: 売られすぎ=買いチャンス=高スコア
    if rsi_value <= 30:
        # 30→70点, 20→80点, 10→90点
        score = 70 + (30 - rsi_value) * 1.0
    elif rsi_value >= 70:
        # 70→30点, 80→20点, 90→10点
        score = 30 - (rsi_value - 70) * 1.0
    else:
        # 30-70は線形: 30=70点, 50=50点, 70=30点
        score = 70 - (rsi_value - 30) * 1.0
    
    return float(np.clip(score, 0, 100))


def score_52week_position(series: pd.Series) -> Tuple[float, float]:
    """
    52週レンジ内の位置をスコア化
    
    Returns:
        (score, position_pct) - position_pctは0-100%
    """
    if series is None or len(series) < 252:
        return 50.0, 50.0
    
    recent_252 = series.tail(252).dropna()
    if len(recent_252) < 50:
        return 50.0, 50.0
    
    current = series.iloc[-1]
    high_52w = recent_252.max()
    low_52w = recent_252.min()
    
    if pd.isna(current) or high_52w == low_52w:
        return 50.0, 50.0
    
    # 位置を0-100%で計算
    position_pct = ((current - low_52w) / (high_52w - low_52w)) * 100
    
    # スコア化: 高い位置 = 強い = 高スコア（順張り）
    # ただし過度に高い位置は警戒
    if position_pct >= 95:
        score = 80  # 極端に高いと少し減点
    elif position_pct <= 5:
        score = 20  # 極端に低いと低スコア
    else:
        score = position_pct  # 基本は位置=スコア
    
    return float(np.clip(score, 0, 100)), float(position_pct)


def calculate_technical_score(data: Any) -> Tuple[float, Dict[str, Any]]:
    """
    テクニカルスコアを計算
    
    Args:
        data: S&P500の価格データ
            - pd.Series: 価格時系列
            - dict: {'series': pd.Series, 'value': float}
    
    Returns:
        (総合スコア, 詳細辞書)
    """
    details = {
        'ma_deviation': {'value': None, 'deviation_pct': None, 'score': None, 'weight': 0.40},
        'rsi': {'value': None, 'score': None, 'weight': 0.30},
        'position_52w': {'value': None, 'position_pct': None, 'score': None, 'weight': 0.30},
        'components_available': 0,
        'data_quality': 'unknown'
    }
    
    # データ抽出
    if isinstance(data, pd.Series):
        series = data
    elif isinstance(data, dict):
        series = data.get('series') or data.get('data')
    else:
        series = None
    
    if series is None or len(series) < 50:
        return 50.0, details
    
    weighted_sum = 0.0
    total_weight = 0.0
    
    # --- 1. 200日MA乖離 (40%) ---
    if len(series) >= 200:
        ma_score, deviation_pct = score_ma_deviation(series, 200)
        details['ma_deviation']['value'] = series.iloc[-1]
        details['ma_deviation']['deviation_pct'] = deviation_pct
        details['ma_deviation']['score'] = ma_score
        weighted_sum += ma_score * 0.40
        total_weight += 0.40
        details['components_available'] += 1
    
    # --- 2. RSI (30%) ---
    rsi_value = calculate_rsi(series, 14)
    rsi_score = score_rsi(rsi_value)
    details['rsi']['value'] = rsi_value
    details['rsi']['score'] = rsi_score
    weighted_sum += rsi_score * 0.30
    total_weight += 0.30
    details['components_available'] += 1
    
    # --- 3. 52週位置 (30%) ---
    if len(series) >= 252:
        pos_score, pos_pct = score_52week_position(series)
        details['position_52w']['value'] = series.iloc[-1]
        details['position_52w']['position_pct'] = pos_pct
        details['position_52w']['score'] = pos_score
        weighted_sum += pos_score * 0.30
        total_weight += 0.30
        details['components_available'] += 1
    
    # --- 総合スコア ---
    if total_weight > 0:
        final_score = weighted_sum / total_weight * (total_weight / 1.0)
        final_score = np.clip(final_score, 0, 100)
    else:
        final_score = 50.0
    
    # データ品質
    if details['components_available'] >= 3:
        details['data_quality'] = 'good'
    elif details['components_available'] >= 2:
        details['data_quality'] = 'partial'
    else:
        details['data_quality'] = 'insufficient'
    
    return float(final_score), details


def interpret_technical_score(score: float) -> Dict[str, str]:
    """テクニカルスコアを解釈"""
    if score >= 65:
        return {
            'level': 'bullish',
            'label': '強気',
            'label_en': 'Bullish',
            'color': 'green',
            'description': 'テクニカル的に良好。上昇トレンド。'
        }
    elif score >= 45:
        return {
            'level': 'neutral',
            'label': '中立',
            'label_en': 'Neutral',
            'color': 'yellow',
            'description': '方向感模索中。トレンド転換に注意。'
        }
    elif score >= 25:
        return {
            'level': 'cautious',
            'label': '弱気',
            'label_en': 'Cautious',
            'color': 'orange',
            'description': 'テクニカル悪化中。慎重姿勢を。'
        }
    else:
        return {
            'level': 'bearish',
            'label': '警戒',
            'label_en': 'Bearish',
            'color': 'red',
            'description': '下降トレンド。リスク管理優先。'
        }


# =============================================================================
# テスト用
# =============================================================================
if __name__ == '__main__':
    # ダミーデータでテスト（上昇トレンド）
    dates = pd.date_range('2023-01-01', periods=300, freq='D')
    prices = pd.Series(np.cumsum(np.random.randn(300) * 0.5 + 0.1) + 100, index=dates)
    
    score, details = calculate_technical_score(prices)
    interpretation = interpret_technical_score(score)
    
    print(f"Technical Score: {score:.1f}")
    print(f"Interpretation: {interpretation['label']} ({interpretation['level']})")
    print(f"Components: {details['components_available']}/3")
    print(f"\nDetails:")
    print(f"  MA Deviation: {details['ma_deviation']['deviation_pct']:.2f}% → Score: {details['ma_deviation']['score']:.1f}")
    print(f"  RSI: {details['rsi']['value']:.1f} → Score: {details['rsi']['score']:.1f}")
    print(f"  52W Position: {details['position_52w']['position_pct']:.1f}% → Score: {details['position_52w']['score']:.1f}")
