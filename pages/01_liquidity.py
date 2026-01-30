# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 1: Liquidity & Rates
流動性、金利、Fed バランスシート、銀行セクター
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
    get_pe_ratios,
    get_crypto_leverage_data,
    record_api_status,
    show_metric,
    show_metric_with_sparkline,
    plot_dual_axis,
    plot_soma_composition,
    styled_line_chart,
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
st.subheader(t('liquidity_title'))

# === VALUATION & LEVERAGE SECTION ===
pe_data = get_pe_ratios()
leverage_data = get_crypto_leverage_data()

# Record API status for health monitoring (keep outside expander)
record_api_status('SP500_PE', pe_data is not None and pe_data.get('sp500_pe') is not None)
record_api_status('NASDAQ_PE', pe_data is not None and pe_data.get('nasdaq_pe') is not None)
record_api_status('BTC_Funding_Rate', leverage_data is not None and leverage_data.get('btc_funding_rate') is not None)
record_api_status('BTC_Open_Interest', leverage_data is not None and leverage_data.get('btc_open_interest') is not None)
record_api_status('BTC_Long_Short_Ratio', leverage_data is not None and leverage_data.get('btc_long_short_ratio') is not None)
record_api_status('ETH_Funding_Rate', leverage_data is not None and leverage_data.get('eth_funding_rate') is not None)
record_api_status('ETH_Open_Interest', leverage_data is not None and leverage_data.get('eth_open_interest') is not None)

with st.expander(t('valuation_leverage'), expanded=True):
    st.caption(t('valuation_leverage_desc'))

    # Show data source timestamps
    data_sources = []
    if pe_data and pe_data.get('timestamp'):
        data_sources.append(f"P/E: {pe_data['timestamp'][:16]}")
    if leverage_data and leverage_data.get('timestamp'):
        data_sources.append(f"Leverage: {leverage_data['timestamp'][:16]}")
    if leverage_data and leverage_data.get('data_source'):
        data_sources.append(f"Source: {leverage_data['data_source']}")
    if data_sources:
        st.caption(f"🔄 {t('source_update')}: {' | '.join(data_sources)}")

    col_val1, col_val2, col_val3, col_val4, col_val5 = st.columns(5)

    with col_val1:
        if pe_data and pe_data.get('sp500_pe'):
            pe = pe_data['sp500_pe']
            avg = pe_data['sp500_pe_avg']
            delta = pe - avg
            color = "🔴" if pe > 25 else "🟡" if pe > 20 else "🟢"
            st.metric(
                f"{color} {t('sp500_pe')}",
                f"{pe:.1f}",
                delta=f"{delta:+.1f} {t('vs_avg')} ({avg:.1f})",
                help=t('sp500_pe_help')
            )
        else:
            st.metric(t('sp500_pe'), t('loading'))

    with col_val2:
        if pe_data and pe_data.get('nasdaq_pe'):
            pe = pe_data['nasdaq_pe']
            color = "🔴" if pe > 35 else "🟡" if pe > 28 else "🟢"
            st.metric(
                f"{color} {t('nasdaq_pe')}",
                f"{pe:.1f}",
                help=t('nasdaq_pe_help')
            )
        else:
            st.metric(t('nasdaq_pe'), t('loading'))

    with col_val3:
        if leverage_data and leverage_data.get('btc_funding_rate') is not None:
            fr = leverage_data['btc_funding_rate']
            if fr > 0.05:
                color = "🔴"
                status = t('long_heavy')
            elif fr < -0.05:
                color = "🔵"
                status = t('short_heavy')
            else:
                color = "🟢"
                status = t('neutral')
            st.metric(
                f"{color} {t('btc_funding_rate')}",
                f"{fr:.4f}%",
                delta=status,
                help=t('funding_rate_help')
            )
        else:
            st.metric(t('btc_funding_rate'), t('loading'))

    with col_val4:
        if leverage_data and leverage_data.get('eth_funding_rate') is not None:
            fr = leverage_data['eth_funding_rate']
            if fr > 0.05:
                color = "🔴"
                status = t('long_heavy')
            elif fr < -0.05:
                color = "🔵"
                status = t('short_heavy')
            else:
                color = "🟢"
                status = t('neutral')
            st.metric(
                f"{color} {t('eth_funding_rate')}",
                f"{fr:.4f}%",
                delta=status,
                help=t('funding_rate_help')
            )
        else:
            st.metric(t('eth_funding_rate'), t('loading'))

    with col_val5:
        if leverage_data and leverage_data.get('btc_long_short_ratio'):
            ratio = leverage_data['btc_long_short_ratio']
            if ratio > 1.5:
                color = "🔴"
                status = t('long_biased')
            elif ratio < 0.7:
                color = "🔵"
                status = t('short_biased')
            else:
                color = "🟢"
                status = t('balanced')
            st.metric(
                f"{color} {t('btc_ls_ratio')}",
                f"{ratio:.2f}",
                delta=status,
                help=t('ls_ratio_help')
            )
        else:
            st.metric(t('btc_ls_ratio'), t('loading'))

# === Open Interest ===
if leverage_data:
    with st.expander(t('open_interest_title'), expanded=True):
        col_btc, col_eth = st.columns(2)
        
        with col_btc:
            oi = leverage_data.get('btc_open_interest', 0)
            avg = leverage_data.get('btc_oi_avg_30d')
            ath = leverage_data.get('btc_oi_ath')
            
            if oi and avg:
                pct_vs_avg = ((oi - avg) / avg) * 100
                pct_vs_ath = (oi / ath * 100) if ath else 0
                
                if pct_vs_avg > 20:
                    color = "🔴"
                    status = t('danger_zone')
                elif pct_vs_avg > 5:
                    color = "🟡"
                    status = t('elevated')
                elif pct_vs_avg < -20:
                    color = "🔵"
                    status = t('low')
                else:
                    color = "🟢"
                    status = t('normal')
                
                st.metric(
                    f"{color} {t('btc_open_interest')}",
                    f"{oi:,.0f} BTC",
                    delta=f"{pct_vs_avg:+.1f}% {t('vs_30d_avg')}",
                    help=f"30d avg: {avg:,.0f} BTC | 30d high: {ath:,.0f} BTC ({pct_vs_ath:.0f}%)"
                )
                oi_source = leverage_data.get('btc_oi_data_source', 'Bybit/OKX')
                st.caption(f"📊 {t('ath_ratio')}: **{pct_vs_ath:.0f}%** | {t('status')}: **{status}** | {t('source')}: {oi_source}")
            else:
                days = leverage_data.get('btc_oi_days_available', 0)
                st.metric(t('btc_open_interest'), f"{oi:,.0f} BTC" if oi else t('loading'))
                if oi and days > 0:
                    st.caption(t('accumulating_data', days=days))
                elif oi:
                    st.caption(t('accumulating_data', days=0))
    
        with col_eth:
            oi = leverage_data.get('eth_open_interest', 0)
            avg = leverage_data.get('eth_oi_avg_30d')
            ath = leverage_data.get('eth_oi_ath')
            
            if oi and avg:
                pct_vs_avg = ((oi - avg) / avg) * 100
                pct_vs_ath = (oi / ath * 100) if ath else 0
                
                if pct_vs_avg > 20:
                    color = "🔴"
                    status = t('danger_zone')
                elif pct_vs_avg > 5:
                    color = "🟡"
                    status = t('elevated')
                elif pct_vs_avg < -20:
                    color = "🔵"
                    status = t('low')
                else:
                    color = "🟢"
                    status = t('normal')
                
                st.metric(
                    f"{color} {t('eth_open_interest')}",
                    f"{oi:,.0f} ETH",
                    delta=f"{pct_vs_avg:+.1f}% {t('vs_30d_avg')}",
                    help=f"30d avg: {avg:,.0f} ETH | 30d high: {ath:,.0f} ETH ({pct_vs_ath:.0f}%)"
                )
                oi_source = leverage_data.get('eth_oi_data_source', 'Bybit/OKX')
                st.caption(f"📊 {t('ath_ratio')}: **{pct_vs_ath:.0f}%** | {t('status')}: **{status}** | {t('source')}: {oi_source}")
            else:
                days = leverage_data.get('eth_oi_days_available', 0)
                st.metric(t('eth_open_interest'), f"{oi:,.0f} ETH" if oi else t('loading'))
                if oi and days > 0:
                    st.caption(t('accumulating_data', days=days))
                elif oi:
                    st.caption(t('accumulating_data', days=0))
        
        st.caption(t('open_interest_guide'))

st.markdown("---")
with st.expander(t('net_liquidity'), expanded=True):
    col1, col2 = st.columns([1, 3])
    with col1:
        # Get S&P500 date for extra_sources
        extra_src = {'_primary': 'Fed BS'}  # Primary source label
        if 'SP500' in df.columns and not df.get('SP500', pd.Series()).isna().all():
            sp500_series = df['SP500'].dropna()
            if len(sp500_series) > 0:
                sp500_date = sp500_series.index[-1].strftime('%Y-%m-%d')
                extra_src['S&P500'] = sp500_date
        show_metric_with_sparkline(t('net_liquidity'), df.get('Net_Liquidity'), 'Net_Liquidity', "B", "Net_Liquidity", notes=t('net_liquidity_notes'), extra_sources=extra_src)
    with col2:
        st.markdown(f"##### {t('net_liquidity_chart_title')}")
        plot_dual_axis(df, 'Net_Liquidity', 'SP500', 'Net Liquidity (L)', 'S&P 500 (R)')

st.markdown("---")
with st.expander(t('liquidity_components'), expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {t('on_rrp')}")
        show_metric_with_sparkline(t('on_rrp'), df.get('ON_RRP'), 'ON_RRP', "B", "ON_RRP", notes=t('on_rrp_notes'))
        if 'ON_RRP' in df.columns and not df.get('ON_RRP', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['ON_RRP']], height=250)
        
        st.markdown("")
        
        st.markdown(f"#### {t('tga')}")
        show_metric_with_sparkline(t('tga'), df.get('TGA'), 'TGA', "B", "TGA", notes=t('tga_notes'))
        if 'TGA' in df.columns and not df.get('TGA', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['TGA']], height=250)

    with col2:
        st.markdown(f"#### {t('reserves')}")
        show_metric_with_sparkline(t('reserves'), df.get('Reserves'), 'Reserves', "B", "Reserves", notes=t('reserves_notes'))
        if 'Reserves' in df.columns and not df.get('Reserves', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['Reserves']], height=250)

st.markdown("---")
with st.expander(t('market_plumbing'), expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {t('srf')}")
        show_metric_with_sparkline(t('srf'), df.get('SRF'), 'SRF', "B", "SRF", notes=t('srf_notes'))
        if 'SRF' in df.columns and not df.get('SRF', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['SRF']], height=200)
        
        st.markdown("")
        
        st.markdown(f"#### {t('sofr')}")
        show_metric_with_sparkline(t('sofr'), df.get('SOFR'), 'SOFR', "%", "SOFR", notes=t('sofr_notes'), decimal_places=3)
        if 'SOFR' in df.columns and not df.get('SOFR', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['SOFR']], height=200)

    with col2:
        st.markdown(f"#### {t('fima')}")
        show_metric_with_sparkline(t('fima'), df.get('FIMA'), 'FIMA', "B", "FIMA", notes=t('fima_notes'))
        if 'FIMA' in df.columns and not df.get('FIMA', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['FIMA']], height=200)
        
        st.markdown("")
        
        st.markdown(f"#### {t('effr_iorb')}")
        diff = None
        if 'EFFR' in df.columns and 'IORB' in df.columns:
            diff = (df['EFFR'] - df['IORB']) * 100
            diff.name = 'EFFR_IORB'  # Set name for proper handling
        # notesを除いて表示（日付の後にnotesを手動表示するため）
        show_metric(t('effr_iorb'), diff, "bps", explanation_key="EFFR_IORB")
        
        # EFFR-IORB用の日付情報を手動表示（計算値なのでEFFRの日付を使用）
        if 'EFFR' in df.columns and hasattr(df, 'attrs'):
            effr_date = df.attrs.get('last_valid_dates', {}).get('EFFR')
            effr_release = df.attrs.get('fred_release_dates', {}).get('EFFR')
            if effr_date:
                freq_key = DATA_FREQUENCY.get('EFFR', '')
                if freq_key:
                    freq_label = t(f'freq_{freq_key}')
                    st.caption(f"📅 {t('data_period')}: {effr_date} ({freq_label})")
                else:
                    st.caption(f"📅 {t('data_period')}: {effr_date}")
            if effr_release:
                st.caption(f"🔄 {t('source_update')}: {effr_release}")
        # notesは日付の後に表示（他の指標と同じ順序にする）
        st.caption(t('effr_iorb_notes'))
        
        # EFFR-IORB専用sparkline（計算値なので手動で追加）
        if diff is not None and not diff.isna().all():
            recent_diff = diff.tail(60)
            st.caption(f"📊 {t('sparkline_label')}")
            fig_spark = go.Figure()
            fig_spark.add_trace(go.Scatter(
                x=recent_diff.index,
                y=recent_diff.values,
                mode='lines',
                line=dict(color='#FF9F43', width=2),
                fill='tozeroy',
                fillcolor='rgba(255, 159, 67, 0.3)',
                showlegend=False
            ))
            fig_spark.update_layout(
                height=100,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                hovermode=False
            )
            st.plotly_chart(fig_spark, use_container_width=True, config={'displayModeBar': False},
                           key=f"spark_effr_iorb_{uuid.uuid4().hex[:8]}")
        
        rate_cols = ['EFFR', 'IORB']
        valid_rates = [c for c in rate_cols if c in df.columns and not df.get(c, pd.Series()).isna().all()]
        if valid_rates:
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[valid_rates], height=200)

# === FF Target Rate (Upper/Lower) ===
st.markdown("---")
with st.expander(t('ff_target_rate'), expanded=True):
    col_ff1, col_ff2 = st.columns(2)

    with col_ff1:
        st.markdown(f"#### {t('ff_upper')}")
        show_metric_with_sparkline(t('ff_upper'), df.get('FedFundsUpper'), 'FedFundsUpper', "%", "FF_Upper", notes=t('ff_upper_notes'), decimal_places=2)
        if 'FedFundsUpper' in df.columns and not df.get('FedFundsUpper', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['FedFundsUpper']], height=200)

    with col_ff2:
        st.markdown(f"#### {t('ff_lower')}")
        show_metric_with_sparkline(t('ff_lower'), df.get('FedFundsLower'), 'FedFundsLower', "%", "FF_Lower", notes=t('ff_lower_notes'), decimal_places=2)
        if 'FedFundsLower' in df.columns and not df.get('FedFundsLower', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['FedFundsLower']], height=200)

st.markdown("---")
with st.expander(t('fed_balance_sheet'), expanded=True):
    # RMP Status (i18n support)
    # Get status type and weekly change from data
    rmp_status_type_series = df.get('RMP_Status_Type')
    rmp_status_type = rmp_status_type_series.iloc[-1] if hasattr(rmp_status_type_series, 'iloc') and len(rmp_status_type_series) > 0 else 'monitoring'
    rmp_weekly_change_series = df.get('RMP_Weekly_Change')
    rmp_weekly_change = rmp_weekly_change_series.iloc[-1] if hasattr(rmp_weekly_change_series, 'iloc') and len(rmp_weekly_change_series) > 0 else None
    rmp_active_series = df.get('RMP_Alert_Active', pd.Series([False]))
    rmp_active = rmp_active_series.iloc[-1] if hasattr(rmp_active_series, 'iloc') and len(rmp_active_series) > 0 else False

    # Build translated RMP status text
    if rmp_status_type == 'monitoring' or rmp_weekly_change is None:
        rmp_status = t('rmp_monitoring')
    elif rmp_status_type == 'active':
        rmp_status = t('rmp_active').replace('${value}', f'{rmp_weekly_change:.1f}')
    elif rmp_status_type == 'accelerating':
        rmp_status = t('rmp_accelerating').replace('${value}', f'{rmp_weekly_change:.1f}')
    elif rmp_status_type == 'slowing':
        rmp_status = t('rmp_slowing').replace('${value}', f'{rmp_weekly_change:.1f}')
    elif rmp_status_type == 'selling':
        rmp_status = t('rmp_selling').replace('${value}', f'{rmp_weekly_change:.1f}')
    else:
        rmp_status = t('rmp_monitoring')

    if rmp_active:
        st.info(f"{t('rmp_status')}: {rmp_status}")
    else:
        st.warning(f"ℹ️ {t('rmp_status')}: {rmp_status}")

    st.markdown(f"##### {t('soma_composition')}")
    plot_soma_composition(df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"#### {t('soma_total')}")
        show_metric_with_sparkline(t('soma_total'), df.get('SOMA_Total'), 'SOMA_Total', "B", "SOMA_Total", notes=t('soma_total_notes'))

    with col2:
        st.markdown(f"#### {t('soma_treasury')}")
        show_metric_with_sparkline(t('soma_treasury'), df.get('SOMA_Treasury'), 'SOMA_Treasury', "B", "SOMA_Treasury", notes=t('soma_treasury_notes'))
        if 'SOMA_Treasury' in df.columns and not df.get('SOMA_Treasury', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['SOMA_Treasury']], height=200)

    with col3:
        st.markdown(f"#### {t('soma_bills')}")
        show_metric_with_sparkline(t('soma_bills'), df.get('SOMA_Bills'), 'SOMA_Bills', "B", "SOMA_Bills", notes=t('soma_bills_notes'))
        if 'SOMA_Bills' in df.columns and not df.get('SOMA_Bills', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['SOMA_Bills']], height=200)

st.markdown("---")
with st.expander(t('emergency_loans'), expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {t('total_loans')}")
        show_metric_with_sparkline(t('total_loans'), df.get('Total_Loans'), 'Total_Loans', "B", "Window", notes=t('total_loans_notes'))
        if 'Total_Loans' in df.columns and not df.get('Total_Loans', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['Total_Loans']], height=250)

    with col2:
        st.markdown(f"#### {t('primary_credit')}")
        show_metric_with_sparkline(t('primary_credit'), df.get('Primary_Credit'), 'Primary_Credit', "B", "Primary", notes=t('primary_credit_notes'), alert_func=lambda x: x>1)
        if 'Primary_Credit' in df.columns and not df.get('Primary_Credit', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['Primary_Credit']], height=250)

st.markdown("---")
with st.expander(t('risk_bonds'), expanded=True):
    st.caption(t('risk_bonds_desc'))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"#### {t('vix_index')}")
        show_metric_with_sparkline(t('vix_index'), df.get('VIX'), 'VIX', "pt", "VIX", notes=t('vix_notes'), alert_func=lambda x: x>20)
        if 'VIX' in df.columns and not df.get('VIX', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['VIX']], height=200)

    with col2:
        st.markdown(f"#### {t('credit_spread')}")
        show_metric_with_sparkline(t('credit_spread'), df.get('Credit_Spread'), 'Credit_Spread', "%", "Credit_Spread", notes=t('credit_spread_notes'), decimal_places=3)
        if 'Credit_Spread' in df.columns and not df.get('Credit_Spread', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['Credit_Spread']], height=200)

    with col3:
        st.markdown(f"#### {t('us_10y_yield')}")
        show_metric_with_sparkline(t('us_10y_yield'), df.get('US_TNX'), 'US_TNX', "%", "US_TNX", notes=t('us_10y_notes'), decimal_places=3)
        if 'US_TNX' in df.columns and not df.get('US_TNX', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['US_TNX']], height=200)

    with col4:
        st.markdown(f"#### {t('t10y2y')}")
        show_metric_with_sparkline(t('t10y2y'), df.get('T10Y2Y'), 'T10Y2Y', "%", "T10Y2Y", notes=t('t10y2y_notes'), decimal_places=3)
        if 'T10Y2Y' in df.columns and not df.get('T10Y2Y', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['T10Y2Y']], height=200)

# === Corporate Bond ETFs ===
st.markdown("---")
with st.expander(t('corp_bond_etf_section'), expanded=True):
    st.caption(t('corp_bond_etf_desc'))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {t('hyg')}")
        show_metric_with_sparkline(t('hyg'), df.get('HYG'), 'HYG', "$", "HYG", notes=t('hyg_notes'), decimal_places=2)
        if 'HYG' in df.columns and not df.get('HYG', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['HYG']], height=200)

    with col2:
        st.markdown(f"#### {t('lqd')}")
        show_metric_with_sparkline(t('lqd'), df.get('LQD'), 'LQD', "$", "LQD", notes=t('lqd_notes'), decimal_places=2)
        if 'LQD' in df.columns and not df.get('LQD', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['LQD']], height=200)
