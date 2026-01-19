# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 8: Market Sentiment
市場心理指標（Fear & Greed、VIX、AAII、Put/Call）
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    t,
    show_metric_with_sparkline, 
    get_crypto_fear_greed, 
    get_cnn_fear_greed,
    get_aaii_sentiment, 
    get_put_call_ratio,
    EXPLANATIONS,
    DATA_FREQUENCY,
)

# Get data from session state
df = st.session_state.get('df')

if df is None:
    st.error(t('error_data_not_loaded'))
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader(t('sentiment_title'))
st.caption(t('sent_subtitle'))

# Fetch sentiment data
crypto_fg = get_crypto_fear_greed()
cnn_fg = get_cnn_fear_greed()
aaii = get_aaii_sentiment()
vix_value = df.get('VIX').iloc[-1] if df.get('VIX') is not None else None

# === ROW 1: Fear & Greed Gauges ===
st.markdown(f"### {t('sent_fg_section')}")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"#### {t('sent_cnn_fg')}")
    if cnn_fg and cnn_fg.get('current'):
        fg_value = cnn_fg['current']
        
        if fg_value <= 25:
            color, label = "🔴", t('sent_extreme_fear')
        elif fg_value <= 45:
            color, label = "🟠", t('sent_fear')
        elif fg_value <= 55:
            color, label = "🟡", t('sent_neutral')
        elif fg_value <= 75:
            color, label = "🟢", t('sent_greed')
        else:
            color, label = "🟣", t('sent_extreme_greed')
        
        st.metric(f"{color} {label}", f"{fg_value}")
        st.progress(fg_value / 100)
        
        if cnn_fg.get('history') is not None and len(cnn_fg['history']) > 0:
            st.caption(t('sent_30d_trend'))
            st.line_chart(cnn_fg['history']['value'], height=120)
    else:
        st.info(t('sent_cnn_unavail'))

with col2:
    st.markdown(f"#### {t('sent_crypto_fg')}")
    if crypto_fg:
        cfg_value = crypto_fg['current']
        cfg_class = crypto_fg.get('classification', '')
        
        if cfg_value <= 25:
            color = "🔴"
        elif cfg_value <= 45:
            color = "🟠"
        elif cfg_value <= 55:
            color = "🟡"
        elif cfg_value <= 75:
            color = "🟢"
        else:
            color = "🟣"
        
        st.metric(f"{color} {cfg_class}", f"{cfg_value}")
        st.progress(cfg_value / 100)
        
        if crypto_fg.get('history') is not None and len(crypto_fg['history']) > 0:
            latest_date = crypto_fg['history'].index[-1]
            st.caption(t('source_update_date', date=latest_date.strftime('%Y-%m-%d %H:%M')))
            st.caption(t('sent_30d_trend'))
            st.line_chart(crypto_fg['history']['value'], height=120)
    else:
        st.warning(t('sent_crypto_error'))

with col3:
    st.markdown(f"#### {t('sent_vix')}")
    if vix_value is not None:
        if vix_value < 15:
            vix_label = t('vix_low')
        elif vix_value < 20:
            vix_label = t('vix_normal')
        elif vix_value < 30:
            vix_label = t('vix_elevated')
        else:
            vix_label = t('vix_high_fear')
        
        st.metric(vix_label, f"{vix_value:.1f}")
        
        vix_series = df.get('VIX')
        if vix_series is not None and not vix_series.isna().all():
            latest_vix_date = vix_series.dropna().index[-1]
            st.caption(t('source_update_date', date=latest_vix_date.strftime('%Y-%m-%d')))
            st.caption(t('sent_60d_trend'))
            st.line_chart(vix_series.tail(60), height=120)
    else:
        st.warning(t('sent_vix_no_data'))

st.markdown("---")

# === ROW 2: AAII Investor Sentiment ===
st.markdown(f"### {t('sent_aaii_title')}")
st.caption(t('sent_aaii_contrarian'))

if aaii:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(t('sent_aaii_bullish_label'), f"{aaii['bullish']:.1f}%")
    with col2:
        st.metric(t('sent_aaii_neutral_label'), f"{aaii['neutral']:.1f}%")
    with col3:
        st.metric(t('sent_aaii_bearish_label'), f"{aaii['bearish']:.1f}%")
    with col4:
        spread = aaii['bull_bear_spread']
        if spread >= 20:
            spread_emoji, spread_hint = "🔴", t('sent_spread_overheated')
        elif spread >= 10:
            spread_emoji, spread_hint = "🟠", t('sent_spread_somewhat_bullish')
        elif spread >= -10:
            spread_emoji, spread_hint = "🟢", t('sent_spread_neutral')
        elif spread >= -20:
            spread_emoji, spread_hint = "🟠", t('sent_spread_somewhat_bearish')
        else:
            spread_emoji, spread_hint = "🔴", t('sent_spread_bottom_signal')
        st.metric(f"{spread_emoji} Bull-Bear Spread", f"{spread:+.1f}%")
        st.caption(spread_hint)
    
    if aaii.get('date'):
        st.caption(t('sent_aaii_update', date=aaii['date']))
    
    st.markdown(t('sent_distribution'))
    bar_data = pd.DataFrame({
        t('sent_category'): [t('bullish'), t('sent_neutral'), t('bearish')],
        t('sent_ratio'): [aaii['bullish'], aaii['neutral'], aaii['bearish']]
    })
    st.bar_chart(bar_data.set_index(t('sent_category')), height=150)
    
    with st.expander(t('sent_spread_guide_title')):
        st.markdown(t('sent_spread_guide'))
    
    if aaii.get('note'):
        st.caption(f"📝 {aaii['note']}")
else:
    st.warning(t('sent_aaii_error'))

st.markdown("---")

# === ROW 3: Put/Call Ratio ===
st.markdown(t('sent_put_call_title'))
st.caption(t('sent_put_call_subtitle'))

pc_ratio = get_put_call_ratio()
if pc_ratio:
    st.metric("Equity P/C Ratio", f"{pc_ratio:.2f}")
else:
    st.info(t('sent_put_call_preparing'))
    if vix_value is not None:
        st.caption(t('sent_put_call_ref', value=vix_value))

st.markdown("---")

# === Interpretation Guide ===
st.markdown(t('sent_guide_section'))
with st.expander(t('sent_guide_expand')):
    st.markdown(t('sent_guide_content'))
