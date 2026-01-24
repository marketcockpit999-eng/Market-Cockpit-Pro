# -*- coding: utf-8 -*-
"""
MARKET VERDICT - Multi-Asset Score Calculator
================================================================================
Phase 5: 株式・ゴールド・BTCの3資産クラス別スコア計算

設計哲学（4人の巨人）:
  - Druckenmiller: 流動性が全てを動かす
  - Howell: Net Liq = Fed - TGA - RRP（BTCとの相関が強い）
  - Dalio: サイクルの位置を知れ
  - Marks: 振り子の極端を避けよ

使用方法:
  from utils.verdict_assets import calculate_multi_asset_verdict
  verdicts = calculate_multi_asset_verdict(data)
================================================================================
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional


# =============================================================================
# ASSET-SPECIFIC WEIGHTS
# =============================================================================

# 株式: 流動性・サイクル・テクニカル・センチメント
STOCK_WEIGHTS = {
    'liquidity': 0.35,
    'cycle': 0.25,
    'technical': 0.25,
    'sentiment': 0.15,
}

# ゴールド: 実質金利（逆相関）・不確実性・テクニカル・ドル（逆相関）
GOLD_WEIGHTS = {
    'real_rate': 0.40,      # 実質金利（逆相関）← 最重要
    'uncertainty': 0.25,    # VIX / 不確実性
    'technical': 0.20,      # ゴールドのMA/RSI
    'dxy': 0.15,            # ドル指数（逆相関）
}

# BTC: 流動性（Howell）・テクニカル・Cryptoセンチメント・ドル
BTC_WEIGHTS = {
    'liquidity': 0.45,      # 流動性が最重要（Howell研究）
    'technical': 0.25,      # BTCのMA/RSI
    'crypto_sentiment': 0.20,  # Crypto Fear & Greed
    'dxy': 0.10,            # ドル指数（逆相関）
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_latest_value(data: Any) -> Optional[float]:
    """データから最新値を取得"""
    if data is None:
        return None
    if isinstance(data, pd.Series):
        if len(data) == 0:
            return None
        val = data.dropna().iloc[-1] if len(data.dropna()) > 0 else None
        return float(val) if val is not None and not pd.isna(val) else None
    if isinstance(data, (int, float)):
        return float(data) if not pd.isna(data) else None
    return None


def calculate_real_rate(nominal_rate: float, breakeven: float) -> float:
    """
    実質金利を計算
    
    実質金利 = 名目金利 - 期待インフレ率
    """
    if nominal_rate is None or breakeven is None:
        return None
    return nominal_rate - breakeven


def score_real_rate_for_gold(real_rate: float) -> float:
    """
    実質金利をゴールド用スコアに変換（逆相関）
    
    実質金利↑ → ゴールド↓ → 低スコア
    実質金利↓ → ゴールド↑ → 高スコア
    
    基準:
    - +3%以上: 極めて高い実質金利 → ゴールドに逆風 → 0-20
    - +1.5~+3%: 高い実質金利 → 20-40
    - 0~+1.5%: 中立域 → 40-60
    - -1.5~0%: 低い実質金利 → ゴールドに追い風 → 60-80
    - -1.5%以下: 極めて低い/マイナス → ゴールドに強い追い風 → 80-100
    """
    if real_rate is None:
        return 50.0
    
    # 逆相関: 実質金利が低いほど高スコア
    if real_rate >= 3.0:
        score = 10
    elif real_rate >= 1.5:
        score = 20 + (3.0 - real_rate) / 1.5 * 20  # 20-40
    elif real_rate >= 0:
        score = 40 + (1.5 - real_rate) / 1.5 * 20  # 40-60
    elif real_rate >= -1.5:
        score = 60 + (-real_rate) / 1.5 * 20  # 60-80
    else:
        score = 80 + min(20, (-real_rate - 1.5) * 10)  # 80-100
    
    return float(np.clip(score, 0, 100))


def score_dxy_inverse(dxy_value: float, dxy_series: Optional[pd.Series] = None) -> float:
    """
    DXY（ドル指数）を逆相関スコアに変換
    
    ドル高 → ゴールド/BTC安 → 低スコア
    ドル安 → ゴールド/BTC高 → 高スコア
    
    基準 (DXY typical range: 90-110):
    - 110以上: 極端なドル高 → 10-20
    - 105-110: ドル高 → 20-40
    - 100-105: やや強い → 40-50
    - 95-100: 中立 → 50-60
    - 90-95: やや弱い → 60-80
    - 90以下: ドル安 → 80-100
    """
    if dxy_value is None:
        return 50.0
    
    if dxy_value >= 110:
        score = 15
    elif dxy_value >= 105:
        score = 20 + (110 - dxy_value) / 5 * 20  # 20-40
    elif dxy_value >= 100:
        score = 40 + (105 - dxy_value) / 5 * 10  # 40-50
    elif dxy_value >= 95:
        score = 50 + (100 - dxy_value) / 5 * 10  # 50-60
    elif dxy_value >= 90:
        score = 60 + (95 - dxy_value) / 5 * 20  # 60-80
    else:
        score = 80 + min(20, (90 - dxy_value) * 2)  # 80-100
    
    return float(np.clip(score, 0, 100))


def score_vix_for_gold(vix_value: float) -> float:
    """
    VIXをゴールド用スコアに変換
    
    ゴールドは安全資産なので、VIX高（恐怖）→ ゴールド買い → 高スコア
    
    基準:
    - VIX < 15: 低ボラ（リスクオン）→ ゴールドに逆風 → 30-40
    - VIX 15-20: 正常 → 中立 → 40-55
    - VIX 20-30: 警戒 → ゴールドに追い風 → 55-75
    - VIX > 30: 恐怖 → ゴールドに強い追い風 → 75-90
    """
    if vix_value is None:
        return 50.0
    
    if vix_value < 15:
        score = 30 + vix_value / 15 * 10  # 30-40
    elif vix_value < 20:
        score = 40 + (vix_value - 15) / 5 * 15  # 40-55
    elif vix_value < 30:
        score = 55 + (vix_value - 20) / 10 * 20  # 55-75
    else:
        score = 75 + min(15, (vix_value - 30) / 10 * 15)  # 75-90
    
    return float(np.clip(score, 0, 100))


def calculate_technical_score_for_asset(price_series: pd.Series) -> Tuple[float, Dict]:
    """
    任意の資産のテクニカルスコアを計算
    
    既存のverdict_technical.pyと同じロジックを使用
    """
    from utils.verdict_technical import calculate_technical_score
    return calculate_technical_score(price_series)


# =============================================================================
# MAIN ASSET VERDICT FUNCTIONS
# =============================================================================

def calculate_stock_verdict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    株式（S&P500）のVERDICTを計算
    
    これは既存のverdict_main.pyとほぼ同じロジック
    """
    # 既存のverdict_mainを使用
    from utils.verdict_main import calculate_market_verdict
    
    verdict = calculate_market_verdict(data)
    
    return {
        'asset': 'stock',
        'asset_label': '📈 株式',
        'asset_label_en': '📈 Stocks',
        'score': verdict['verdict_score'],
        'label': verdict['verdict_label'],
        'label_en': verdict['verdict_label_en'],
        'color': verdict['verdict_color'],
        'pillars': verdict['pillars'],
        'data_quality': verdict['data_quality'],
    }


def calculate_gold_verdict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ゴールドのVERDICTを計算
    
    構成:
    - 実質金利（逆相関）: 40%
    - VIX/不確実性: 25%
    - テクニカル: 20%
    - DXY（逆相関）: 15%
    """
    result = {
        'asset': 'gold',
        'asset_label': '🥇 ゴールド',
        'asset_label_en': '🥇 Gold',
        'score': 50.0,
        'label': '中立',
        'label_en': 'Neutral',
        'color': 'yellow',
        'pillars': {},
        'data_quality': 'unknown',
    }
    
    weighted_sum = 0.0
    total_weight = 0.0
    pillars_available = 0
    
    # --- 1. 実質金利スコア (40%) ---
    us_tnx = get_latest_value(data.get('US_TNX'))
    breakeven = get_latest_value(data.get('Breakeven_10Y'))
    
    if us_tnx is not None and breakeven is not None:
        real_rate = calculate_real_rate(us_tnx, breakeven)
        real_rate_score = score_real_rate_for_gold(real_rate)
        result['pillars']['real_rate'] = {
            'score': real_rate_score,
            'weight': GOLD_WEIGHTS['real_rate'],
            'value': real_rate,
            'us_tnx': us_tnx,
            'breakeven': breakeven,
            'interpretation': _interpret_real_rate_score(real_rate_score),
        }
        weighted_sum += real_rate_score * GOLD_WEIGHTS['real_rate']
        total_weight += GOLD_WEIGHTS['real_rate']
        pillars_available += 1
    
    # --- 2. 不確実性/VIXスコア (25%) ---
    vix = get_latest_value(data.get('VIX'))
    if vix is not None:
        vix_score = score_vix_for_gold(vix)
        result['pillars']['uncertainty'] = {
            'score': vix_score,
            'weight': GOLD_WEIGHTS['uncertainty'],
            'value': vix,
            'interpretation': _interpret_uncertainty_score(vix_score),
        }
        weighted_sum += vix_score * GOLD_WEIGHTS['uncertainty']
        total_weight += GOLD_WEIGHTS['uncertainty']
        pillars_available += 1
    
    # --- 3. テクニカルスコア (20%) ---
    gold_price = data.get('Gold')
    if gold_price is not None and isinstance(gold_price, pd.Series) and len(gold_price) >= 50:
        tech_score, tech_details = calculate_technical_score_for_asset(gold_price)
        result['pillars']['technical'] = {
            'score': tech_score,
            'weight': GOLD_WEIGHTS['technical'],
            'details': tech_details,
            'interpretation': _interpret_technical_score(tech_score),
        }
        weighted_sum += tech_score * GOLD_WEIGHTS['technical']
        total_weight += GOLD_WEIGHTS['technical']
        pillars_available += 1
    
    # --- 4. DXYスコア（逆相関）(15%) ---
    dxy = get_latest_value(data.get('DXY'))
    if dxy is not None:
        dxy_score = score_dxy_inverse(dxy)
        result['pillars']['dxy'] = {
            'score': dxy_score,
            'weight': GOLD_WEIGHTS['dxy'],
            'value': dxy,
            'interpretation': _interpret_dxy_score(dxy_score),
        }
        weighted_sum += dxy_score * GOLD_WEIGHTS['dxy']
        total_weight += GOLD_WEIGHTS['dxy']
        pillars_available += 1
    
    # --- 総合スコア計算 ---
    if total_weight > 0:
        final_score = weighted_sum / total_weight
        final_score = float(np.clip(final_score, 0, 100))
    else:
        final_score = 50.0
    
    result['score'] = final_score
    result['pillars_available'] = pillars_available
    
    # 解釈
    interp = _interpret_asset_verdict(final_score)
    result['label'] = interp['label']
    result['label_en'] = interp['label_en']
    result['color'] = interp['color']
    
    # データ品質
    if pillars_available >= 4:
        result['data_quality'] = 'good'
    elif pillars_available >= 2:
        result['data_quality'] = 'partial'
    else:
        result['data_quality'] = 'insufficient'
    
    return result


def calculate_btc_verdict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    BTCのVERDICTを計算
    
    構成:
    - 流動性: 45% (Howell: Net Liquidity = Fed - TGA - RRP)
    - テクニカル: 25%
    - Cryptoセンチメント: 20% (Fear & Greed)
    - DXY（逆相関）: 10%
    """
    result = {
        'asset': 'btc',
        'asset_label': '₿ ビットコイン',
        'asset_label_en': '₿ Bitcoin',
        'score': 50.0,
        'label': '中立',
        'label_en': 'Neutral',
        'color': 'yellow',
        'pillars': {},
        'data_quality': 'unknown',
    }
    
    weighted_sum = 0.0
    total_weight = 0.0
    pillars_available = 0
    
    # --- 1. 流動性スコア (45%) ---
    liq_data = data.get('liquidity_data', {})
    if liq_data:
        from utils.verdict_liquidity import calculate_liquidity_score, interpret_liquidity_score
        liq_score, liq_details = calculate_liquidity_score(liq_data)
        liq_interp = interpret_liquidity_score(liq_score)
        result['pillars']['liquidity'] = {
            'score': liq_score,
            'weight': BTC_WEIGHTS['liquidity'],
            'details': liq_details,
            'interpretation': liq_interp,
        }
        weighted_sum += liq_score * BTC_WEIGHTS['liquidity']
        total_weight += BTC_WEIGHTS['liquidity']
        pillars_available += 1
    
    # --- 2. テクニカルスコア (25%) ---
    btc_price = data.get('BTC')
    if btc_price is not None and isinstance(btc_price, pd.Series) and len(btc_price) >= 50:
        tech_score, tech_details = calculate_technical_score_for_asset(btc_price)
        result['pillars']['technical'] = {
            'score': tech_score,
            'weight': BTC_WEIGHTS['technical'],
            'details': tech_details,
            'interpretation': _interpret_technical_score(tech_score),
        }
        weighted_sum += tech_score * BTC_WEIGHTS['technical']
        total_weight += BTC_WEIGHTS['technical']
        pillars_available += 1
    
    # --- 3. Cryptoセンチメント (20%) ---
    # TODO: Phase 5.2 で Crypto Fear & Greed API を追加
    # 現時点ではスキップ（将来対応）
    crypto_fg = data.get('crypto_fear_greed')
    if crypto_fg is not None:
        fg_score = _score_crypto_fear_greed(crypto_fg)
        result['pillars']['crypto_sentiment'] = {
            'score': fg_score,
            'weight': BTC_WEIGHTS['crypto_sentiment'],
            'value': crypto_fg,
            'interpretation': _interpret_crypto_sentiment(fg_score),
        }
        weighted_sum += fg_score * BTC_WEIGHTS['crypto_sentiment']
        total_weight += BTC_WEIGHTS['crypto_sentiment']
        pillars_available += 1
    
    # --- 4. DXYスコア（逆相関）(10%) ---
    dxy = get_latest_value(data.get('DXY'))
    if dxy is not None:
        dxy_score = score_dxy_inverse(dxy)
        result['pillars']['dxy'] = {
            'score': dxy_score,
            'weight': BTC_WEIGHTS['dxy'],
            'value': dxy,
            'interpretation': _interpret_dxy_score(dxy_score),
        }
        weighted_sum += dxy_score * BTC_WEIGHTS['dxy']
        total_weight += BTC_WEIGHTS['dxy']
        pillars_available += 1
    
    # --- 総合スコア計算 ---
    if total_weight > 0:
        final_score = weighted_sum / total_weight
        final_score = float(np.clip(final_score, 0, 100))
    else:
        final_score = 50.0
    
    result['score'] = final_score
    result['pillars_available'] = pillars_available
    
    # 解釈
    interp = _interpret_asset_verdict(final_score)
    result['label'] = interp['label']
    result['label_en'] = interp['label_en']
    result['color'] = interp['color']
    
    # データ品質
    if pillars_available >= 3:
        result['data_quality'] = 'good'
    elif pillars_available >= 2:
        result['data_quality'] = 'partial'
    else:
        result['data_quality'] = 'insufficient'
    
    return result


def calculate_multi_asset_verdict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    3資産クラスのVERDICTを計算し、ランキングを生成
    
    Returns:
        {
            'stock': {...},
            'gold': {...},
            'btc': {...},
            'ranking': ['btc', 'stock', 'gold'],  # スコア順
            'recommendation': '現環境では: BTC > 株式 > ゴールド'
        }
    """
    # 各資産のVERDICT計算
    stock_verdict = calculate_stock_verdict(data)
    gold_verdict = calculate_gold_verdict(data)
    btc_verdict = calculate_btc_verdict(data)
    
    # ランキング生成
    assets = [
        ('stock', stock_verdict['score'], stock_verdict['asset_label']),
        ('gold', gold_verdict['score'], gold_verdict['asset_label']),
        ('btc', btc_verdict['score'], btc_verdict['asset_label']),
    ]
    
    # スコア降順でソート
    sorted_assets = sorted(assets, key=lambda x: x[1], reverse=True)
    ranking = [a[0] for a in sorted_assets]
    
    # 推奨文生成
    from utils.i18n import t
    labels = [a[2] for a in sorted_assets]
    recommendation = t('verdict_ranking_format', first=labels[0], second=labels[1], third=labels[2])
    recommendation_en = f"Current environment favors: {sorted_assets[0][0].upper()} > {sorted_assets[1][0].upper()} > {sorted_assets[2][0].upper()}"
    
    return {
        'stock': stock_verdict,
        'gold': gold_verdict,
        'btc': btc_verdict,
        'ranking': ranking,
        'recommendation': recommendation,
        'recommendation_en': recommendation_en,
    }


# =============================================================================
# INTERPRETATION HELPERS
# =============================================================================

def _interpret_asset_verdict(score: float) -> Dict[str, str]:
    """資産VERDICTを解釈"""
    if score >= 75:
        return {'level': 'bullish', 'label': '強気', 'label_en': 'Bullish', 'color': 'green'}
    elif score >= 60:
        return {'level': 'moderately_bullish', 'label': 'やや強気', 'label_en': 'Moderately Bullish', 'color': 'lightgreen'}
    elif score >= 45:
        return {'level': 'neutral', 'label': '中立', 'label_en': 'Neutral', 'color': 'yellow'}
    elif score >= 30:
        return {'level': 'cautious', 'label': '注意', 'label_en': 'Caution', 'color': 'orange'}
    else:
        return {'level': 'bearish', 'label': '警戒', 'label_en': 'Bearish', 'color': 'red'}


def _interpret_real_rate_score(score: float) -> Dict[str, str]:
    """実質金利スコアを解釈"""
    if score >= 70:
        return {'label': '追い風', 'label_en': 'Tailwind', 'color': 'green'}
    elif score >= 50:
        return {'label': '中立', 'label_en': 'Neutral', 'color': 'yellow'}
    else:
        return {'label': '逆風', 'label_en': 'Headwind', 'color': 'red'}


def _interpret_uncertainty_score(score: float) -> Dict[str, str]:
    """不確実性スコアを解釈"""
    if score >= 65:
        return {'label': '恐怖（買い場）', 'label_en': 'Fear (Opportunity)', 'color': 'green'}
    elif score >= 45:
        return {'label': '中立', 'label_en': 'Neutral', 'color': 'yellow'}
    else:
        return {'label': '楽観（警戒）', 'label_en': 'Complacency', 'color': 'orange'}


def _interpret_technical_score(score: float) -> Dict[str, str]:
    """テクニカルスコアを解釈"""
    if score >= 65:
        return {'label': '強気', 'label_en': 'Bullish', 'color': 'green'}
    elif score >= 45:
        return {'label': '中立', 'label_en': 'Neutral', 'color': 'yellow'}
    else:
        return {'label': '弱気', 'label_en': 'Bearish', 'color': 'red'}


def _interpret_dxy_score(score: float) -> Dict[str, str]:
    """DXYスコアを解釈"""
    if score >= 65:
        return {'label': 'ドル安（追い風）', 'label_en': 'Weak Dollar (Tailwind)', 'color': 'green'}
    elif score >= 45:
        return {'label': '中立', 'label_en': 'Neutral', 'color': 'yellow'}
    else:
        return {'label': 'ドル高（逆風）', 'label_en': 'Strong Dollar (Headwind)', 'color': 'red'}


def _score_crypto_fear_greed(fg_value: int) -> float:
    """
    Crypto Fear & Greed Index (0-100) をスコアに変換
    
    Howard Marks流: 極端な恐怖 = 買い場、極端な欲 = 警戒
    
    F&G Index:
    - 0-24: Extreme Fear → 逆張り買いチャンス → 高スコア
    - 25-44: Fear → やや買い場 → やや高スコア
    - 45-54: Neutral → 中立
    - 55-74: Greed → やや警戒
    - 75-100: Extreme Greed → 逆張り警戒 → 低スコア
    """
    if fg_value is None:
        return 50.0
    
    # 逆張りロジック
    if fg_value <= 24:
        score = 80 + (24 - fg_value) / 24 * 20  # 80-100
    elif fg_value <= 44:
        score = 60 + (44 - fg_value) / 20 * 20  # 60-80
    elif fg_value <= 54:
        score = 50 + (54 - fg_value) / 10 * 10  # 50-60 (roughly)
    elif fg_value <= 74:
        score = 30 + (74 - fg_value) / 20 * 20  # 30-50
    else:
        score = max(10, 30 - (fg_value - 74) / 26 * 20)  # 10-30
    
    return float(np.clip(score, 0, 100))


def _interpret_crypto_sentiment(score: float) -> Dict[str, str]:
    """Cryptoセンチメントスコアを解釈"""
    if score >= 70:
        return {'label': '極度の恐怖（買い場）', 'label_en': 'Extreme Fear (Opportunity)', 'color': 'green'}
    elif score >= 50:
        return {'label': '中立', 'label_en': 'Neutral', 'color': 'yellow'}
    else:
        return {'label': '過熱（警戒）', 'label_en': 'Overheated (Caution)', 'color': 'orange'}


# =============================================================================
# TEST
# =============================================================================
if __name__ == '__main__':
    import pandas as pd
    
    # ダミーデータ
    dates = pd.date_range('2023-01-01', periods=300, freq='D')
    
    test_data = {
        # 流動性
        'liquidity_data': {
            'Fed_Assets': pd.Series(np.random.normal(7500, 200, 300), index=dates),
            'TGA': pd.Series(np.random.normal(500, 100, 300), index=dates),
            'ON_RRP': pd.Series(np.random.normal(300, 100, 300), index=dates),
            'Reserves': pd.Series(np.random.normal(3200, 150, 300), index=dates),
            'M2SL': pd.Series(np.linspace(20000, 21000, 300), index=dates),
        },
        # サイクル
        'cycle_data': {
            'T10Y2Y': pd.Series(np.random.normal(0.5, 0.3, 300), index=dates),
            'UNRATE': pd.Series(np.linspace(3.8, 4.1, 300), index=dates),
            'Credit_Spread': pd.Series(np.random.normal(2.5, 0.5, 300), index=dates),
        },
        # 価格データ
        'price_data': pd.Series(np.cumsum(np.random.randn(300) * 0.5 + 0.05) + 4500, index=dates),
        'Gold': pd.Series(np.cumsum(np.random.randn(300) * 0.3 + 0.02) + 2000, index=dates),
        'BTC': pd.Series(np.cumsum(np.random.randn(300) * 1.0 + 0.1) + 40000, index=dates),
        'DXY': pd.Series(np.random.normal(103, 2, 300), index=dates),
        # 金利
        'US_TNX': pd.Series(np.random.normal(4.5, 0.3, 300), index=dates),
        'Breakeven_10Y': pd.Series(np.random.normal(2.3, 0.2, 300), index=dates),
        # ボラティリティ
        'VIX': pd.Series(np.random.normal(18, 5, 300), index=dates),
    }
    
    # テスト実行
    result = calculate_multi_asset_verdict(test_data)
    
    print("=" * 60)
    print("MULTI-ASSET VERDICT TEST")
    print("=" * 60)
    
    for asset in ['stock', 'gold', 'btc']:
        v = result[asset]
        print(f"\n{v['asset_label']}: {v['score']:.0f} ({v['label']})")
        print(f"  Data Quality: {v['data_quality']}")
        print(f"  Pillars: {list(v['pillars'].keys())}")
    
    print(f"\n📊 Ranking: {result['ranking']}")
    print(f"💡 {result['recommendation']}")
