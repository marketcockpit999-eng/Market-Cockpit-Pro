# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 11: Market Analysis Lab
マクロ分析ラボ
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import t, show_metric_with_sparkline, EXPLANATIONS, DATA_FREQUENCY

df = st.session_state.get('df')
if df is None:
    st.error(t('error_data_not_loaded'))
    st.stop()

st.subheader(t('analysis_lab_title'))
st.caption(t('lab_subtitle'))

# ========== Global Liquidity Proxy ==========
st.markdown("---")
st.markdown(f"### {t('lab_glp_section')}")

with st.expander(t('lab_glp_about'), expanded=False):
    st.markdown(t('lab_glp_explanation'))

if 'Global_Liquidity_Proxy' in df.columns and not df.get('Global_Liquidity_Proxy', pd.Series()).isna().all():
    gl = df['Global_Liquidity_Proxy'].dropna()
    
    glp_latest_date = None
    if hasattr(df, 'attrs') and 'last_valid_dates' in df.attrs:
        glp_latest_date = df.attrs['last_valid_dates'].get('Global_Liquidity_Proxy')
    
    col1, col2 = st.columns([1,2])
    with col1:
        st.metric("GLP", f"${gl.iloc[-1]/1000:.2f}T", help="Fed + ECB - TGA - RRP")
        if glp_latest_date:
            st.caption(f"{t('lab_data_period')}: {glp_latest_date}")
            st.caption(f"🔄 {t('lab_calculated')}")
    with col2:
        if 'SP500' in df.columns:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Scatter(x=gl.index, y=gl, name='GLP', line=dict(color='cyan')), secondary_y=False)
            fig.add_trace(go.Scatter(x=df.index, y=df['SP500'], name='S&P500', line=dict(color='orange', dash='dot')), secondary_y=True)
            fig.update_layout(template='plotly_dark', height=280, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)
else:
    st.warning(t('lab_glp_no_data'))

# === GLP YoY Growth ===
if 'Global_Liquidity_Proxy' in df.columns and not df.get('Global_Liquidity_Proxy', pd.Series()).isna().all():
    gl_series = df['Global_Liquidity_Proxy'].dropna()
    
    st.markdown(f"##### 📊 {t('yoy_growth')}")
    st.caption(t('yoy_growth_desc'))
    
    if len(gl_series) > 252:
        yoy_growth = gl_series.pct_change(periods=252) * 100
        yoy_growth = yoy_growth.dropna().tail(365)
        
        if not yoy_growth.empty:
            fig_yoy = go.Figure()
            colors = ['#00e676' if v >= 0 else '#ff1744' for v in yoy_growth]
            
            fig_yoy.add_trace(go.Bar(
                x=yoy_growth.index,
                y=yoy_growth,
                marker_color=colors,
                name='YoY %'
            ))
            
            fig_yoy.add_hline(y=0, line_dash="dash", line_color="white", line_width=1)
            
            fig_yoy.update_layout(
                template='plotly_dark',
                height=200,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                yaxis_title="YoY (%)"
            )
            st.plotly_chart(fig_yoy, use_container_width=True)
            
            current_yoy = yoy_growth.iloc[-1]
            if current_yoy > 0:
                st.success(f"{t('liquidity_expanding')}: {current_yoy:+.2f}% YoY")
            else:
                st.warning(f"{t('liquidity_contracting')}: {current_yoy:+.2f}% YoY")
    else:
        st.info(t('insufficient_data_yoy'))

# ========== M2 Velocity ==========
st.markdown("---")
st.markdown(f"### {t('lab_m2v_section')}")

with st.expander(t('lab_m2v_about'), expanded=False):
    st.markdown(t('lab_m2v_explanation'))

if 'M2_Velocity' in df.columns and not df.get('M2_Velocity', pd.Series()).isna().all():
    m2v = df['M2_Velocity'].dropna()
    m2v_val = m2v.iloc[-1]
    
    m2v_latest_date = None
    m2v_release_date = None
    if hasattr(df, 'attrs'):
        if 'last_valid_dates' in df.attrs:
            m2v_latest_date = df.attrs['last_valid_dates'].get('M2_Velocity')
        if 'fred_release_dates' in df.attrs:
            m2v_release_date = df.attrs['fred_release_dates'].get('M2_Velocity')
    
    if m2v_val < 1.2:
        status = t('lab_m2v_historic_low')
    elif m2v_val < 1.5:
        status = t('lab_m2v_low')
    else:
        status = t('lab_m2v_normal')
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("M2V", f"{m2v_val:.2f}", help="GDP ÷ M2")
        st.caption(status)
        if m2v_latest_date:
            st.caption(f"{t('lab_data_period')}: {m2v_latest_date}")
        if m2v_release_date:
            st.caption(f"{t('lab_source_update')}: {m2v_release_date}")
    with col2:
        st.line_chart(m2v, height=200)
else:
    st.info(t('lab_m2v_unavailable'))

# ========== Financial Stress Index ==========
st.markdown("---")
st.markdown(f"### {t('lab_fsi_section')}")

with st.expander(t('lab_fsi_about'), expanded=False):
    st.markdown(t('lab_fsi_explanation'))

if 'Financial_Stress' in df.columns and not df.get('Financial_Stress', pd.Series()).isna().all():
    fs = df['Financial_Stress'].dropna()
    fs_val = fs.iloc[-1]
    
    fsi_latest_date = None
    fsi_release_date = None
    if hasattr(df, 'attrs'):
        if 'last_valid_dates' in df.attrs:
            fsi_latest_date = df.attrs['last_valid_dates'].get('Financial_Stress')
        if 'fred_release_dates' in df.attrs:
            fsi_release_date = df.attrs['fred_release_dates'].get('Financial_Stress')
    
    if fs_val < -0.5:
        status = t('lab_fsi_loose')
    elif fs_val < 0.5:
        status = t('lab_fsi_normal')
    elif fs_val < 1.5:
        status = t('lab_fsi_caution')
    else:
        status = t('lab_fsi_crisis')
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("FSI", f"{fs_val:.2f}", help="St. Louis Fed Financial Stress Index")
        st.caption(status)
        if fsi_latest_date:
            st.caption(f"{t('lab_data_period')}: {fsi_latest_date}")
        if fsi_release_date:
            st.caption(f"{t('lab_source_update')}: {fsi_release_date}")
    with col2:
        st.line_chart(fs.tail(500), height=200)
else:
    st.info(t('lab_fsi_unavailable'))

# ========== Lag Correlation Analysis ==========
st.markdown("---")
st.markdown(f"### {t('lab_lag_correlation')}")
st.caption(t('lab_lag_desc'))

def calculate_lag_correlation(series1, series2, max_lag=60):
    """Calculate cross-correlation at different lags"""
    correlations = []
    for lag in range(max_lag + 1):
        if lag == 0:
            corr = series1.corr(series2)
        else:
            corr = series1.iloc[:-lag].reset_index(drop=True).corr(
                series2.iloc[lag:].reset_index(drop=True)
            )
        correlations.append((lag, corr))
    return correlations

if 'Global_Liquidity_Proxy' in df.columns and not df.get('Global_Liquidity_Proxy', pd.Series()).isna().all():
    gl_clean = df['Global_Liquidity_Proxy'].dropna()
    
    target_col = st.selectbox(t('lab_compare_with'), ["SP500", "BTC"], key="lag_target")
    
    if target_col in df.columns and not df.get(target_col, pd.Series()).isna().all():
        target_clean = df[target_col].dropna()
        
        common_idx = gl_clean.index.intersection(target_clean.index)
        if len(common_idx) > 100:
            gl_aligned = gl_clean.loc[common_idx]
            target_aligned = target_clean.loc[common_idx]
            
            correlations = calculate_lag_correlation(gl_aligned, target_aligned, max_lag=60)
            
            best_lag, best_corr = max(correlations, key=lambda x: x[1] if not pd.isna(x[1]) else -1)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric(t('lab_best_lag'), f"{best_lag} days", help=t('lab_lag_help'))
                st.metric(t('lab_correlation'), f"{best_corr:.3f}", help=t('lab_correlation_help'))
                if best_corr > 0.7:
                    st.success(t('lab_strong_positive'))
                elif best_corr > 0.4:
                    st.info(t('lab_moderate'))
                else:
                    st.warning(t('lab_weak'))
            
            with col2:
                lag_df = pd.DataFrame(correlations, columns=['Lag (days)', 'Correlation'])
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=lag_df['Lag (days)'], 
                    y=lag_df['Correlation'],
                    mode='lines+markers',
                    line=dict(color='cyan'),
                    marker=dict(size=4)
                ))
                fig.add_vline(x=best_lag, line_dash="dash", line_color="yellow", annotation_text=f"Best: {best_lag}d")
                fig.update_layout(
                    template='plotly_dark', 
                    height=250, 
                    xaxis_title="Lag (days)",
                    yaxis_title="Correlation",
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(t('lab_insufficient_data_lag'))
    else:
        st.warning(t('lab_target_unavailable', target=target_col))
else:
    st.warning(t('lab_glp_unavailable'))

# ========== Regime Detection ==========
st.markdown("---")
st.markdown(f"### {t('lab_regime_detection')}")
st.caption(t('lab_regime_desc'))

if 'Global_Liquidity_Proxy' in df.columns and not df.get('Global_Liquidity_Proxy', pd.Series()).isna().all():
    gl_series = df['Global_Liquidity_Proxy'].dropna()
    
    if len(gl_series) > 20:
        ma20 = gl_series.rolling(window=20).mean()
        ma20_change = ma20.pct_change(periods=5) * 100
        
        current_change = ma20_change.iloc[-1]
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if current_change > 0:
                st.markdown(t('lab_regime_chance'))
                st.caption(t('lab_liquidity_accelerating'))
            else:
                st.markdown(t('lab_regime_caution'))
                st.caption(t('lab_liquidity_decelerating'))
            
            st.metric(t('lab_ma20_change'), f"{current_change:+.2f}%", help=t('lab_ma20_help'))
        
        with col2:
            regime_df = pd.DataFrame({
                'GLP': gl_series.tail(120),
                'MA20': ma20.tail(120)
            })
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=regime_df.index, y=regime_df['GLP'], name='GLP', line=dict(color='cyan', width=1)))
            fig.add_trace(go.Scatter(x=regime_df.index, y=regime_df['MA20'], name='MA20', line=dict(color='yellow', width=2)))
            fig.update_layout(template='plotly_dark', height=200, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(t('lab_insufficient_data_short'))
else:
    st.warning(t('lab_glp_unavailable'))

# ========== Cross-Asset Liquidity Monitor ==========
st.markdown("---")
st.markdown(f"### {t('lab_cross_spreads')}")
st.caption(t('lab_spreads_desc'))

import yfinance as yf

@st.cache_data(ttl=300)
def fetch_etf_spreads():
    """Fetch bid-ask spreads for major ETFs"""
    etfs = ['SPY', 'TLT', 'LQD', 'HYG', 'GLD', 'SLV', 'USO']
    asset_names = {
        'SPY': 'Equity', 'TLT': 'Long Treasury', 'LQD': 'IG Corp Bond',
        'HYG': 'HY Corp Bond', 'GLD': 'Gold', 'SLV': 'Silver', 'USO': 'Oil'
    }
    results = []
    
    for symbol in etfs:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            bid = info.get('bid', 0) or 0
            ask = info.get('ask', 0) or 0
            last = info.get('regularMarketPrice', 0) or info.get('previousClose', 0) or 1
            
            if bid > 0 and ask > 0:
                spread_pct = ((ask - bid) / last) * 10000
            else:
                spread_pct = None
            
            results.append({
                'Symbol': symbol,
                'Spread (bps)': spread_pct,
                'Asset': asset_names.get(symbol, symbol)
            })
        except:
            results.append({
                'Symbol': symbol,
                'Spread (bps)': None,
                'Asset': asset_names.get(symbol, symbol)
            })
    
    return pd.DataFrame(results)

spread_df = fetch_etf_spreads()

if not spread_df.empty:
    def get_spread_status(spread):
        if spread is None or pd.isna(spread):
            return t('lab_status_na')
        elif spread < 2:
            return t('lab_status_good')
        elif spread < 10:
            return t('lab_status_normal')
        else:
            return t('lab_status_warning')
    
    spread_df['Status'] = spread_df['Spread (bps)'].apply(get_spread_status)
    
    display_df = spread_df[['Symbol', 'Asset', 'Spread (bps)', 'Status']].copy()
    display_df['Spread (bps)'] = display_df['Spread (bps)'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Show market hours notice if many N/A
    na_count = spread_df['Spread (bps)'].isna().sum()
    if na_count >= 3:
        st.caption("⚠️ Bid-Ask data available during US market hours only (9:30-16:00 ET, Mon-Fri)")
    
    valid_spreads = spread_df[spread_df['Spread (bps)'].notna()]
    if not valid_spreads.empty:
        colors = ['#00e676' if s < 2 else '#ffeb3b' if s < 10 else '#ff1744' for s in valid_spreads['Spread (bps)']]
        fig = go.Figure(data=[
            go.Bar(x=valid_spreads['Symbol'], y=valid_spreads['Spread (bps)'], marker_color=colors)
        ])
        fig.update_layout(
            template='plotly_dark', 
            height=200, 
            yaxis_title="Spread (bps)",
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info(t('lab_spreads_no_data'))

# ========== Multi-Region Spread Monitor ==========
st.markdown("---")
st.markdown("### 🌐 Multi-Region Spread Monitor")
st.caption("📊 24-hour Bid-Ask spread monitoring across global markets")

from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # For Python < 3.9, fallback to pytz
    try:
        import pytz
        ZoneInfo = lambda x: pytz.timezone(x)
    except ImportError:
        st.error("⚠️ Timezone library not available. Please install pytz or upgrade to Python 3.9+")
        st.stop()

MARKET_REGIONS = {
    'asia': {
        'name': '🌏 Asia (Tokyo/HK)',
        'tz': 'Asia/Tokyo',
        'open_hour': 9,
        'close_hour': 15,
        'etfs': [
            ('1321.T', 'Nikkei 225 ETF'),
            ('2800.HK', 'HK Tracker Fund'),
            ('EWJ', 'Japan ETF (US-listed)'),
            ('EWH', 'Hong Kong ETF (US-listed)')
        ]
    },
    'europe': {
        'name': '🇪🇺 Europe (London/Frankfurt)',
        'tz': 'Europe/London',
        'open_hour': 8,
        'close_hour': 16,
        'etfs': [
            ('ISF.L', 'FTSE 100 ETF'),
            ('EXS1.DE', 'DAX ETF'),
            ('VGK', 'Europe ETF (US-listed)'),
            ('EWU', 'UK ETF (US-listed)')
        ]
    },
    'us': {
        'name': '🇺🇸 US (NYSE/NASDAQ)',
        'tz': 'America/New_York',
        'open_hour': 9,
        'close_hour': 16,
        'etfs': [
            ('SPY', 'S&P 500'),
            ('QQQ', 'NASDAQ 100'),
            ('IWM', 'Russell 2000'),
            ('DIA', 'Dow Jones')
        ]
    }
}

def get_active_market():
    """Determine which market(s) are currently open"""
    active = []
    now_utc = datetime.now(ZoneInfo('UTC'))
    
    for region_id, region_data in MARKET_REGIONS.items():
        try:
            tz = ZoneInfo(region_data['tz'])
            local_time = now_utc.astimezone(tz)
            
            # Check if weekday (0=Monday, 4=Friday)
            if local_time.weekday() > 4:
                continue
            
            current_hour = local_time.hour
            if region_data['open_hour'] <= current_hour < region_data['close_hour']:
                active.append(region_id)
        except:
            pass
    
    return active

@st.cache_data(ttl=300)
def fetch_regional_spreads(region_id):
    """Fetch bid-ask spreads for a specific region"""
    region_data = MARKET_REGIONS[region_id]
    results = []
    
    for symbol, name in region_data['etfs']:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            bid = info.get('bid', 0) or 0
            ask = info.get('ask', 0) or 0
            last = info.get('regularMarketPrice', 0) or info.get('previousClose', 0) or 1
            
            if bid > 0 and ask > 0 and last > 0:
                spread_pct = ((ask - bid) / last) * 10000
            else:
                spread_pct = None
            
            results.append({
                'Symbol': symbol,
                'Name': name,
                'Spread (bps)': spread_pct,
                'Region': region_data['name']
            })
        except:
            results.append({
                'Symbol': symbol,
                'Name': name,
                'Spread (bps)': None,
                'Region': region_data['name']
            })
    
    return pd.DataFrame(results)

# Show current market status
active_markets = get_active_market()

if active_markets:
    st.success(f"✅ Markets currently OPEN: {', '.join([MARKET_REGIONS[m]['name'] for m in active_markets])}")
    
    # Display spreads for active markets
    for region_id in active_markets:
        with st.expander(f"{MARKET_REGIONS[region_id]['name']} - Live Spreads", expanded=True):
            region_spreads = fetch_regional_spreads(region_id)
            
            if not region_spreads.empty:
                # Add status column
                def get_spread_status(spread):
                    if spread is None or pd.isna(spread):
                        return "⚪ N/A"
                    elif spread < 2:
                        return "🟢 Tight"
                    elif spread < 10:
                        return "🟡 Normal"
                    else:
                        return "🔴 Wide"
                
                region_spreads['Status'] = region_spreads['Spread (bps)'].apply(get_spread_status)
                
                # Format display
                display_cols = ['Symbol', 'Name', 'Spread (bps)', 'Status']
                display_spreads = region_spreads[display_cols].copy()
                display_spreads['Spread (bps)'] = display_spreads['Spread (bps)'].apply(
                    lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
                )
                
                st.dataframe(display_spreads, use_container_width=True, hide_index=True)
                
                # Chart for valid spreads
                valid = region_spreads[region_spreads['Spread (bps)'].notna()]
                if not valid.empty:
                    colors = ['#00e676' if s < 2 else '#ffeb3b' if s < 10 else '#ff1744' 
                             for s in valid['Spread (bps)']]
                    fig = go.Figure(data=[
                        go.Bar(x=valid['Symbol'], y=valid['Spread (bps)'], marker_color=colors)
                    ])
                    fig.update_layout(
                        template='plotly_dark',
                        height=180,
                        yaxis_title="Spread (bps)",
                        margin=dict(l=0, r=0, t=10, b=0)
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available for this region")
else:
    st.info("⏰ No markets currently open. Market hours:")
    for region_id, region_data in MARKET_REGIONS.items():
        st.caption(f"{region_data['name']}: {region_data['open_hour']}:00 - {region_data['close_hour']}:00 local time (Mon-Fri)")
    
    # Show all regions even when closed
    st.markdown("#### 📊 All Regions (Data from last market close)")
    
    selected_region = st.radio(
        "Select region to view:",
        options=list(MARKET_REGIONS.keys()),
        format_func=lambda x: MARKET_REGIONS[x]['name'],
        horizontal=True
    )
    
    region_spreads = fetch_regional_spreads(selected_region)
    
    if not region_spreads.empty:
        st.caption("⚠️ Note: Data reflects last available quotes and may be stale during closed hours")
        
        def get_spread_status(spread):
            if spread is None or pd.isna(spread):
                return "⚪ N/A"
            elif spread < 2:
                return "🟢 Tight"
            elif spread < 10:
                return "🟡 Normal"
            else:
                return "🔴 Wide"
        
        region_spreads['Status'] = region_spreads['Spread (bps)'].apply(get_spread_status)
        
        display_cols = ['Symbol', 'Name', 'Spread (bps)', 'Status']
        display_spreads = region_spreads[display_cols].copy()
        display_spreads['Spread (bps)'] = display_spreads['Spread (bps)'].apply(
            lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
        )
        
        st.dataframe(display_spreads, use_container_width=True, hide_index=True)
        
        valid = region_spreads[region_spreads['Spread (bps)'].notna()]
        if not valid.empty:
            colors = ['#00e676' if s < 2 else '#ffeb3b' if s < 10 else '#ff1744' 
                     for s in valid['Spread (bps)']]
            fig = go.Figure(data=[
                go.Bar(x=valid['Symbol'], y=valid['Spread (bps)'], marker_color=colors)
            ])
            fig.update_layout(
                template='plotly_dark',
                height=180,
                yaxis_title="Spread (bps)",
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for this region")
