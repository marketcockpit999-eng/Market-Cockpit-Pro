# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 8: Market Sentiment
市場心理指標（Fear & Greed、VIX、Put/Call）

NOTE: Removed unreliable data sources:
- AAII Investor Sentiment: Was using hardcoded dummy data
- CNN Fear & Greed: No official API, web scraping blocked by rate limits
- CME FedWatch: Was using hardcoded dummy data
"""

import streamlit as st
import pandas as pd
import datetime as dt
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    t,
    show_metric_with_sparkline, 
    styled_line_chart,
    get_crypto_fear_greed, 
    get_put_call_ratio,
    record_api_status,
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
vix_value = df.get('VIX').iloc[-1] if df.get('VIX') is not None else None

# Record API status for health monitoring
record_api_status('Crypto_Fear_Greed', crypto_fg is not None and crypto_fg.get('current') is not None)

# === ROW 1: Fear & Greed and VIX ===
col1, col2 = st.columns(2)

with col1:
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
            # Data period display
            history_start = crypto_fg['history'].index[0].strftime('%Y-%m-%d')
            history_end = crypto_fg['history'].index[-1]
            st.caption(f"📅 {t('data_period')}: {history_start} ~ {history_end.strftime('%Y-%m-%d')}")
            st.caption(t('source_update_date', date=history_end.strftime('%Y-%m-%d %H:%M')))
            st.caption(t('sent_30d_trend'))
            styled_line_chart(crypto_fg['history']['value'], height=120)
    else:
        st.warning(t('sent_crypto_error'))

with col2:
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
            vix_60d = vix_series.dropna().tail(60)
            latest_vix_date = vix_60d.index[-1]
            vix_start_date = vix_60d.index[0]
            st.caption(f"📅 {t('data_period')}: {vix_start_date.strftime('%Y-%m-%d')} ~ {latest_vix_date.strftime('%Y-%m-%d')}")
            st.caption(t('source_update_date', date=latest_vix_date.strftime('%Y-%m-%d')))
            st.caption(t('sent_60d_trend'))
            styled_line_chart(vix_60d, height=120)
    else:
        st.warning(t('sent_vix_no_data'))

st.markdown("---")

# === ROW 2: Put/Call Ratio ===
st.markdown(t('sent_put_call_title'))
st.caption(t('sent_put_call_subtitle'))

pc_ratio = get_put_call_ratio()
if pc_ratio:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Interpret P/C ratio
        if pc_ratio > 1.0:
            pc_color = "🔴"
            pc_status = t('sent_pc_bearish')
        elif pc_ratio > 0.7:
            pc_color = "🟡"
            pc_status = t('sent_pc_neutral')
        else:
            pc_color = "🟢"
            pc_status = t('sent_pc_bullish')
        
        st.metric(f"{pc_color} Equity P/C Ratio", f"{pc_ratio:.2f}")
        st.caption(pc_status)
        
        # CBOE CSV provides daily data, show today as data date
        today_str = dt.date.today().strftime('%Y-%m-%d')
        st.caption(f"📅 {t('data_period')}: {today_str}")
        st.caption(t('source_update_date', date=today_str))
        st.caption("📊 Source: CBOE Official")
    
    with col2:
        with st.expander(t('sent_pc_guide_title'), expanded=False):
            st.markdown(t('sent_pc_guide'))
else:
    st.info(t('sent_put_call_preparing'))
    if vix_value is not None:
        st.caption(t('sent_put_call_ref', value=vix_value))

st.markdown("---")

# === Interpretation Guide ===
st.markdown(t('sent_guide_section'))
with st.expander(t('sent_guide_expand')):
    st.markdown(t('sent_guide_content'))
