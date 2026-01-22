# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 3: US Economic Data
米国経済指標（雇用、インフレ、景気）
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
    styled_line_chart,
    get_mom_yoy,
    EXPLANATIONS,
    DATA_FREQUENCY,
    t,
)


def show_date_info(df, column_name):
    """データ期間と提供元更新日を表示するヘルパー関数"""
    if df is None or not hasattr(df, 'attrs'):
        return
    
    latest_date = None
    release_date = None
    
    if 'last_valid_dates' in df.attrs and column_name in df.attrs['last_valid_dates']:
        latest_date = df.attrs['last_valid_dates'][column_name]
    if 'fred_release_dates' in df.attrs and column_name in df.attrs['fred_release_dates']:
        release_date = df.attrs['fred_release_dates'][column_name]
    
    if latest_date:
        freq_key = DATA_FREQUENCY.get(column_name, '')
        if freq_key:
            freq_label = t(f'freq_{freq_key}')
            st.caption(f"📅 {t('data_period')}: {latest_date} ({freq_label})")
        else:
            st.caption(f"📅 {t('data_date')}: {latest_date}")
    
    if release_date:
        st.caption(f"🔄 {t('source_update')}: {release_date}")

# Get data from session state
df = st.session_state.get('df')
df_original = st.session_state.get('df_original')

if df is None:
    st.error(t('error_data_not_loaded'))
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader(t('us_economic_page_title'))

# === 1. Employment ===
st.markdown(f"### {t('us_economic_section_employment')}")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### {t('nfp_title')}")
    nfp_original = df_original.get('NFP') if df_original is not None else None
    
    if nfp_original is not None and len(nfp_original.dropna()) >= 2:
        nfp_data = nfp_original.dropna()
        nfp_change = nfp_data.iloc[-1] - nfp_data.iloc[-2]
        st.metric(t('result'), f"{nfp_change:+,.0f}K")
        show_date_info(df, 'NFP')
        
        nfp_changes = nfp_data.diff().dropna()
        if len(nfp_changes) > 0:
            st.markdown(f"###### {t('nfp_monthly_change')}")
            styled_line_chart(nfp_changes, height=150)
    
    st.markdown("---")
    st.markdown(f"#### {t('unemployment_rate')}")
    unemp_original = df_original.get('UNRATE') if df_original is not None else None
    unemp_series = df.get('UNRATE')
    
    if unemp_original is not None and len(unemp_original.dropna()) >= 2:
        unemp_data = unemp_original.dropna()
        unemp_curr = unemp_data.iloc[-1]
        unemp_change = unemp_curr - unemp_data.iloc[-2]
        st.metric(t('unemployment_rate'), f"{unemp_curr:.1f}%", delta=f"{unemp_change:+.1f}pp {t('vs_last_month')}")
        show_date_info(df, 'UNRATE')
    
    if unemp_series is not None and not unemp_series.isna().all():
        styled_line_chart(unemp_series, height=150)

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
        
        styled_line_chart(ahe_data, height=120)
        show_date_info(df, 'AvgHourlyEarnings')
    
    st.markdown("---")
    st.markdown(f"#### {t('jolts_title')}")
    jolts_series = df.get('JOLTS')
    show_metric_with_sparkline(t('jolts_label'), jolts_series, 'JOLTS', "K", "JOLTS", notes=t('jolts_notes'))
    if jolts_series is not None and not jolts_series.isna().all():
        styled_line_chart(jolts_series, height=150)
    
    st.markdown("---")
    st.markdown(f"#### {t('icsa_title')}")
    icsa_series = df.get('ICSA')
    if icsa_series is not None and len(icsa_series.dropna()) >= 2:
        icsa_data = icsa_series.dropna() / 1000
        icsa_curr = icsa_data.iloc[-1]
        icsa_change = icsa_curr - icsa_data.iloc[-2]
        st.metric(t('latest_week'), f"{icsa_curr:,.0f}K", delta=f"{icsa_change:+,.0f}K {t('vs_last_week')}", delta_color="inverse")
        styled_line_chart(icsa_data, height=150)

# === 2. Inflation ===
st.markdown("---")
st.markdown(f"### {t('us_economic_section_inflation')}")
col1, col2 = st.columns(2)

with col1:
    display_macro_card(t('cpi_title'), df.get('CPI'), 'CPI', df_original=df_original, notes=t('cpi_notes_full'))
    st.markdown("---")
    
    st.markdown(f"#### {t('core_pce_title')}")
    pce_series = df.get('CorePCE')
    if pce_series is not None and len(pce_series.dropna()) >= 2:
        pce_curr = pce_series.dropna().iloc[-1]
        pce_change = pce_curr - pce_series.dropna().iloc[-2]
        st.metric(t('current_inflation'), f"{pce_curr:.2f}%", delta=f"{pce_change:+.2f}pp {t('vs_last_month')}")
    show_metric_with_sparkline(t('core_pce_label'), pce_series, 'CorePCE', "%", "CorePCE", notes=t('core_pce_notes'))
    if pce_series is not None and not pce_series.isna().all():
        styled_line_chart(pce_series, height=150)
        
with col2:
    display_macro_card(t('core_cpi_title'), df.get('CPICore'), 'CPICore', df_original=df_original, notes=t('core_cpi_notes'))
    st.markdown("---")
    display_macro_card(t('ppi_title'), df.get('PPI'), 'PPI', df_original=df_original, notes=t('ppi_notes_full'))

# === 3. Economy ===
st.markdown("---")
st.markdown(f"### {t('us_economic_section_economy')}")
col1, col2 = st.columns(2)

with col1:
    display_macro_card(t('retail_sales_title'), df.get('RetailSales'), 'RetailSales', df_original=df_original, unit="$M", notes=t('retail_sales_notes'))
    st.markdown("---")
    display_macro_card(t('consumer_sentiment_title'), df.get('ConsumerSent'), 'ConsumerSent', df_original=df_original, unit="pt", notes=t('consumer_sentiment_notes'))

with col2:
    st.markdown(f"#### {t('gdp_title')}")
    gdp_series = df.get('RealGDP')
    if gdp_series is not None and len(gdp_series.dropna()) >= 2:
        gdp_data = gdp_series.dropna()
        gdp_curr = gdp_data.iloc[-1]
        qoq_pct = (gdp_curr / gdp_data.iloc[-2] - 1)
        annualized = ((1 + qoq_pct) ** 4 - 1) * 100
        st.metric(t('qoq_annualized'), f"{annualized:+.1f}%", delta=f"{t('level')}: ${gdp_curr:,.0f}B", delta_color="off")
    show_metric_with_sparkline(t('gdp_label'), gdp_series, 'RealGDP', "$B", "RealGDP", notes=t('gdp_notes'))
    if gdp_series is not None and not gdp_series.isna().all():
        styled_line_chart(gdp_series, height=150)
    
    st.markdown("---")
    st.markdown(f"#### {t('yield_curve_title')}")
    show_metric_with_sparkline(t('yield_curve_label'), df.get('T10Y2Y'), 'T10Y2Y', "%", "T10Y2Y", notes=t('yield_curve_notes'))
    if 'T10Y2Y' in df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['T10Y2Y'], name='2Y-10Y Spread', line=dict(color='cyan')))
        fig.add_hline(y=0, line_dash='dash', line_color='red', annotation_text=t('inversion_boundary'))
        st.plotly_chart(fig, use_container_width=True, key=f"yield_curve_{uuid.uuid4().hex[:8]}")

# === Michigan Inflation Expectations ===
st.markdown("---")
st.markdown(f"#### {t('michigan_inflation_title')}")
st.caption(t('michigan_inflation_desc'))
mich_series = df.get('Michigan_Inflation_Exp')
col1, col2 = st.columns([1, 2])

with col1:
    show_metric_with_sparkline(t('michigan_inflation_label'), mich_series, 'Michigan_Inflation_Exp', "%", "Michigan_Inflation_Exp", notes=t('michigan_inflation_notes'))

with col2:
    if mich_series is not None and not mich_series.isna().all():
        fig_mich = go.Figure()
        fig_mich.add_trace(go.Scatter(x=mich_series.index, y=mich_series.values, name='1Y Inflation Exp', line=dict(color='#ff6b6b')))
        fig_mich.add_hline(y=2.0, line_dash='dash', line_color='green', annotation_text=t('fed_target'))
        fig_mich.update_layout(height=200, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_mich, use_container_width=True, key=f"mich_inf_{uuid.uuid4().hex[:8]}")

# === 4. Leading Indicators ===
st.markdown("---")
st.markdown(f"### 📈 {t('us_economic_section_leading')}")
st.caption(t('leading_indicators_desc'))

st.markdown(f"#### {t('leading_index_title')}")
lei_series = df.get('Leading_Index')
show_metric_with_sparkline(t('leading_index_label'), lei_series, 'Leading_Index', "idx", "Leading_Index", notes=t('leading_index_notes'))
if lei_series is not None and not lei_series.isna().all():
    fig_lei = go.Figure()
    fig_lei.add_trace(go.Scatter(x=lei_series.index, y=lei_series.values, name='CFNAI (3-mo MA)', line=dict(color='#00ff88')))
    fig_lei.add_hline(y=0, line_dash='dash', line_color='orange', annotation_text=t('zero_line'))
    st.plotly_chart(fig_lei, use_container_width=True, key=f"leading_index_{uuid.uuid4().hex[:8]}")

# === 5. Housing ===
st.markdown("---")
st.markdown(f"### 🏠 {t('us_economic_section_housing')}")
st.caption(t('housing_indicators_desc'))
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### {t('housing_starts_title')}")
    houst_series = df.get('Housing_Starts')
    show_metric_with_sparkline(t('housing_starts_label'), houst_series, 'Housing_Starts', "K", "Housing_Starts", notes=t('housing_starts_notes'))
    if houst_series is not None and not houst_series.isna().all():
        styled_line_chart(houst_series, height=150)

with col2:
    st.markdown(f"#### {t('building_permits_title')}")
    permit_series = df.get('Building_Permits')
    show_metric_with_sparkline(t('building_permits_label'), permit_series, 'Building_Permits', "K", "Building_Permits", notes=t('building_permits_notes'))
    if permit_series is not None and not permit_series.isna().all():
        styled_line_chart(permit_series, height=150)
