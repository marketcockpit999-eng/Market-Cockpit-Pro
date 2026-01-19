# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 12: Currency Comparison Lab
通貨比較ラボ - Gold建て・BTC建て・USD建てで通貨を自由に比較
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import t

# ========== HELPER FUNCTION FOR SOURCE UPDATE DATE ==========
def get_source_update_dates(df, columns):
    """Get latest valid dates and release dates for specified columns"""
    dates = {}
    if hasattr(df, 'attrs'):
        last_valid = df.attrs.get('last_valid_dates', {})
        release_dates = df.attrs.get('fred_release_dates', {})
        for col in columns:
            if col in last_valid:
                dates[col] = {
                    'data_date': last_valid.get(col),
                    'release_date': release_dates.get(col)
                }
    return dates

def display_source_update(df, columns, label=""):
    """Display source update info for given columns"""
    dates = get_source_update_dates(df, columns)
    if dates:
        # Find the oldest date among columns
        data_dates = [d['data_date'] for d in dates.values() if d.get('data_date')]
        if data_dates:
            oldest_date = min(data_dates)
            st.caption(f"🔄 {t('source_update')}: {oldest_date}")

# ========== DATA LOADING ==========
df = st.session_state.get('df')
if df is None:
    st.error(t('error_data_not_loaded'))
    st.stop()

# ========== PAGE HEADER ==========
st.subheader(t('currency_lab_title'))
st.caption(t('currency_lab_subtitle'))

# ========== CURRENCY CALCULATION FUNCTIONS ==========
def calculate_gold_denominated(df, currencies):
    """Calculate Gold-denominated currency values"""
    result = {}
    gold = df.get('Gold')
    if gold is None or gold.isna().all():
        return None
    
    fx_map = {
        'USD': lambda: 1 / gold,
        'EUR': lambda: df['EURUSD'] / gold if 'EURUSD' in df.columns else None,
        'JPY': lambda: (1 / df['USDJPY']) / gold if 'USDJPY' in df.columns else None,
        'GBP': lambda: df['GBPUSD'] / gold if 'GBPUSD' in df.columns else None,
        'CNY': lambda: (1 / df['USDCNY']) / gold if 'USDCNY' in df.columns else None,
        'CHF': lambda: (1 / df['USDCHF']) / gold if 'USDCHF' in df.columns else None,
        'AUD': lambda: df['AUDUSD'] / gold if 'AUDUSD' in df.columns else None,
    }
    
    for curr in currencies:
        if curr in fx_map:
            val = fx_map[curr]()
            if val is not None:
                result[f'Gold/{curr}'] = val
    
    return pd.DataFrame(result) if result else None

def calculate_btc_denominated(df, currencies):
    """Calculate BTC-denominated currency values"""
    result = {}
    btc = df.get('BTC')
    if btc is None or btc.isna().all():
        return None
    
    fx_map = {
        'USD': lambda: 1 / btc,
        'EUR': lambda: df['EURUSD'] / btc if 'EURUSD' in df.columns else None,
        'JPY': lambda: (1 / df['USDJPY']) / btc if 'USDJPY' in df.columns else None,
        'GBP': lambda: df['GBPUSD'] / btc if 'GBPUSD' in df.columns else None,
        'CNY': lambda: (1 / df['USDCNY']) / btc if 'USDCNY' in df.columns else None,
        'CHF': lambda: (1 / df['USDCHF']) / btc if 'USDCHF' in df.columns else None,
        'AUD': lambda: df['AUDUSD'] / btc if 'AUDUSD' in df.columns else None,
    }
    
    for curr in currencies:
        if curr in fx_map:
            val = fx_map[curr]()
            if val is not None:
                result[f'BTC/{curr}'] = val
    
    return pd.DataFrame(result) if result else None

def calculate_usd_denominated(df, pairs):
    """Calculate USD-denominated pairs"""
    result = {}
    
    pair_map = {
        'USD/JPY': lambda: df.get('USDJPY'),
        'EUR/USD': lambda: df.get('EURUSD'),
        'USD/CNY': lambda: df.get('USDCNY'),
        'GBP/USD': lambda: df.get('GBPUSD'),
        'USD/CHF': lambda: df.get('USDCHF'),
        'AUD/USD': lambda: df.get('AUDUSD'),
        'BTC/USD': lambda: df.get('BTC'),
        'ETH/USD': lambda: df.get('ETH'),
        'Gold/USD': lambda: df.get('Gold'),
        'Silver/USD': lambda: df.get('Silver'),
    }
    
    for pair in pairs:
        if pair in pair_map:
            val = pair_map[pair]()
            if val is not None and not val.isna().all():
                result[pair] = val
    
    return pd.DataFrame(result) if result else None

def normalize_data(df, base_idx):
    """Normalize data to base_idx = 100"""
    normalized = pd.DataFrame(index=df.index)
    for col in df.columns:
        series = df[col].dropna()
        if len(series) > abs(base_idx):
            base_val = series.iloc[base_idx]
            if base_val != 0 and not pd.isna(base_val):
                normalized[col] = (df[col] / base_val) * 100
    return normalized

def filter_by_period(df, period):
    """Filter dataframe by time period"""
    period_days = {
        '6M': 126,
        '1Y': 252,
        '2Y': 504,
        '5Y': 1260,
        'All': len(df)
    }
    days = period_days.get(period, len(df))
    return df.tail(days)

# ========== SIDEBAR CONTROLS ==========
st.sidebar.markdown(f"### {t('currency_lab_settings')}")

# Period selection
period = st.sidebar.selectbox(
    t('currency_lab_period'),
    ['6M', '1Y', '2Y', '5Y', 'All'],
    index=2,  # Default: 2Y
    key='currency_lab_period'
)

# Normalization option
normalize = st.sidebar.checkbox(t('currency_lab_normalize'), value=True, key='currency_lab_normalize')

st.sidebar.markdown("---")

# ========== GOLD-DENOMINATED SECTION ==========
st.markdown("---")
st.markdown(f"### {t('currency_lab_gold_section')}")
st.caption(t('currency_lab_gold_desc'))

with st.expander(t('currency_lab_gold_meaning_title'), expanded=False):
    st.markdown(t('currency_lab_gold_meaning'))

# Gold currency selection
gold_currencies = st.multiselect(
    t('currency_lab_select_gold'),
    ['USD', 'EUR', 'JPY', 'GBP', 'CNY', 'CHF', 'AUD'],
    default=['USD', 'EUR', 'JPY'],
    key='gold_currencies'
)

if gold_currencies:
    gold_data = calculate_gold_denominated(df, gold_currencies)
    if gold_data is not None and not gold_data.empty:
        gold_filtered = filter_by_period(gold_data, period)
        
        if normalize:
            gold_display = normalize_data(gold_filtered, 0)
        else:
            gold_display = gold_filtered
        
        fig_gold = go.Figure()
        colors = ['#FFD700', '#4169E1', '#DC143C', '#32CD32', '#FF8C00', '#8A2BE2', '#00CED1']
        
        for i, col in enumerate(gold_display.columns):
            fig_gold.add_trace(go.Scatter(
                x=gold_display.index,
                y=gold_display[col],
                name=col,
                line=dict(color=colors[i % len(colors)], width=2)
            ))
        
        fig_gold.update_layout(
            template='plotly_dark',
            height=350,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            xaxis=dict(tickformat='%Y/%m', dtick='M3'),
            yaxis_title='Index (100 = Base)' if normalize else 'Value'
        )
        
        st.plotly_chart(fig_gold, use_container_width=True)
        
        cols = st.columns(len(gold_currencies))
        for i, curr in enumerate(gold_currencies):
            col_name = f'Gold/{curr}'
            if col_name in gold_display.columns:
                current = gold_display[col_name].dropna().iloc[-1]
                base = 100 if normalize else gold_display[col_name].dropna().iloc[0]
                change = current - base
                with cols[i]:
                    st.metric(f"🥇/{curr}", f"{current:.1f}", f"{change:+.1f}")
        
        # Display source update for Gold section
        gold_data_cols = ['Gold', 'EURUSD', 'USDJPY', 'GBPUSD', 'USDCNY', 'USDCHF', 'AUDUSD']
        display_source_update(df, gold_data_cols)
else:
    st.info(t('currency_lab_select_hint'))

# ========== BTC-DENOMINATED SECTION ==========
st.markdown("---")
st.markdown(f"### {t('currency_lab_btc_section')}")
st.caption(t('currency_lab_btc_desc'))

with st.expander(t('currency_lab_btc_meaning_title'), expanded=False):
    st.markdown(t('currency_lab_btc_meaning'))

btc_currencies = st.multiselect(
    t('currency_lab_select_btc'),
    ['USD', 'EUR', 'JPY', 'GBP', 'CNY', 'CHF', 'AUD'],
    default=['USD', 'EUR', 'JPY'],
    key='btc_currencies'
)

if btc_currencies:
    btc_data = calculate_btc_denominated(df, btc_currencies)
    if btc_data is not None and not btc_data.empty:
        btc_filtered = filter_by_period(btc_data, period)
        
        if normalize:
            btc_display = normalize_data(btc_filtered, 0)
        else:
            btc_display = btc_filtered
        
        fig_btc = go.Figure()
        colors = ['#F7931A', '#4169E1', '#DC143C', '#32CD32', '#FF8C00', '#8A2BE2', '#00CED1']
        
        for i, col in enumerate(btc_display.columns):
            fig_btc.add_trace(go.Scatter(
                x=btc_display.index,
                y=btc_display[col],
                name=col,
                line=dict(color=colors[i % len(colors)], width=2)
            ))
        
        fig_btc.update_layout(
            template='plotly_dark',
            height=350,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            xaxis=dict(tickformat='%Y/%m', dtick='M3'),
            yaxis_title='Index (100 = Base)' if normalize else 'Value'
        )
        
        st.plotly_chart(fig_btc, use_container_width=True)
        
        cols = st.columns(len(btc_currencies))
        for i, curr in enumerate(btc_currencies):
            col_name = f'BTC/{curr}'
            if col_name in btc_display.columns:
                current = btc_display[col_name].dropna().iloc[-1]
                base = 100 if normalize else btc_display[col_name].dropna().iloc[0]
                change = current - base
                with cols[i]:
                    st.metric(f"₿/{curr}", f"{current:.1f}", f"{change:+.1f}")
        
        # Display source update for BTC section
        btc_data_cols = ['BTC', 'EURUSD', 'USDJPY', 'GBPUSD', 'USDCNY', 'USDCHF', 'AUDUSD']
        display_source_update(df, btc_data_cols)
else:
    st.info(t('currency_lab_select_hint'))

# ========== USD-DENOMINATED SECTION ==========
st.markdown("---")
st.markdown(f"### {t('currency_lab_usd_section')}")
st.caption(t('currency_lab_usd_desc'))

with st.expander(t('currency_lab_usd_meaning_title'), expanded=False):
    st.markdown(t('currency_lab_usd_meaning'))

usd_pairs = st.multiselect(
    t('currency_lab_select_usd'),
    ['USD/JPY', 'EUR/USD', 'USD/CNY', 'GBP/USD', 'USD/CHF', 'AUD/USD', 'BTC/USD', 'ETH/USD', 'Gold/USD', 'Silver/USD'],
    default=['USD/JPY', 'BTC/USD', 'Gold/USD'],
    key='usd_pairs'
)

if usd_pairs:
    usd_data = calculate_usd_denominated(df, usd_pairs)
    if usd_data is not None and not usd_data.empty:
        usd_filtered = filter_by_period(usd_data, period)
        
        if normalize:
            usd_display = normalize_data(usd_filtered, 0)
        else:
            usd_display = usd_filtered
        
        fig_usd = go.Figure()
        colors = ['#00BFFF', '#FFD700', '#FF6347', '#32CD32', '#9370DB', '#FF8C00', '#F7931A', '#627EEA', '#FFD700', '#C0C0C0']
        
        for i, col in enumerate(usd_display.columns):
            fig_usd.add_trace(go.Scatter(
                x=usd_display.index,
                y=usd_display[col],
                name=col,
                line=dict(color=colors[i % len(colors)], width=2)
            ))
        
        fig_usd.update_layout(
            template='plotly_dark',
            height=350,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            xaxis=dict(tickformat='%Y/%m', dtick='M3'),
            yaxis_title='Index (100 = Base)' if normalize else 'Value'
        )
        
        st.plotly_chart(fig_usd, use_container_width=True)
        
        num_cols = min(len(usd_pairs), 5)
        cols = st.columns(num_cols)
        for i, pair in enumerate(usd_pairs[:num_cols]):
            if pair in usd_display.columns:
                current = usd_display[pair].dropna().iloc[-1]
                base = 100 if normalize else usd_display[pair].dropna().iloc[0]
                change = current - base
                with cols[i]:
                    st.metric(pair, f"{current:.1f}", f"{change:+.1f}")
else:
    st.info(t('currency_lab_select_hint'))

# ========== CROSS COMPARISON SECTION ==========
st.markdown("---")
st.markdown(f"### {t('currency_lab_cross_section')}")
st.caption(t('currency_lab_cross_desc'))

with st.expander(t('currency_lab_cross_meaning_title'), expanded=False):
    st.markdown(t('currency_lab_cross_meaning'))

cross_currency = st.selectbox(
    t('currency_lab_select_cross'),
    ['USD', 'EUR', 'JPY', 'GBP', 'CNY', 'CHF', 'AUD'],
    index=2,
    key='cross_currency'
)

gold_cross = calculate_gold_denominated(df, [cross_currency])
btc_cross = calculate_btc_denominated(df, [cross_currency])

if gold_cross is not None and btc_cross is not None:
    cross_df = pd.DataFrame({
        f'Gold/{cross_currency}': gold_cross[f'Gold/{cross_currency}'],
        f'BTC/{cross_currency}': btc_cross[f'BTC/{cross_currency}']
    })
    
    cross_filtered = filter_by_period(cross_df, period)
    if normalize:
        cross_display = normalize_data(cross_filtered, 0)
    else:
        cross_display = cross_filtered
    
    fig_cross = go.Figure()
    
    fig_cross.add_trace(go.Scatter(
        x=cross_display.index,
        y=cross_display[f'Gold/{cross_currency}'],
        name=f'🥇 Gold/{cross_currency}',
        line=dict(color='#FFD700', width=2)
    ))
    
    fig_cross.add_trace(go.Scatter(
        x=cross_display.index,
        y=cross_display[f'BTC/{cross_currency}'],
        name=f'₿ BTC/{cross_currency}',
        line=dict(color='#F7931A', width=2)
    ))
    
    fig_cross.update_layout(
        template='plotly_dark',
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        xaxis=dict(tickformat='%Y/%m', dtick='M3'),
        yaxis_title='Index (100 = Base)' if normalize else 'Value'
    )
    
    st.plotly_chart(fig_cross, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    
    gold_curr = cross_display[f'Gold/{cross_currency}'].dropna().iloc[-1]
    btc_curr = cross_display[f'BTC/{cross_currency}'].dropna().iloc[-1]
    
    with col1:
        change = gold_curr - 100 if normalize else 0
        st.metric(f"🥇 Gold/{cross_currency}", f"{gold_curr:.1f}", f"{change:+.1f}")
    
    with col2:
        change = btc_curr - 100 if normalize else 0
        st.metric(f"₿ BTC/{cross_currency}", f"{btc_curr:.1f}", f"{change:+.1f}")
    
    with col3:
        if normalize:
            ratio = btc_curr / gold_curr * 100 if gold_curr != 0 else 0
            st.metric(t('currency_lab_btc_vs_gold'), f"{ratio:.1f}", f"{ratio-100:+.1f}%")
        else:
            st.metric(t('currency_lab_btc_vs_gold'), "N/A", help=t('currency_lab_normalize'))
else:
    st.warning(t('currency_lab_insufficient_data'))

# ========== FOOTER ==========
st.markdown("---")
st.caption(t('currency_lab_tip'))
