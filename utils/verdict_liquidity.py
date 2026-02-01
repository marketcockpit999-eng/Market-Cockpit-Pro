# -*- coding: utf-8 -*-
"""
MARKET VERDICT - Liquidity Score Calculator
================================================================================
流動性スコア（0-100）を計算するモジュール

V2スコア構成（100点満点）:
  【Tier 1】マクロ流動性環境（50点）
    - Fed資産増減率:     15点
    - ON RRP枯渇度:       15点
    - TGA圧力指数:        20点
  【Tier 2】システミック指標（35点）
    - 銀行準備金偏差:     12点
    - SOFR適正性:         10点
    - M2実質成長率:       13点
  【Tier 3】市場シグナル（15点）
    - CP Spread:          5点
    - MOVE Index:         5点
    - Credit Spread:      5点

使用方法:
  from utils.verdict_liquidity import calculate_liquidity_score_v2
  score, details = calculate_liquidity_score_v2(data_dict)
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


# =============================================================================
# V2 スコア計算関数（Tier 2）
# =============================================================================

def score_reserves_deviation(reserves_series: pd.Series) -> Tuple[float, Dict[str, Any]]:
    """
    準備金の5年平均からの偏差をスコア化（0-12点）
    
    金融的根拠:
      - 2019年レポ危機は準備金不足が原因
      - Fed目安: 最低準備金水準は約2,500B
      - 5年平均からの乖離で「相対的な余裕度」を測定
    
    スコア変換:
      deviation +10%以上 → 12点（準備金潤沢）
      deviation 0～+10% → 9点（平均以上）
      deviation -10%～0% → 6点（平均以下）
      deviation -20%～-10% → 3点（逼迫警告）
      deviation -20%以下 → 0点（危機水準）
    """
    MAX_POINTS = 12
    NEUTRAL_SCORE = MAX_POINTS / 2  # 6
    LOOKBACK_WEEKS = 260  # 約5年
    
    if reserves_series is None or len(reserves_series) < 52:  # 最低1年
        return NEUTRAL_SCORE, {'value': None, 'status': 'insufficient_data'}
    
    current = reserves_series.iloc[-1]
    
    if pd.isna(current):
        return NEUTRAL_SCORE, {'value': None, 'status': 'nan'}
    
    # 5年平均（または利用可能な全期間）
    lookback = min(LOOKBACK_WEEKS, len(reserves_series))
    avg_5y = reserves_series.tail(lookback).mean()
    
    if avg_5y == 0 or pd.isna(avg_5y):
        return NEUTRAL_SCORE, {'value': current, 'status': 'avg_nan'}
    
    deviation_pct = (current - avg_5y) / avg_5y * 100
    
    # スコア変換
    if deviation_pct >= 10:
        score = 12
    elif deviation_pct >= 0:
        score = 9 + (deviation_pct / 10) * 3
    elif deviation_pct >= -10:
        score = 6 + (deviation_pct + 10) / 10 * 3
    elif deviation_pct >= -20:
        score = 3 + (deviation_pct + 20) / 10 * 3
    else:
        score = max(0, 3 + (deviation_pct + 20) / 10 * 3)
    
    return float(np.clip(score, 0, MAX_POINTS)), {
        'value': current,
        'avg_5y': avg_5y,
        'deviation_pct': deviation_pct,
        'status': 'ok'
    }


def score_sofr_appropriateness(sofr_series: pd.Series, 
                                ff_upper_series: pd.Series) -> Tuple[float, Dict[str, Any]]:
    """
    SOFR適正性をスコア化（0-10点）
    
    金融的根拠:
      - SOFRがFF上限を上回る = 短期金融市場のストレス
      - 2019年レポ危機時、SOFRは一時的に急騰
      - 通常、SOFRはFF上限より5-15bp低い
    
    スコア変換:
      spread <= -5bp → 10点（SOFR正常、余裕あり）
      spread -5～0bp → 8点（正常範囲）
      spread 0～+5bp → 6点（タイト気味）
      spread +5～+15bp → 4点（ストレス兆候）
      spread +15bp以上 → 2点（短期市場ストレス）
    """
    MAX_POINTS = 10
    NEUTRAL_SCORE = MAX_POINTS / 2  # 5
    
    if sofr_series is None or ff_upper_series is None:
        return NEUTRAL_SCORE, {'value': None, 'status': 'insufficient_data'}
    
    if len(sofr_series) == 0 or len(ff_upper_series) == 0:
        return NEUTRAL_SCORE, {'value': None, 'status': 'insufficient_data'}
    
    sofr = sofr_series.iloc[-1]
    ff_upper = ff_upper_series.iloc[-1]
    
    if pd.isna(sofr) or pd.isna(ff_upper):
        return NEUTRAL_SCORE, {'value': None, 'status': 'nan'}
    
    # スプレッド計算（bps）
    spread_bps = (sofr - ff_upper) * 100
    
    # スコア変換
    if spread_bps <= -5:
        score = 10
    elif spread_bps <= 0:
        score = 8 + (-spread_bps / 5) * 2
    elif spread_bps <= 5:
        score = 6 - (spread_bps / 5) * 2
    elif spread_bps <= 15:
        score = 4 - (spread_bps - 5) / 10 * 2
    else:
        score = max(0, 2 - (spread_bps - 15) / 10 * 2)
    
    return float(np.clip(score, 0, MAX_POINTS)), {
        'sofr': sofr,
        'ff_upper': ff_upper,
        'spread_bps': spread_bps,
        'status': 'ok'
    }


def score_real_m2_growth(m2_series: pd.Series, 
                          pce_series: pd.Series) -> Tuple[float, Dict[str, Any]]:
    """
    M2実質成長率をスコア化（0-13点）
    
    金融的根拠:
      - 名目M2成長がインフレ率を下回る = 実質流動性縮小
      - 実質M2成長率 = 経済への実質的な流動性供給
      - Michael Howell理論: 実質流動性が資産価格を決定
    
    スコア変換:
      real_growth +5%以上 → 13点（実質拡大）
      real_growth +2～+5% → 10点（穏やかな拡大）
      real_growth 0～+2% → 7点（維持）
      real_growth -3%～0% → 4点（実質縮小）
      real_growth -3%以下 → 1点（大幅な実質縮小）
    """
    MAX_POINTS = 13
    NEUTRAL_SCORE = MAX_POINTS / 2  # 6.5
    
    if m2_series is None or len(m2_series) < 252:  # 1年分
        return NEUTRAL_SCORE, {'value': None, 'status': 'insufficient_data'}
    
    m2_current = m2_series.iloc[-1]
    m2_1y_ago = m2_series.iloc[-252] if len(m2_series) >= 252 else m2_series.iloc[0]
    
    if pd.isna(m2_current) or pd.isna(m2_1y_ago) or m2_1y_ago == 0:
        return NEUTRAL_SCORE, {'value': None, 'status': 'nan'}
    
    m2_yoy = (m2_current - m2_1y_ago) / m2_1y_ago * 100
    
    # CorePCE取得（すでにYoY%として提供）
    if pce_series is not None and len(pce_series) > 0:
        core_pce = pce_series.iloc[-1]
        if pd.isna(core_pce):
            core_pce = 2.5  # デフォルト
    else:
        core_pce = 2.5  # デフォルト
    
    real_growth = m2_yoy - core_pce
    
    # スコア変換
    if real_growth >= 5:
        score = 13
    elif real_growth >= 2:
        score = 10 + (real_growth - 2) / 3 * 3
    elif real_growth >= 0:
        score = 7 + (real_growth / 2) * 3
    elif real_growth >= -3:
        score = 4 + (real_growth + 3) / 3 * 3
    else:
        score = max(0, 1 + (real_growth + 3) / 3 * 3)
    
    return float(np.clip(score, 0, MAX_POINTS)), {
        'm2_yoy': m2_yoy,
        'core_pce': core_pce,
        'real_growth': real_growth,
        'status': 'ok'
    }


# =============================================================================
# V2 スコア計算関数（Tier 3）
# =============================================================================

def score_cp_spread(cp_spread_series: pd.Series) -> Tuple[float, Dict[str, Any]]:
    """
    CPスプレッドをスコア化（0-5点、低スプレッド=高スコア）
    
    金融的根拠:
      - CP-FFスプレッド = 企業の短期資金調達コスト
      - スプレッド拡大 = 企業の資金調達ストレス
      - 2008年、2020年の危機時に急拡大
    
    スコア変換（逆スケール: 低いほど良い）:
      spread < 0.10% → 5点（正常）
      spread 0.10-0.20% → 4点（やや緊張）
      spread 0.20-0.40% → 3点（警戒）
      spread 0.40-0.80% → 2点（ストレス）
      spread > 0.80% → 1点（危機的）
    """
    MAX_POINTS = 5
    NEUTRAL_SCORE = MAX_POINTS / 2  # 2.5
    
    if cp_spread_series is None or len(cp_spread_series) == 0:
        return NEUTRAL_SCORE, {'value': None, 'status': 'insufficient_data'}
    
    current = cp_spread_series.iloc[-1]
    
    if pd.isna(current):
        return NEUTRAL_SCORE, {'value': None, 'status': 'nan'}
    
    # スコア変換（逆スケール）
    if current < 0.10:
        score = 5
    elif current < 0.20:
        score = 4 + (0.20 - current) / 0.10
    elif current < 0.40:
        score = 3 + (0.40 - current) / 0.20
    elif current < 0.80:
        score = 2 + (0.80 - current) / 0.40
    else:
        score = max(0, 1 - (current - 0.80) / 0.40)
    
    return float(np.clip(score, 0, MAX_POINTS)), {
        'value': current,
        'status': 'ok'
    }


def score_move_index(move_series: pd.Series) -> Tuple[float, Dict[str, Any]]:
    """
    MOVE Indexをスコア化（0-5点、低MOVE=高スコア）
    
    金融的根拠:
      - MOVE = 債券市場のVIX
      - 債券ボラ上昇 = 金利不確実性 = 流動性縮小圧力
      - 株式VIXより先行することがある
    
    スコア変換（逆スケール: 低いほど良い）:
      move < 80 → 5点（低ボラ、安定）
      move 80-100 → 4点（通常）
      move 100-120 → 3点（やや高ボラ）
      move 120-150 → 2点（高ボラ、警戒）
      move > 150 → 1点（危機水準）
    """
    MAX_POINTS = 5
    NEUTRAL_SCORE = MAX_POINTS / 2  # 2.5
    
    if move_series is None or len(move_series) == 0:
        return NEUTRAL_SCORE, {'value': None, 'status': 'insufficient_data'}
    
    current = move_series.iloc[-1]
    
    if pd.isna(current):
        return NEUTRAL_SCORE, {'value': None, 'status': 'nan'}
    
    # スコア変換（逆スケール）
    if current < 80:
        score = 5
    elif current < 100:
        score = 4 + (100 - current) / 20
    elif current < 120:
        score = 3 + (120 - current) / 20
    elif current < 150:
        score = 2 + (150 - current) / 30
    else:
        score = max(0, 1 - (current - 150) / 50)
    
    return float(np.clip(score, 0, MAX_POINTS)), {
        'value': current,
        'status': 'ok'
    }


def score_credit_spread(credit_spread_series: pd.Series) -> Tuple[float, Dict[str, Any]]:
    """
    Credit Spreadをスコア化（0-5点）
    
    金融的根拠:
      - HYスプレッド = 信用リスクのバロメーター
      - スプレッド縮小 = リスク選好（ただし行き過ぎは警告）
      - スプレッド拡大 = 信用収縮、流動性縮小
    
    スコア変換（非線形: 3-4%が最適）:
      spread < 3% → 4点（過度の楽観、やや警戒）
      spread 3-4% → 5点（健全な信用環境）
      spread 4-5% → 4点（通常）
      spread 5-7% → 3点（やや警戒）
      spread 7-10% → 2点（信用収縮）
      spread > 10% → 1点（危機）
    """
    MAX_POINTS = 5
    NEUTRAL_SCORE = MAX_POINTS / 2  # 2.5
    
    if credit_spread_series is None or len(credit_spread_series) == 0:
        return NEUTRAL_SCORE, {'value': None, 'status': 'insufficient_data'}
    
    current = credit_spread_series.iloc[-1]
    
    if pd.isna(current):
        return NEUTRAL_SCORE, {'value': None, 'status': 'nan'}
    
    # スコア変換（非線形: 3-4%が最適）
    if current < 3:
        score = 4  # 過度の楽観は減点
    elif current < 4:
        score = 5  # 最適ゾーン
    elif current < 5:
        score = 4 + (5 - current)
    elif current < 7:
        score = 3 + (7 - current) / 2
    elif current < 10:
        score = 2 + (10 - current) / 3
    else:
        score = max(0, 1 - (current - 10) / 5)
    
    return float(np.clip(score, 0, MAX_POINTS)), {
        'value': current,
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
      
      【Tier 2】システミック指標（35点）
        ├─ 銀行準備金偏差:     12点
        ├─ SOFR適正性:         10点
        └─ M2実質成長率:       13点
      
      【Tier 3】市場シグナル（15点）
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
    # Tier 2: システミック指標（35点）
    # =================================================================
    tier2_total = 0
    tier2_components = 0
    
    # 2.1 準備金偏差（12点）
    reserves_series = extract_series('Reserves')
    score, meta = score_reserves_deviation(reserves_series)
    details['tier2']['reserves_deviation']['score'] = score
    details['tier2']['reserves_deviation']['details'] = meta
    if meta.get('status') == 'ok':
        tier2_total += score
        tier2_components += 1
    else:
        tier2_total += score  # 中立スコアも加算
    
    # 2.2 SOFR適正性（10点）
    sofr_series = extract_series('SOFR')
    ff_upper_series = extract_series('FedFundsUpper')
    score, meta = score_sofr_appropriateness(sofr_series, ff_upper_series)
    details['tier2']['sofr_appropriateness']['score'] = score
    details['tier2']['sofr_appropriateness']['details'] = meta
    if meta.get('status') == 'ok':
        tier2_total += score
        tier2_components += 1
    else:
        tier2_total += score
    
    # 2.3 M2実質成長率（13点）
    m2_series = extract_series('M2SL')
    pce_series = extract_series('CorePCE')
    score, meta = score_real_m2_growth(m2_series, pce_series)
    details['tier2']['real_m2_growth']['score'] = score
    details['tier2']['real_m2_growth']['details'] = meta
    if meta.get('status') == 'ok':
        tier2_total += score
        tier2_components += 1
    else:
        tier2_total += score
    
    details['tier2']['subtotal'] = tier2_total
    details['components_available'] += tier2_components
    
    # =================================================================
    # Tier 3: 市場シグナル（15点）
    # =================================================================
    tier3_total = 0
    tier3_components = 0
    
    # 3.1 CP Spread（5点）
    cp_spread_series = extract_series('CP_Spread')
    score, meta = score_cp_spread(cp_spread_series)
    details['tier3']['cp_spread']['score'] = score
    details['tier3']['cp_spread']['details'] = meta
    if meta.get('status') == 'ok':
        tier3_total += score
        tier3_components += 1
    else:
        tier3_total += score  # 中立スコアも加算
    
    # 3.2 MOVE Index（5点）
    move_series = extract_series('MOVE')
    score, meta = score_move_index(move_series)
    details['tier3']['move_index']['score'] = score
    details['tier3']['move_index']['details'] = meta
    if meta.get('status') == 'ok':
        tier3_total += score
        tier3_components += 1
    else:
        tier3_total += score
    
    # 3.3 Credit Spread（5点）
    credit_spread_series = extract_series('Credit_Spread')
    score, meta = score_credit_spread(credit_spread_series)
    details['tier3']['credit_spread']['score'] = score
    details['tier3']['credit_spread']['details'] = meta
    if meta.get('status') == 'ok':
        tier3_total += score
        tier3_components += 1
    else:
        tier3_total += score
    
    details['tier3']['subtotal'] = tier3_total
    details['components_available'] += tier3_components
    
    # =================================================================
    # 総合スコア計算
    # =================================================================
    total_score = (
        details['tier1']['subtotal'] +
        details['tier2']['subtotal'] +
        details['tier3']['subtotal']
    )
    
    details['total_score'] = float(np.clip(total_score, 0, 100))
    
    # データ品質判定（全9指標で判定）
    total_components = tier1_components + tier2_components + tier3_components
    if total_components >= 8:
        details['data_quality'] = 'good'
    elif total_components >= 5:
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
        # Tier 1 data
        'SOMA_Total': pd.Series(np.random.normal(7500, 200, 600), index=dates),
        'TGA': pd.Series(np.random.normal(500, 100, 600), index=dates),
        'ON_RRP': pd.Series(np.random.normal(500, 200, 600), index=dates),
        # Tier 2 data
        'Reserves': pd.Series(np.random.normal(3200, 150, 600), index=dates),
        'M2SL': pd.Series(np.linspace(20000, 21000, 600), index=dates),
        'SOFR': pd.Series(np.random.normal(4.30, 0.05, 600), index=dates),
        'FedFundsUpper': pd.Series(np.full(600, 4.50), index=dates),
        'CorePCE': pd.Series(np.random.normal(2.8, 0.2, 600), index=dates),
        # Tier 3 data
        'CP_Spread': pd.Series(np.random.normal(0.15, 0.05, 600), index=dates),
        'MOVE': pd.Series(np.random.normal(95, 15, 600), index=dates),
        'Credit_Spread': pd.Series(np.random.normal(4.2, 0.5, 600), index=dates),
    }
    
    score, details = calculate_liquidity_score(test_data)
    interpretation = interpret_liquidity_score(score)
    
    print(f"Liquidity Score (v1): {score:.1f}")
    print(f"Interpretation: {interpretation['label']} ({interpretation['level']})")
    print(f"Components available: {details['components_available']}/3")
    print(f"Data quality: {details['data_quality']}")
    
    print("\n" + "="*50)
    print("V2 Score Test (All 9 Indicators)")
    print("="*50)
    
    # V2テスト
    score_v2, details_v2 = calculate_liquidity_score_v2(test_data)
    interpretation_v2 = interpret_liquidity_score(score_v2)
    
    print(f"Liquidity Score (v2): {score_v2:.1f}")
    print(f"Interpretation: {interpretation_v2['label']} ({interpretation_v2['level']})")
    print(f"Components available: {details_v2['components_available']}/9")
    print(f"Data quality: {details_v2['data_quality']}")
    
    print(f"\nTier 1 Details (50 points):")
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
    
    print(f"\nTier 2 Details (35 points):")
    t2 = details_v2['tier2']
    print(f"  Reserves Deviation: {t2['reserves_deviation']['score']:.1f}/12")
    print(f"    -> Value: {t2['reserves_deviation']['details'].get('value', 'N/A')}B")
    print(f"    -> 5Y Avg: {t2['reserves_deviation']['details'].get('avg_5y', 'N/A')}B")
    print(f"    -> Deviation: {t2['reserves_deviation']['details'].get('deviation_pct', 'N/A')}%")
    print(f"  SOFR Appropriateness: {t2['sofr_appropriateness']['score']:.1f}/10")
    print(f"    -> SOFR: {t2['sofr_appropriateness']['details'].get('sofr', 'N/A')}%")
    print(f"    -> FF Upper: {t2['sofr_appropriateness']['details'].get('ff_upper', 'N/A')}%")
    print(f"    -> Spread: {t2['sofr_appropriateness']['details'].get('spread_bps', 'N/A')}bp")
    print(f"  Real M2 Growth: {t2['real_m2_growth']['score']:.1f}/13")
    print(f"    -> M2 YoY: {t2['real_m2_growth']['details'].get('m2_yoy', 'N/A')}%")
    print(f"    -> Core PCE: {t2['real_m2_growth']['details'].get('core_pce', 'N/A')}%")
    print(f"    -> Real Growth: {t2['real_m2_growth']['details'].get('real_growth', 'N/A')}%")
    print(f"  Subtotal: {t2['subtotal']:.1f}/35")
    
    print(f"\nTier 3 Details (15 points):")
    t3 = details_v2['tier3']
    print(f"  CP Spread: {t3['cp_spread']['score']:.1f}/5")
    print(f"    -> Value: {t3['cp_spread']['details'].get('value', 'N/A')}%")
    print(f"  MOVE Index: {t3['move_index']['score']:.1f}/5")
    print(f"    -> Value: {t3['move_index']['details'].get('value', 'N/A')}")
    print(f"  Credit Spread: {t3['credit_spread']['score']:.1f}/5")
    print(f"    -> Value: {t3['credit_spread']['details'].get('value', 'N/A')}%")
    print(f"  Subtotal: {t3['subtotal']:.1f}/15")
    
    print(f"\n" + "="*50)
    print(f"Total Score: {details_v2['total_score']:.1f}/100")
    print(f"="*50)
