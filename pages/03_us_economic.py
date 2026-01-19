# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 3: US Economic Data
米国経済指標（金利、雇用、インフレ、景気）
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import uuid
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    show_metric_with_sparkline, 
    display_macro_card,
    get_mom_yoy,
    EXPLANATIONS,
    DATA_FREQUENCY,
    t,
)

# Get data from session state
df = st.session_state.get('df')
df_original = st.session_state.get('df_original')

if df is None:
    st.error(t('error_data_not_loaded'))
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader("📈 US Economic Data")

# === 1. Interest Rates ===
st.markdown(f"### {t('us_economic_section_rates')}")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"#### {t('ff_upper')}")
    show_metric_with_sparkline("FF Upper", df.get('FedFundsUpper'), 'FedFundsUpper', "%", "FF_Upper", notes=t('ff_upper_notes'), decimal_places=3)
    if 'FedFundsUpper' in df.columns:
        st.line_chart(df[['FedFundsUpper']].dropna(), height=120)
        
with col2:
    st.markdown("#### EFFR")
    show_metric_with_sparkline("EFFR", df.get('EFFR'), 'EFFR', "%", "EFFR", notes=t('effr_notes'), decimal_places=3)
    if 'EFFR' in df.columns:
        st.line_chart(df[['EFFR']].dropna(), height=120)
        
with col3:
    st.markdown("#### SOFR")
    show_metric_with_sparkline("SOFR", df.get('SOFR'), 'SOFR', "%", "SOFR", notes=t('sofr_notes_full'), decimal_places=3)
    if 'SOFR' in df.columns:
        st.line_chart(df[['SOFR']].dropna(), height=120)

# === 2. Employment ===
st.markdown("---")
st.markdown(f"### {t('us_economic_section_employment')}")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### {t('nfp_title')}")
    nfp_original = df_original.get('NFP') if df_original is not None else None
    
    if nfp_original is not None and len(nfp_original.dropna()) >= 2:
        nfp_data = nfp_original.dropna()
        nfp_change = nfp_data.iloc[-1] - nfp_data.iloc[-2]
        st.metric(t('result'), f"{nfp_change:+,.0f}K（{nfp_change/10:+,.1f}万人）")
        
        nfp_changes = nfp_data.diff().dropna()
        if len(nfp_changes) > 0:
            st.markdown(f"###### {t('nfp_monthly_change')}")
            st.line_chart(nfp_changes, height=150)
    
    st.markdown("---")
    st.markdown(f"#### {t('unemployment_rate')}")
    unemp_original = df_original.get('UNRATE') if df_original is not None else None
    unemp_series = df.get('UNRATE')
    
    if unemp_original is not None and len(unemp_original.dropna()) >= 2:
        unemp_data = unemp_original.dropna()
        unemp_curr = unemp_data.iloc[-1]
        unemp_change = unemp_curr - unemp_data.iloc[-2]
        st.metric(t('unemployment_rate'), f"{unemp_curr:.1f}%", delta=f"{unemp_change:+.1f}pp {t('vs_last_month')}")
    
    if unemp_series is not None and not unemp_series.isna().all():
        st.line_chart(unemp_series.dropna(), height=150)

with col2:
    st.markdown(f"#### {t('avg_hourly_earnings')}")
    ahe_original = df_original.get('AvgHourlyEarnings') if df_original is not None else None
    
    if ahe_original is not None and len(ahe_original.dropna()) >= 2:
        ahe_data = ahe_original.dropna()
        ahe_curr = ahe_data.iloc[-1]
        mom = (ahe_curr / ahe_data.iloc[-2] - 1) * 100
        
        yoy = None
        if len(ahe_data) > 12:
            yoy = (ahe_curr / ahe_data.iloc[-13] - 1) * 100
        
        m_col1, m_col2 = st.columns(2)
        m_col1.metric(t('mom'), f"{mom:+.1f}%")
        if yoy is not None:
            m_col2.metric(t('yoy'), f"{yoy:+.1f}%")
        
        st.line_chart(ahe_data, height=120)
    
    st.markdown("---")
    st.markdown("#### JOLTS Job Openings")
    jolts_series = df.get('JOLTS')
    show_metric_with_sparkline("JOLTS Level", jolts_series, 'JOLTS', "K", "JOLTS", notes=t('jolts_notes'))
    if jolts_series is not None and not jolts_series.isna().all():
        st.line_chart(jolts_series.dropna(), height=150)
    
    st.markdown("---")
    st.markdown(f"#### {t('icsa_title')}")
    icsa_series = df.get('ICSA')
    if icsa_series is not None and len(icsa_series.dropna()) >= 2:
        icsa_data = icsa_series.dropna() / 1000
        icsa_curr = icsa_data.iloc[-1]
        icsa_change = icsa_curr - icsa_data.iloc[-2]
        st.metric(t('latest_week'), f"{icsa_curr:,.0f}K", delta=f"{icsa_change:+,.0f}K {t('vs_last_week')}", delta_color="inverse")
        st.line_chart(icsa_data.dropna(), height=150)

# === 3. Inflation ===
st.markdown("---")
st.markdown(f"### {t('us_economic_section_inflation')}")
col1, col2 = st.columns(2)

with col1:
    display_macro_card("Consumer Price Index (CPI)", df.get('CPI'), 'CPI', df_original=df_original, notes=t('cpi_notes_full'))
    st.markdown("---")
    
    st.markdown(f"#### {t('core_pce_title')}")
    pce_series = df.get('CorePCE')
    if pce_series is not None and len(pce_series.dropna()) >= 2:
        pce_curr = pce_series.dropna().iloc[-1]
        pce_change = pce_curr - pce_series.dropna().iloc[-2]
        st.metric(t('current_inflation'), f"{pce_curr:.2f}%", delta=f"{pce_change:+.2f}pp {t('vs_last_month')}")
    show_metric_with_sparkline("Core PCE", pce_series, 'CorePCE', "%", "CorePCE", notes=t('core_pce_notes'))
    if pce_series is not None and not pce_series.isna().all():
        st.line_chart(pce_series.dropna(), height=150)
        
with col2:
    display_macro_card("Core CPI", df.get('CPICore'), 'CPICore', df_original=df_original, notes=t('core_cpi_notes'))
    st.markdown("---")
    display_macro_card("Producer Price Index (PPI)", df.get('PPI'), 'PPI', df_original=df_original, notes=t('ppi_notes_full'))

# === 4. Economy ===
st.markdown("---")
st.markdown(f"### {t('us_economic_section_economy')}")
col1, col2 = st.columns(2)

with col1:
    display_macro_card("Retail Sales", df.get('RetailSales'), 'RetailSales', df_original=df_original, unit="$M", notes=t('retail_sales_notes'))
    st.markdown("---")
    display_macro_card("Consumer Sentiment", df.get('ConsumerSent'), 'ConsumerSent', df_original=df_original, unit="pt", notes=t('consumer_sentiment_notes'))

with col2:
    st.markdown(f"#### {t('gdp_title')}")
    gdp_series = df.get('RealGDP')
    if gdp_series is not None and len(gdp_series.dropna()) >= 2:
        gdp_data = gdp_series.dropna()
        gdp_curr = gdp_data.iloc[-1]
        qoq_pct = (gdp_curr / gdp_data.iloc[-2] - 1)
        annualized = ((1 + qoq_pct) ** 4 - 1) * 100
        st.metric(t('qoq_annualized'), f"{annualized:+.1f}%", delta=f"{t('level')}: ${gdp_curr:,.0f}B", delta_color="off")
    show_metric_with_sparkline("GDP Level", gdp_series, 'RealGDP', "$B", "RealGDP", notes=t('gdp_notes'))
    if gdp_series is not None and not gdp_series.isna().all():
        st.line_chart(gdp_series.dropna(), height=150)
    
    st.markdown("---")
    st.markdown(f"#### {t('yield_curve_title')}")
    show_metric_with_sparkline("2Y-10Y Spread", df.get('T10Y2Y'), 'T10Y2Y', "%", "T10Y2Y", notes=t('yield_curve_notes'))
    if 'T10Y2Y' in df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['T10Y2Y'], name='2Y-10Y Spread', line=dict(color='cyan')))
        fig.add_hline(y=0, line_dash='dash', line_color='red', annotation_text=t('inversion_boundary'))
        st.plotly_chart(fig, use_container_width=True, key=f"yield_curve_{uuid.uuid4().hex[:8]}")
