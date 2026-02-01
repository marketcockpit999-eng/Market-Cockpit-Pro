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
from utils.data_fetcher import get_richmond_fed_survey, get_richmond_fed_services_survey


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
with st.expander(t('us_economic_section_employment'), expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {t('nfp_title')}")
        nfp_original = df_original.get('NFP') if df_original is not None else None
        
        if nfp_original is not None and len(nfp_original.dropna()) >= 2:
            nfp_data = nfp_original.dropna()
            nfp_change = nfp_data.iloc[-1] - nfp_data.iloc[-2]
            from utils.help_texts import HELP_EN, HELP_JA
            from utils.i18n import get_current_language
            help_dict = HELP_JA if get_current_language() == 'ja' else HELP_EN
            st.metric(t('result'), f"{nfp_change:+,.0f}K", help=help_dict.get('help_NFP', ''))
            show_date_info(df, 'NFP')
            
            nfp_changes = nfp_data.diff().dropna()
            if len(nfp_changes) > 0:
                st.markdown(f"###### {t('nfp_monthly_change')}")
                styled_line_chart(nfp_changes, height=150)
        
        st.markdown("---")
        st.markdown(f"#### {t('adp_title')}")
        adp_original = df_original.get('ADP') if df_original is not None else None
        
        if adp_original is not None and len(adp_original.dropna()) >= 2:
            adp_data = adp_original.dropna()
            adp_change = adp_data.iloc[-1] - adp_data.iloc[-2]
            from utils.help_texts import HELP_EN, HELP_JA
            from utils.i18n import get_current_language
            help_dict = HELP_JA if get_current_language() == 'ja' else HELP_EN
            st.metric(t('adp_label'), f"{adp_change:+,.0f}K", help=help_dict.get('help_ADP', ''))
            show_date_info(df, 'ADP')
            
            adp_changes = adp_data.diff().dropna()
            if len(adp_changes) > 0:
                st.markdown(f"###### {t('adp_monthly_change')}")
                styled_line_chart(adp_changes, height=120)
        
        st.markdown("---")
        st.markdown(f"#### {t('unemployment_rate')}")
        unemp_original = df_original.get('UNRATE') if df_original is not None else None
        unemp_series = df.get('UNRATE')
        
        if unemp_original is not None and len(unemp_original.dropna()) >= 2:
            unemp_data = unemp_original.dropna()
            unemp_curr = unemp_data.iloc[-1]
            unemp_change = unemp_curr - unemp_data.iloc[-2]
            from utils.help_texts import HELP_EN, HELP_JA
            from utils.i18n import get_current_language
            help_dict = HELP_JA if get_current_language() == 'ja' else HELP_EN
            st.metric(t('unemployment_rate'), f"{unemp_curr:.1f}%", delta=f"{unemp_change:+.1f}pp {t('vs_last_month')}", help=help_dict.get('help_UNRATE', ''))
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
            from utils.help_texts import HELP_EN, HELP_JA
            from utils.i18n import get_current_language
            help_dict = HELP_JA if get_current_language() == 'ja' else HELP_EN
            st.metric(t('latest_week'), f"{icsa_curr:,.0f}K", delta=f"{icsa_change:+,.0f}K {t('vs_last_week')}", delta_color="inverse", help=help_dict.get('help_ICSA', ''))
            show_date_info(df, 'ICSA')
            st.caption(t('icsa_notes'))
            # 60-day sparkline
            icsa_60d = icsa_data.tail(60)
            if len(icsa_60d) > 0:
                st.caption(f"📊 {t('sparkline_label')}")
                styled_line_chart(icsa_60d, height=80)
            # Long-term trend
            styled_line_chart(icsa_data, height=150)
        else:
            st.info(t('no_data'))

# === 2. Inflation ===
st.markdown("---")
with st.expander(t('us_economic_section_inflation'), expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        display_macro_card(t('cpi_title'), df.get('CPI'), 'CPI', df_original=df_original, notes=t('cpi_notes_full'))
        st.markdown("---")
        
        display_macro_card(t('core_pce_title'), df.get('CorePCE'), 'CorePCE', df_original=df_original, notes=t('core_pce_notes'))
            
    with col2:
        display_macro_card(t('core_cpi_title'), df.get('CPICore'), 'CPICore', df_original=df_original, notes=t('core_cpi_notes'))
        st.markdown("---")
        display_macro_card(t('ppi_title'), df.get('PPI'), 'PPI', df_original=df_original, notes=t('ppi_notes_full'))

# === 3. Economy ===
st.markdown("---")
with st.expander(t('us_economic_section_economy'), expanded=True):
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
with st.expander(t('michigan_inflation_title'), expanded=True):
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

# === 4. Manufacturing ===
st.markdown("---")
with st.expander(t('us_economic_section_manufacturing'), expanded=True):
    st.caption(t('manufacturing_indicators_desc'))

    # Manufacturing indicators in 2x2 grid
    mfg_col1, mfg_col2 = st.columns(2)

    with mfg_col1:
        st.markdown(f"#### {t('empire_state_mfg_title')}")
        empire_series = df.get('Empire_State_Mfg')
        show_metric_with_sparkline(t('empire_state_mfg_label'), empire_series, 'Empire_State_Mfg', "idx", "Empire_State_Mfg", notes=t('empire_state_mfg_notes'))
        if empire_series is not None and not empire_series.isna().all():
            fig_empire = go.Figure()
            fig_empire.add_trace(go.Scatter(x=empire_series.index, y=empire_series.values, name='Empire State', line=dict(color='#4CAF50')))
            fig_empire.add_hline(y=0, line_dash='dash', line_color='red', annotation_text=t('manufacturing_boundary'))
            fig_empire.update_layout(height=150, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig_empire, use_container_width=True, key=f"empire_mfg_{uuid.uuid4().hex[:8]}")
        
        st.markdown("---")
        st.markdown(f"#### {t('dallas_fed_mfg_title')}")
        dallas_series = df.get('Dallas_Fed_Mfg')
        show_metric_with_sparkline(t('dallas_fed_mfg_label'), dallas_series, 'Dallas_Fed_Mfg', "idx", "Dallas_Fed_Mfg", notes=t('dallas_fed_mfg_notes'))
        if dallas_series is not None and not dallas_series.isna().all():
            fig_dallas = go.Figure()
            fig_dallas.add_trace(go.Scatter(x=dallas_series.index, y=dallas_series.values, name='Dallas Fed', line=dict(color='#FF9800')))
            fig_dallas.add_hline(y=0, line_dash='dash', line_color='red', annotation_text=t('manufacturing_boundary'))
            fig_dallas.update_layout(height=150, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig_dallas, use_container_width=True, key=f"dallas_mfg_{uuid.uuid4().hex[:8]}")

    with mfg_col2:
        st.markdown(f"#### {t('philly_fed_mfg_title')}")
        philly_series = df.get('Philly_Fed_Mfg')
        show_metric_with_sparkline(t('philly_fed_mfg_label'), philly_series, 'Philly_Fed_Mfg', "idx", "Philly_Fed_Mfg", notes=t('philly_fed_mfg_notes'))
        if philly_series is not None and not philly_series.isna().all():
            fig_philly = go.Figure()
            fig_philly.add_trace(go.Scatter(x=philly_series.index, y=philly_series.values, name='Philly Fed', line=dict(color='#2196F3')))
            fig_philly.add_hline(y=0, line_dash='dash', line_color='red', annotation_text=t('manufacturing_boundary'))
            fig_philly.update_layout(height=150, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig_philly, use_container_width=True, key=f"philly_mfg_{uuid.uuid4().hex[:8]}")
        
        st.markdown("---")
        st.markdown(f"#### {t('richmond_fed_mfg_title')}")
        
        # Richmond Fed: Fetch from web (not in main DataFrame)
        richmond_data = get_richmond_fed_survey()
        
        if richmond_data is not None:
            # Display current value
            current_val = richmond_data.get('current')
            change_val = richmond_data.get('change')
            data_date = richmond_data.get('date')
            release_date = richmond_data.get('release_date')
            
            if current_val is not None:
                delta_str = f"{change_val:+.1f} pts" if change_val is not None else None
                # Import help texts
                from utils.help_texts import HELP_EN, HELP_JA
                from utils.i18n import get_current_language
                help_dict = HELP_JA if get_current_language() == 'ja' else HELP_EN
                help_text = help_dict.get('help_Richmond_Fed_Mfg', '')
                st.metric(t('richmond_fed_mfg_label'), f"{current_val:.1f}", delta=delta_str, help=help_text)
            
            # Show both data_period and source_update like other indicators
            if data_date:
                st.caption(f"📅 {t('data_period')}: {data_date} ({t('freq_monthly')})")
            if release_date:
                st.caption(f"🔄 {t('source_update')}: {release_date}")
            
            st.caption(t('richmond_fed_mfg_notes'))
            
            # Plot history if available
            history_df = richmond_data.get('history')
            if history_df is not None and not history_df.empty:
                fig_richmond = go.Figure()
                fig_richmond.add_trace(go.Scatter(
                    x=history_df.index, 
                    y=history_df['Composite Index'].values, 
                    name='Richmond Fed', 
                    line=dict(color='#9C27B0')
                ))
                fig_richmond.add_hline(y=0, line_dash='dash', line_color='red', annotation_text=t('manufacturing_boundary'))
                fig_richmond.update_layout(height=150, margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig_richmond, use_container_width=True, key=f"richmond_mfg_{uuid.uuid4().hex[:8]}")
        else:
            st.info(t('data_fetch_failed'))

    # Additional Manufacturing Indicators
    st.markdown("---")
    mfg_add_col1, mfg_add_col2 = st.columns(2)
    
    with mfg_add_col1:
        st.markdown(f"#### {t('indpro_title')}")
        indpro_series = df.get('INDPRO')
        show_metric_with_sparkline(t('indpro_label'), indpro_series, 'INDPRO', "idx", "INDPRO", notes=t('indpro_notes'))
        if indpro_series is not None and not indpro_series.isna().all():
            styled_line_chart(indpro_series, height=150)
    
    with mfg_add_col2:
        st.markdown(f"#### {t('neworder_title')}")
        neworder_series = df.get('NEWORDER')
        show_metric_with_sparkline(t('neworder_label'), neworder_series, 'NEWORDER', "idx", "NEWORDER", notes=t('neworder_notes'))
        if neworder_series is not None and not neworder_series.isna().all():
            styled_line_chart(neworder_series, height=150)

    # Manufacturing guide
    with st.expander(t('manufacturing_guide').split('\n')[0], expanded=False):
        st.markdown(t('manufacturing_guide'))

# === 5. Services (Nonmanufacturing) ===
st.markdown("---")
with st.expander(t('us_economic_section_services'), expanded=True):
    st.caption(t('services_indicators_desc'))

    # Services indicators in 2x2 grid
    svc_col1, svc_col2 = st.columns(2)

    with svc_col1:
        st.markdown(f"#### {t('philly_fed_services_title')}")
        philly_svc_series = df.get('Philly_Fed_Services')
        show_metric_with_sparkline(t('philly_fed_services_label'), philly_svc_series, 'Philly_Fed_Services', "idx", "Philly_Fed_Services", notes=t('philly_fed_services_notes'))
        if philly_svc_series is not None and not philly_svc_series.isna().all():
            fig_philly_svc = go.Figure()
            fig_philly_svc.add_trace(go.Scatter(x=philly_svc_series.index, y=philly_svc_series.values, name='Philly Fed Services', line=dict(color='#2196F3')))
            fig_philly_svc.add_hline(y=0, line_dash='dash', line_color='red', annotation_text=t('services_boundary'))
            fig_philly_svc.update_layout(height=150, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig_philly_svc, use_container_width=True, key=f"philly_svc_{uuid.uuid4().hex[:8]}")
        
        st.markdown("---")
        st.markdown(f"#### {t('ny_fed_services_title')}")
        ny_svc_series = df.get('NY_Fed_Services')
        show_metric_with_sparkline(t('ny_fed_services_label'), ny_svc_series, 'NY_Fed_Services', "idx", "NY_Fed_Services", notes=t('ny_fed_services_notes'))
        if ny_svc_series is not None and not ny_svc_series.isna().all():
            fig_ny_svc = go.Figure()
            fig_ny_svc.add_trace(go.Scatter(x=ny_svc_series.index, y=ny_svc_series.values, name='NY Fed Services', line=dict(color='#4CAF50')))
            fig_ny_svc.add_hline(y=0, line_dash='dash', line_color='red', annotation_text=t('services_boundary'))
            fig_ny_svc.update_layout(height=150, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig_ny_svc, use_container_width=True, key=f"ny_svc_{uuid.uuid4().hex[:8]}")

    with svc_col2:
        st.markdown(f"#### {t('dallas_fed_services_title')}")
        dallas_svc_series = df.get('Dallas_Fed_Services')
        show_metric_with_sparkline(t('dallas_fed_services_label'), dallas_svc_series, 'Dallas_Fed_Services', "idx", "Dallas_Fed_Services", notes=t('dallas_fed_services_notes'))
        if dallas_svc_series is not None and not dallas_svc_series.isna().all():
            fig_dallas_svc = go.Figure()
            fig_dallas_svc.add_trace(go.Scatter(x=dallas_svc_series.index, y=dallas_svc_series.values, name='Dallas Fed Services', line=dict(color='#FF9800')))
            fig_dallas_svc.add_hline(y=0, line_dash='dash', line_color='red', annotation_text=t('services_boundary'))
            fig_dallas_svc.update_layout(height=150, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig_dallas_svc, use_container_width=True, key=f"dallas_svc_{uuid.uuid4().hex[:8]}")
        
        st.markdown("---")
        st.markdown(f"#### {t('richmond_fed_services_title')}")
        
        # Richmond Fed Services: Fetch from web (not in main DataFrame)
        richmond_svc_data = get_richmond_fed_services_survey()
        
        if richmond_svc_data is not None:
            # Display current value
            current_val = richmond_svc_data.get('current')
            change_val = richmond_svc_data.get('change')
            data_date = richmond_svc_data.get('date')
            release_date = richmond_svc_data.get('release_date')
            
            if current_val is not None:
                delta_str = f"{change_val:+.1f} pts" if change_val is not None else None
                # Import help texts
                from utils.help_texts import HELP_EN, HELP_JA
                from utils.i18n import get_current_language
                help_dict = HELP_JA if get_current_language() == 'ja' else HELP_EN
                help_text = help_dict.get('help_Richmond_Fed_Services', '')
                st.metric(t('richmond_fed_services_label'), f"{current_val:.1f}", delta=delta_str, help=help_text)
            
            # Show both data_period and source_update like other indicators
            if data_date:
                st.caption(f"📅 {t('data_period')}: {data_date} ({t('freq_monthly')})")
            if release_date:
                st.caption(f"🔄 {t('source_update')}: {release_date}")
            
            st.caption(t('richmond_fed_services_notes'))
            
            # Plot history if available
            history_df = richmond_svc_data.get('history')
            if history_df is not None and not history_df.empty:
                fig_richmond_svc = go.Figure()
                fig_richmond_svc.add_trace(go.Scatter(
                    x=history_df.index, 
                    y=history_df['Composite Index'].values, 
                    name='Richmond Fed Services', 
                    line=dict(color='#9C27B0')
                ))
                fig_richmond_svc.add_hline(y=0, line_dash='dash', line_color='red', annotation_text=t('services_boundary'))
                fig_richmond_svc.update_layout(height=150, margin=dict(l=0, r=0, t=20, b=0))
                st.plotly_chart(fig_richmond_svc, use_container_width=True, key=f"richmond_svc_{uuid.uuid4().hex[:8]}")
        else:
            st.info(t('data_fetch_failed'))

    # Services guide
    with st.expander(t('services_guide').split('\n')[0], expanded=False):
        st.markdown(t('services_guide'))

# === 6. Leading Indicators ===
st.markdown("---")
with st.expander(f"📈 {t('us_economic_section_leading')}", expanded=True):
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
with st.expander(f"🏠 {t('us_economic_section_housing')}", expanded=True):
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
