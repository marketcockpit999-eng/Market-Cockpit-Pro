# -*- coding: utf-8 -*-
"""
MARKET VERDICT - 市場総合判定ダッシュボード
================================================================================
3本柱（流動性・サイクル・テクニカル）を統合した市場判定スコア

VERDICT = 流動性(40%) + サイクル(30%) + テクニカル(30%)
================================================================================
"""

import streamlit as st
import pandas as pd
from utils.i18n import t
from utils.verdict_main import calculate_market_verdict


def get_color_hex(color_name: str) -> str:
    """色名からHEX値を取得"""
    colors = {
        'green': '#00c853',
        'lightgreen': '#76ff03',
        'yellow': '#ffd600',
        'orange': '#ff9100',
        'red': '#ff1744',
    }
    return colors.get(color_name, '#ffd600')


def render_verdict_gauge(score: float, label: str, color: str):
    """総合VERDICTゲージを描画"""
    hex_color = get_color_hex(color)
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(145deg, #1a1a2e, #16213e); border-radius: 16px; margin-bottom: 1rem;">
        <h1 style="font-size: 5rem; color: {hex_color}; margin: 0;">{score:.0f}</h1>
        <p style="font-size: 1.5rem; color: {hex_color}; margin: 0.5rem 0;">{label}</p>
        <div style="background: #2d2d44; border-radius: 10px; height: 20px; margin-top: 1rem;">
            <div style="background: linear-gradient(90deg, #ff1744 0%, #ffd600 50%, #00c853 100%); width: {score}%; height: 100%; border-radius: 10px;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #888; margin-top: 0.3rem;">
            <span>0 (警戒)</span><span>50 (中立)</span><span>100 (強気)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_pillar_card(name: str, pillar: dict, lang: str):
    """3本柱カードを描画"""
    icons = {'liquidity': '💧', 'cycle': '🔄', 'technical': '📈'}
    labels = {
        'en': {'liquidity': 'Liquidity', 'cycle': 'Cycle', 'technical': 'Technical'},
        'ja': {'liquidity': '流動性', 'cycle': 'サイクル', 'technical': 'テクニカル'}
    }
    
    score = pillar.get('score', 50)
    interp = pillar.get('interpretation', {})
    label = interp.get('label', '-')
    color = get_color_hex(interp.get('color', 'yellow'))
    weight = int(pillar.get('weight', 0) * 100)
    
    st.markdown(f"""
    <div style="background: #1e1e2f; padding: 1.2rem; border-radius: 12px; border-left: 4px solid {color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 1.1rem;">{icons.get(name, '')} {labels.get(lang, labels['en']).get(name, name)}</span>
            <span style="font-size: 0.8rem; color: #888;">{weight}%</span>
        </div>
        <div style="font-size: 2.5rem; color: {color}; margin: 0.5rem 0;">{score:.0f}</div>
        <div style="color: {color}; font-size: 0.9rem;">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def render_pillar_details(name: str, pillar: dict, lang: str):
    """柱の詳細を折りたたみで表示 - WHYセクション"""
    details = pillar.get('details', {})
    if not details:
        return
    
    # 表示ラベル
    labels = {
        'en': {'liquidity': '💧 Liquidity Breakdown', 'cycle': '🔄 Cycle Breakdown', 'technical': '📈 Technical Breakdown'},
        'ja': {'liquidity': '💧 流動性の内訳', 'cycle': '🔄 サイクルの内訳', 'technical': '📈 テクニカルの内訳'}
    }
    
    # 指標名の日本語マッピング
    indicator_names = {
        # 流動性
        'fed_assets': 'Fed総資産', 'tga': 'TGA残高', 'on_rrp': 'ON RRP',
        'reserves': '準備預金', 'm2_growth': 'M2成長率', 'net_liquidity': '純流動性',
        # サイクル
        'yield_curve': 'イールドカーブ', 'unemployment': '失業率トレンド',
        'credit_spread': '信用スプレッド', 'leading_index': '先行指標',
        # テクニカル
        'ma_deviation': '200日MA乖離', 'rsi': 'RSI(14)', 'position_52w': '52週レンジ位置'
    }
    
    with st.expander(labels.get(lang, labels['en']).get(name, f'{name} Details'), expanded=False):
        # ヘッダー
        header_cols = st.columns([3, 2, 2, 2])
        with header_cols[0]:
            st.markdown("**指標**" if lang == 'ja' else "**Indicator**")
        with header_cols[1]:
            st.markdown("**値**" if lang == 'ja' else "**Value**")
        with header_cols[2]:
            st.markdown("**スコア**" if lang == 'ja' else "**Score**")
        with header_cols[3]:
            st.markdown("**ウェイト**" if lang == 'ja' else "**Weight**")
        
        st.markdown("---")
        
        # 各指標を表示
        for key, info in details.items():
            if not isinstance(info, dict) or key in ['components_available', 'data_quality']:
                continue
            
            score = info.get('score')
            weight = info.get('weight', 0)
            
            if score is None:
                continue
            
            # 指標ごとに適切な値とフォーマットを選択
            if key == 'ma_deviation':
                val = info.get('deviation_pct')
                val_str = f"{val:+.1f}%" if val is not None else "-"
            elif key == 'position_52w':
                val = info.get('position_pct')
                val_str = f"{val:.0f}%" if val is not None else "-"
            elif key == 'rsi':
                val = info.get('value')
                val_str = f"{val:.1f}" if val is not None else "-"
            elif key in ['yield_curve', 'credit_spread']:
                val = info.get('value')
                val_str = f"{val:.2f}%" if val is not None else "-"
            elif key == 'unemployment':
                val = info.get('value')
                val_str = f"{val:.1f}%" if val is not None else "-"
            elif key == 'leading_index':
                val = info.get('value')
                val_str = f"{val:+.2f}" if val is not None else "-"
            else:
                val = info.get('value', info.get('raw', '-'))
                val_str = f"{val:.2f}" if isinstance(val, float) else str(val) if val else "-"
            
            # スコアに基づく色
            if score >= 65:
                score_color = '#00c853'
            elif score >= 45:
                score_color = '#ffd600'
            elif score >= 25:
                score_color = '#ff9100'
            else:
                score_color = '#ff1744'
            
            cols = st.columns([3, 2, 2, 2])
            with cols[0]:
                display_name = indicator_names.get(key, key) if lang == 'ja' else key.replace('_', ' ').title()
                st.text(display_name)
            with cols[1]:
                st.text(val_str)
            with cols[2]:
                st.markdown(f"<span style='color:{score_color};font-weight:bold;'>{score:.0f}</span>", unsafe_allow_html=True)
            with cols[3]:
                st.text(f"{int(weight*100)}%")


def prepare_verdict_data(df: pd.DataFrame) -> dict:
    """VERDICTに必要なデータを準備"""
    if df is None:
        return {}
    
    # 流動性データ
    liq_keys = ['Fed_Assets', 'TGA', 'ON_RRP', 'Reserves', 'M2SL']
    liquidity_data = {}
    for k in liq_keys:
        if k in df.columns:
            series = df[k].dropna()
            if len(series) > 0:
                liquidity_data[k] = series
    
    # サイクルデータ
    cycle_keys = ['T10Y2Y', 'UNRATE', 'Credit_Spread', 'Leading_Index', 'CFNAI']
    cycle_data = {}
    for k in cycle_keys:
        if k in df.columns:
            series = df[k].dropna()
            if len(series) > 0:
                cycle_data[k] = series
    
    # テクニカルデータ (S&P500)
    price_data = None
    if 'SP500' in df.columns:
        series = df['SP500'].dropna()
        if len(series) > 0:
            price_data = series
    
    return {
        'liquidity_data': liquidity_data,
        'cycle_data': cycle_data,
        'price_data': price_data
    }


def main():
    # 言語取得
    lang = st.session_state.get('language', 'en')
    
    # データ取得
    df = st.session_state.get('df')
    if df is None:
        st.error(t('error_data_not_loaded'))
        st.stop()
    
    # ヘッダー
    title = "⚖️ Market Verdict" if lang == 'en' else "⚖️ マーケット総合判定"
    subtitle = "Integrated market assessment from 3 pillars" if lang == 'en' else "3本柱による市場総合判定"
    st.title(title)
    st.caption(subtitle)
    
    # データ準備
    with st.spinner("Calculating VERDICT..." if lang == 'en' else "VERDICT計算中..."):
        data = prepare_verdict_data(df)
        verdict = calculate_market_verdict(data)
    
    # データ品質チェック
    quality = verdict.get('data_quality', 'unknown')
    if quality == 'insufficient':
        st.warning("⚠️ Insufficient data for VERDICT calculation" if lang == 'en' else "⚠️ VERDICT算出に必要なデータが不足しています")
    elif quality == 'partial':
        st.info("ℹ️ Partial data available - some pillars may be missing" if lang == 'en' else "ℹ️ 一部データ欠損あり")
    
    # 総合VERDICT
    st.markdown("---")
    render_verdict_gauge(
        verdict['verdict_score'],
        verdict.get('verdict_label' if lang == 'ja' else 'verdict_label_en', verdict['verdict_label']),
        verdict['verdict_color']
    )
    
    # 解説
    desc = verdict.get('verdict_description', '')
    if desc:
        st.info(f"💡 {desc}")
    
    # 3本柱
    st.markdown("---")
    section_title = "📊 Three Pillars" if lang == 'en' else "📊 3本柱スコア"
    st.subheader(section_title)
    
    pillars = verdict.get('pillars', {})
    cols = st.columns(3)
    
    pillar_order = ['liquidity', 'cycle', 'technical']
    for i, name in enumerate(pillar_order):
        if name in pillars:
            with cols[i]:
                render_pillar_card(name, pillars[name], lang)
    
    # 詳細セクション
    st.markdown("---")
    detail_title = "📋 Detailed Breakdown" if lang == 'en' else "📋 詳細内訳"
    st.subheader(detail_title)
    
    for name in pillar_order:
        if name in pillars:
            render_pillar_details(name, pillars[name], lang)
    
    # フッター
    st.markdown("---")
    st.caption("⚠️ " + ("This is not investment advice. Please make your own judgment." if lang == 'en' else "投資助言ではありません。投資判断はご自身で行ってください。"))


if __name__ == "__main__":
    main()
