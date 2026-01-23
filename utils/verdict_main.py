# -*- coding: utf-8 -*-
"""
MARKET VERDICT - Main Aggregator
================================================================================
3本柱のスコアを統合してMARKET VERDICTを算出

VERDICT = 流動性(40%) + サイクル(30%) + テクニカル(30%)

使用方法:
  from utils.verdict_main import calculate_market_verdict
  verdict = calculate_market_verdict(all_data)
================================================================================
"""

import numpy as np
from typing import Dict, Any, Optional

from utils.verdict_liquidity import calculate_liquidity_score, interpret_liquidity_score
from utils.verdict_cycle import calculate_cycle_score, interpret_cycle_score
from utils.verdict_technical import calculate_technical_score, interpret_technical_score


# ウェイト定義
WEIGHTS = {
    'liquidity': 0.40,
    'cycle': 0.30,
    'technical': 0.30
}


def calculate_market_verdict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    MARKET VERDICTを計算
    
    Args:
        data: 全データ辞書
            'liquidity_data': 流動性用データ
            'cycle_data': サイクル用データ
            'price_data': テクニカル用データ（S&P500）
    
    Returns:
        {
            'verdict_score': float (0-100),
            'verdict_label': str,
            'verdict_color': str,
            'pillars': {
                'liquidity': {...},
                'cycle': {...},
                'technical': {...}
            },
            'data_quality': str
        }
    """
    result = {
        'verdict_score': 50.0,
        'verdict_label': '中立',
        'verdict_label_en': 'Neutral',
        'verdict_color': 'yellow',
        'pillars': {},
        'data_quality': 'unknown'
    }
    
    weighted_sum = 0.0
    total_weight = 0.0
    pillars_available = 0
    
    # --- 1. 流動性スコア (40%) ---
    liq_data = data.get('liquidity_data', {})
    if liq_data:
        liq_score, liq_details = calculate_liquidity_score(liq_data)
        liq_interp = interpret_liquidity_score(liq_score)
        result['pillars']['liquidity'] = {
            'score': liq_score,
            'weight': WEIGHTS['liquidity'],
            'interpretation': liq_interp,
            'details': liq_details
        }
        weighted_sum += liq_score * WEIGHTS['liquidity']
        total_weight += WEIGHTS['liquidity']
        pillars_available += 1
    
    # --- 2. サイクルスコア (30%) ---
    cycle_data = data.get('cycle_data', {})
    if cycle_data:
        cyc_score, cyc_details = calculate_cycle_score(cycle_data)
        cyc_interp = interpret_cycle_score(cyc_score)
        result['pillars']['cycle'] = {
            'score': cyc_score,
            'weight': WEIGHTS['cycle'],
            'interpretation': cyc_interp,
            'details': cyc_details
        }
        weighted_sum += cyc_score * WEIGHTS['cycle']
        total_weight += WEIGHTS['cycle']
        pillars_available += 1
    
    # --- 3. テクニカルスコア (30%) ---
    price_data = data.get('price_data')
    if price_data is not None:
        tech_score, tech_details = calculate_technical_score(price_data)
        tech_interp = interpret_technical_score(tech_score)
        result['pillars']['technical'] = {
            'score': tech_score,
            'weight': WEIGHTS['technical'],
            'interpretation': tech_interp,
            'details': tech_details
        }
        weighted_sum += tech_score * WEIGHTS['technical']
        total_weight += WEIGHTS['technical']
        pillars_available += 1
    
    # --- 総合VERDICT ---
    if total_weight > 0:
        final_score = weighted_sum / total_weight * (total_weight / 1.0)
        final_score = float(np.clip(final_score, 0, 100))
    else:
        final_score = 50.0
    
    result['verdict_score'] = final_score
    
    # 解釈
    verdict_interp = interpret_verdict(final_score)
    result['verdict_label'] = verdict_interp['label']
    result['verdict_label_en'] = verdict_interp['label_en']
    result['verdict_color'] = verdict_interp['color']
    result['verdict_description'] = verdict_interp['description']
    
    # データ品質
    if pillars_available == 3:
        result['data_quality'] = 'good'
    elif pillars_available >= 2:
        result['data_quality'] = 'partial'
    else:
        result['data_quality'] = 'insufficient'
    
    result['pillars_available'] = pillars_available
    
    return result


def interpret_verdict(score: float) -> Dict[str, str]:
    """総合VERDICTを解釈"""
    if score >= 75:
        return {
            'level': 'strong_buy',
            'label': '強気',
            'label_en': 'Bullish',
            'color': 'green',
            'description': '流動性・サイクル・テクニカルが揃って良好。リスクオン環境。'
        }
    elif score >= 60:
        return {
            'level': 'buy',
            'label': 'やや強気',
            'label_en': 'Moderately Bullish',
            'color': 'lightgreen',
            'description': '概ね良好な環境。グロース株・シクリカルに妥当性。'
        }
    elif score >= 45:
        return {
            'level': 'neutral',
            'label': '中立',
            'label_en': 'Neutral',
            'color': 'yellow',
            'description': '混在シグナル。選別的な対応を。'
        }
    elif score >= 30:
        return {
            'level': 'cautious',
            'label': '注意',
            'label_en': 'Caution',
            'color': 'orange',
            'description': '流動性縮小局面。防御セクター・コモディティへのシフトを検討。'
        }
    else:
        return {
            'level': 'bearish',
            'label': '警戒',
            'label_en': 'Bearish',
            'color': 'red',
            'description': '複合的な悪材料。現金・短期債・ゴールド選好。'
        }


def format_verdict_summary(verdict: Dict) -> str:
    """VERDICTの要約テキストを生成"""
    lines = [
        f"📊 MARKET VERDICT: {verdict['verdict_score']:.0f}/100 ({verdict['verdict_label']})",
        ""
    ]
    
    for name, pillar in verdict.get('pillars', {}).items():
        label_map = {'liquidity': '流動性', 'cycle': 'サイクル', 'technical': 'テクニカル'}
        jp_name = label_map.get(name, name)
        interp = pillar.get('interpretation', {})
        lines.append(f"  {jp_name}: {pillar['score']:.0f} ({interp.get('label', '-')})")
    
    return "\n".join(lines)


# =============================================================================
# テスト用
# =============================================================================
if __name__ == '__main__':
    import pandas as pd
    
    # ダミーデータ
    dates = pd.date_range('2023-01-01', periods=600, freq='D')
    
    test_data = {
        'liquidity_data': {
            'Fed_Assets': pd.Series(np.random.normal(7500, 200, 600), index=dates),
            'TGA': pd.Series(np.random.normal(500, 100, 600), index=dates),
            'ON_RRP': pd.Series(np.random.normal(300, 100, 600), index=dates),
            'Reserves': pd.Series(np.random.normal(3200, 150, 600), index=dates),
            'M2SL': pd.Series(np.linspace(20000, 21000, 600), index=dates),
        },
        'cycle_data': {
            'T10Y2Y': pd.Series(np.random.normal(0.5, 0.3, 600), index=dates),
            'UNRATE': pd.Series(np.linspace(3.8, 4.1, 600), index=dates),
            'Credit_Spread': pd.Series(np.random.normal(2.5, 0.5, 600), index=dates),
            'Leading_Index': pd.Series(np.random.normal(0.2, 0.3, 600), index=dates),
        },
        'price_data': pd.Series(np.cumsum(np.random.randn(600) * 0.5 + 0.05) + 4500, index=dates),
    }
    
    verdict = calculate_market_verdict(test_data)
    print(format_verdict_summary(verdict))
    print(f"\nData Quality: {verdict['data_quality']}")
    print(f"Pillars Available: {verdict['pillars_available']}/3")
