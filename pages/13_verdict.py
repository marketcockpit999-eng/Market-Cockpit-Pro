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
from utils.verdict_why import render_why_section
from utils.verdict_assets import calculate_multi_asset_verdict


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
    # Get translated gauge labels
    gauge_caution = t('verdict_gauge_caution')
    gauge_neutral = t('verdict_gauge_neutral')
    gauge_bullish = t('verdict_gauge_bullish')
    
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(145deg, #1a1a2e, #16213e); border-radius: 16px; margin-bottom: 1rem;">
        <h1 style="font-size: 5rem; color: {hex_color}; margin: 0;">{score:.0f}</h1>
        <p style="font-size: 1.5rem; color: {hex_color}; margin: 0.5rem 0;">{label}</p>
        <div style="background: #2d2d44; border-radius: 10px; height: 20px; margin-top: 1rem;">
            <div style="background: linear-gradient(90deg, #ff1744 0%, #ffd600 50%, #00c853 100%); width: {score}%; height: 100%; border-radius: 10px;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #888; margin-top: 0.3rem;">
            <span>{gauge_caution}</span><span>{gauge_neutral}</span><span>{gauge_bullish}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_pillar_card(name: str, pillar: dict, lang: str):
    """4本柱カードを描画"""
    icons = {'liquidity': '💧', 'cycle': '🔄', 'technical': '📈', 'sentiment': '📊'}
    # Use t() for pillar labels
    pillar_labels = {
        'liquidity': t('verdict_pillar_liquidity'),
        'cycle': t('verdict_pillar_cycle'),
        'technical': t('verdict_pillar_technical'),
        'sentiment': t('verdict_pillar_sentiment')
    }
    
    score = pillar.get('score', 50)
    interp = pillar.get('interpretation', {})
    label = interp.get('label_en' if lang == 'en' else 'label', '-')
    color = get_color_hex(interp.get('color', 'yellow'))
    weight = int(pillar.get('weight', 0) * 100)
    
    st.markdown(f"""
    <div style="background: #1e1e2f; padding: 1.2rem; border-radius: 12px; border-left: 4px solid {color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 1.1rem;">{icons.get(name, '')} {pillar_labels.get(name, name)}</span>
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
    
    # Use t() for breakdown labels
    breakdown_labels = {
        'liquidity': t('verdict_breakdown_liquidity'),
        'cycle': t('verdict_breakdown_cycle'),
        'technical': t('verdict_breakdown_technical'),
        'sentiment': t('verdict_breakdown_sentiment')
    }
    
    # Use t() for indicator names
    indicator_names = {
        # Liquidity
        'fed_assets': t('verdict_ind_fed_assets'),
        'tga': t('verdict_ind_tga'),
        'on_rrp': t('verdict_ind_on_rrp'),
        'reserves': t('verdict_ind_reserves'),
        'm2_growth': t('verdict_ind_m2_growth'),
        'net_liquidity': t('verdict_ind_net_liquidity'),
        # Cycle
        'yield_curve': t('verdict_ind_yield_curve'),
        'unemployment': t('verdict_ind_unemployment'),
        'credit_spread': t('verdict_ind_credit_spread'),
        'sloos_std': t('verdict_ind_sloos_std'),
        'leading_index': t('verdict_ind_leading_index'),
        'mfg_composite': t('verdict_ind_mfg_composite'),
        'svc_composite': t('verdict_ind_svc_composite'),
        # Technical
        'ma_deviation': t('verdict_ind_ma_deviation'),
        'rsi': t('verdict_ind_rsi'),
        'position_52w': t('verdict_ind_position_52w'),
        # Sentiment
        'vix': t('verdict_ind_vix'),
        'consumer_sent': t('verdict_ind_consumer_sent'),
        'nfci': t('verdict_ind_nfci'),
    }
    
    # 指標の表示順序（流動性柱用）
    liquidity_order = ['fed_assets', 'tga', 'net_liquidity', 'reserves', 'on_rrp', 'm2_growth']
    
    with st.expander(breakdown_labels.get(name, f'{name} Details'), expanded=False):
        # Header with t()
        header_cols = st.columns([3, 2, 2, 2])
        with header_cols[0]:
            st.markdown(t('verdict_header_indicator'))
        with header_cols[1]:
            st.markdown(t('verdict_header_value'))
        with header_cols[2]:
            st.markdown(t('verdict_header_score'))
        with header_cols[3]:
            st.markdown(t('verdict_header_weight'))
        
        st.markdown("---")
        
        # 流動性柱の場合は順序を制御
        if name == 'liquidity':
            keys_to_show = liquidity_order
        else:
            keys_to_show = [k for k in details.keys() if k not in ['components_available', 'data_quality']]
        
        # 各指標を表示
        for key in keys_to_show:
            info = details.get(key)
            if not isinstance(info, dict):
                continue
            
            score = info.get('score')
            weight = info.get('weight', 0)
            
            if score is None:
                continue
            
            # 指標ごとに適切な値とフォーマットを選択
            val = info.get('value')
            
            if key in ['fed_assets', 'net_liquidity', 'reserves']:
                # 十億ドル→兆ドル表示
                val_str = f"${val/1000:.2f}T" if val is not None else "-"
            elif key == 'tga':
                # TGAは十億ドル表示
                val_str = f"${val:.0f}B" if val is not None else "-"
            elif key == 'on_rrp':
                # ON RRPは十億ドル表示
                val_str = f"${val:.0f}B" if val is not None else "-"
            elif key == 'm2_growth':
                # M2 YoY成長率
                val_str = f"{val:+.1f}%" if val is not None else "-"
            elif key == 'ma_deviation':
                val = info.get('deviation_pct')
                val_str = f"{val:+.1f}%" if val is not None else "-"
            elif key == 'position_52w':
                val = info.get('position_pct')
                val_str = f"{val:.0f}%" if val is not None else "-"
            elif key == 'rsi':
                val_str = f"{val:.1f}" if val is not None else "-"
            elif key in ['yield_curve', 'credit_spread']:
                val_str = f"{val:.2f}%" if val is not None else "-"
            elif key == 'unemployment':
                val_str = f"{val:.1f}%" if val is not None else "-"
            elif key == 'leading_index':
                val_str = f"{val:+.2f}" if val is not None else "-"
            elif key in ['mfg_composite', 'svc_composite']:
                val_str = f"{val:+.1f}" if val is not None else "-"
            elif key == 'sloos_std':
                # SLOOS融資基準（Net% Tightening）
                val_str = f"{val:+.1f}%" if val is not None else "-"
            elif key == 'consumer_sent':
                # 消費者信頼感指数
                val_str = f"{val:.1f}" if val is not None else "-"
            elif key == 'nfci':
                # NFCI金融環境指数
                val_str = f"{val:+.2f}" if val is not None else "-"
            else:
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
                # Use indicator_names which now uses t() function
                display_name = indicator_names.get(key, key.replace('_', ' ').title())
                st.text(display_name)
            with cols[1]:
                st.text(val_str)
            with cols[2]:
                st.markdown(f"<span style='color:{score_color};font-weight:bold;'>{score:.0f}</span>", unsafe_allow_html=True)
            with cols[3]:
                # Weight 0 = Reference info
                if weight == 0:
                    ref_text = t('verdict_reference')
                    st.markdown(f"<span style='color:#888;font-size:0.8em;'>{ref_text}</span>", unsafe_allow_html=True)
                else:
                    st.text(f"{int(weight*100)}%")


def prepare_verdict_data(df: pd.DataFrame) -> dict:
    """VERDICTに必要なデータを準備"""
    if df is None:
        return {}
    
    # 流動性データ
    liq_keys = ['SOMA_Total', 'TGA', 'ON_RRP', 'Reserves', 'M2SL']
    liquidity_data = {}
    for k in liq_keys:
        if k in df.columns:
            series = df[k].dropna()
            if len(series) > 0:
                liquidity_data[k] = series
    
    # サイクルデータ
    cycle_keys = [
        'T10Y2Y', 'UNRATE', 'Credit_Spread', 'Leading_Index', 'CFNAI',
        # SLOOS融資基準（信用サイクル先行指標）
        'CI_Std_Large', 'CI_Std_Small',
        # Regional Fed Manufacturing
        'Empire_State_Mfg', 'Philly_Fed_Mfg', 'Dallas_Fed_Mfg', 'Richmond_Fed_Mfg',
        # Regional Fed Services
        'NY_Fed_Services', 'Philly_Fed_Services', 'Dallas_Fed_Services', 'Richmond_Fed_Services',
    ]
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
    
    # センチメントデータ (5本柱)
    sentiment_data = {}
    if 'VIX' in df.columns:
        sentiment_data['VIX'] = df['VIX'].dropna()
    if 'Credit_Spread' in df.columns:
        sentiment_data['Credit_Spread'] = df['Credit_Spread'].dropna()
    if 'SP500' in df.columns:
        sentiment_data['SP500'] = df['SP500'].dropna()
    # ConsumerSent (ミシガン大消費者信頼感)
    if 'ConsumerSent' in df.columns:
        sentiment_data['ConsumerSent'] = df['ConsumerSent'].dropna()
    # NFCI (シカゴ連銀金融環境指数)
    if 'NFCI' in df.columns:
        sentiment_data['NFCI'] = df['NFCI'].dropna()
    
    return {
        'liquidity_data': liquidity_data,
        'cycle_data': cycle_data,
        'price_data': price_data,
        'sentiment_data': sentiment_data
    }


def prepare_multi_asset_data(df: pd.DataFrame, base_data: dict) -> dict:
    """マルチアセット用にデータを拡張"""
    from utils.data_fetcher import get_crypto_fear_greed
    
    if df is None:
        return base_data
    
    data = base_data.copy()
    
    # Gold価格
    if 'Gold' in df.columns:
        series = df['Gold'].dropna()
        if len(series) > 0:
            data['Gold'] = series
    
    # BTC価格
    if 'BTC' in df.columns:
        series = df['BTC'].dropna()
        if len(series) > 0:
            data['BTC'] = series
    
    # DXY（ドル指数）
    if 'DXY' in df.columns:
        series = df['DXY'].dropna()
        if len(series) > 0:
            data['DXY'] = series
    
    # US 10Y Yield（実質金利計算用）
    if 'US_TNX' in df.columns:
        series = df['US_TNX'].dropna()
        if len(series) > 0:
            data['US_TNX'] = series
    
    # Breakeven 10Y（実質金利計算用）
    if 'Breakeven_10Y' in df.columns:
        series = df['Breakeven_10Y'].dropna()
        if len(series) > 0:
            data['Breakeven_10Y'] = series
    
    # VIX（不確実性指標用）
    if 'VIX' in df.columns:
        series = df['VIX'].dropna()
        if len(series) > 0:
            data['VIX'] = series
    
    # Crypto Fear & Greed（BTCセンチメント用）
    try:
        crypto_fg = get_crypto_fear_greed()
        if crypto_fg and crypto_fg.get('current'):
            data['crypto_fear_greed'] = crypto_fg['current']
    except Exception:
        pass  # APIエラー時はスキップ
    
    return data


def render_asset_gauge(asset_verdict: dict, lang: str):
    """個別資産のゲージを描画"""
    score = asset_verdict.get('score', 50)
    label = asset_verdict.get('asset_label' if lang == 'ja' else 'asset_label_en', asset_verdict.get('asset_label', ''))
    verdict_label = asset_verdict.get('label' if lang == 'ja' else 'label_en', asset_verdict.get('label', ''))
    color = get_color_hex(asset_verdict.get('color', 'yellow'))
    data_quality = asset_verdict.get('data_quality', 'unknown')
    
    # データ品質ラベル
    quality_labels = {
        'good': t('verdict_data_quality_good'),
        'partial': t('verdict_data_quality_partial'),
        'insufficient': t('verdict_data_quality_insufficient'),
    }
    quality_text = quality_labels.get(data_quality, '')
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(145deg, #1a1a2e, #16213e); border-radius: 12px;">
        <p style="font-size: 1rem; color: #888; margin: 0;">{label}</p>
        <h2 style="font-size: 2.5rem; color: {color}; margin: 0.3rem 0;">{score:.0f}</h2>
        <p style="font-size: 0.9rem; color: {color}; margin: 0;">{verdict_label}</p>
        <div style="background: #2d2d44; border-radius: 8px; height: 12px; margin-top: 0.8rem;">
            <div style="background: linear-gradient(90deg, #ff1744 0%, #ffd600 50%, #00c853 100%); width: {score}%; height: 100%; border-radius: 8px;"></div>
        </div>
        <p style="font-size: 0.7rem; color: #666; margin-top: 0.5rem;">{quality_text}</p>
    </div>
    """, unsafe_allow_html=True)


def render_multi_asset_section(df: pd.DataFrame, base_data: dict, lang: str):
    """マルチアセットVERDICTセクションを描画"""
    # マルチアセット用データを準備
    multi_data = prepare_multi_asset_data(df, base_data)
    
    # 3資産のVERDICTを計算
    try:
        multi_verdict = calculate_multi_asset_verdict(multi_data)
    except Exception as e:
        st.warning(f"マルチアセット計算エラー: {e}")
        return
    
    # タイトル
    st.subheader(t('verdict_multi_asset_title'))
    st.caption(t('verdict_multi_asset_subtitle'))
    
    # データ基準日を表示
    if df is not None and len(df) > 0:
        try:
            latest_date = df.index[-1]
            date_str = latest_date.strftime('%Y-%m-%d')
            date_label = t('verdict_data_as_of')
            st.caption(f"📅 {date_label}: {date_str}")
        except Exception:
            pass
    
    # 3資産ゲージを横並び表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_asset_gauge(multi_verdict['stock'], lang)
    with col2:
        render_asset_gauge(multi_verdict['gold'], lang)
    with col3:
        render_asset_gauge(multi_verdict['btc'], lang)
    
    # ランキング表示
    st.markdown("")
    recommendation = multi_verdict.get('recommendation' if lang == 'ja' else 'recommendation_en', multi_verdict.get('recommendation', ''))
    st.info(f"{t('verdict_ranking_title')}: {recommendation}")


def main():
    # Get language
    lang = st.session_state.get('lang', 'en')
    
    # Get data
    df = st.session_state.get('df')
    if df is None:
        st.error(t('error_data_not_loaded'))
        st.stop()
    
    # Header with t()
    st.title(t('verdict_title'))
    st.caption(t('verdict_subtitle'))
    
    # Prepare data
    with st.spinner(t('verdict_calculating')):
        data = prepare_verdict_data(df)
        verdict = calculate_market_verdict(data)
    
    # Data quality check with t()
    quality = verdict.get('data_quality', 'unknown')
    if quality == 'insufficient':
        st.warning(t('verdict_insufficient_data'))
    elif quality == 'partial':
        st.info(t('verdict_partial_data'))
    
    # 4 Pillars section with t()
    st.markdown("---")
    st.subheader(t('verdict_four_pillars'))
    
    pillars = verdict.get('pillars', {})
    cols = st.columns(4)
    
    pillar_order = ['liquidity', 'cycle', 'technical', 'sentiment']
    for i, name in enumerate(pillar_order):
        if name in pillars:
            with cols[i]:
                render_pillar_card(name, pillars[name], lang)
    
    # Detail section with t()
    st.markdown("---")
    st.subheader(t('verdict_detailed_breakdown'))
    
    for name in pillar_order:
        if name in pillars:
            render_pillar_details(name, pillars[name], lang)
    
    # WHY Section (Phase 4)
    st.markdown("---")
    render_why_section(verdict)
    
    # Multi-Asset VERDICT Section (Phase 5)
    st.markdown("---")
    render_multi_asset_section(df, data, lang)
    
    # Footer with t()
    st.markdown("---")
    st.caption(t('verdict_disclaimer'))


if __name__ == "__main__":
    main()
