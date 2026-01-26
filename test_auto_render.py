# -*- coding: utf-8 -*-
"""
Auto Render Test Page
================================================================================
自動レンダリングシステムのテストページ

Usage:
    streamlit run test_auto_render.py
================================================================================
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    get_market_data,
    render_indicator,
    render_indicators_for_page,
    render_in_columns,
    render_section,
    get_render_stats,
    show_render_debug,
    get_indicators_for_page,
    t,
)

st.set_page_config(page_title="Auto Render Test", layout="wide")

st.title("🧪 Auto Render System Test")

# Load data
@st.cache_data(ttl=600)
def load_data():
    return get_market_data()

with st.spinner("Loading data..."):
    df = load_data()
    st.session_state['df'] = df
    st.session_state['df_original'] = df.copy()

if df is None or df.empty:
    st.error("Failed to load data")
    st.stop()

st.success(f"Data loaded: {len(df)} rows, {len(df.columns)} columns")

# Show render stats
st.header("📊 Render Statistics")
show_render_debug()

# Test individual indicator render
st.header("🔬 Individual Indicator Test")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Standard Pattern: ON_RRP")
    render_indicator(df, 'ON_RRP')

with col2:
    st.subheader("Standard Pattern: VIX")
    render_indicator(df, 'VIX')

st.markdown("---")

# Test mom_yoy pattern
st.header("📈 MoM/YoY Pattern Test")

col1, col2 = st.columns(2)

with col1:
    st.subheader("MoM/YoY Pattern: CPI")
    render_indicator(df, 'CPI')

with col2:
    st.subheader("MoM/YoY Pattern: RetailSales")
    render_indicator(df, 'RetailSales')

st.markdown("---")

# Test render_in_columns
st.header("📐 Column Layout Test")

st.subheader("3 indicators in 3 columns")
render_in_columns(df, ['EFFR', 'IORB', 'SOFR'], num_cols=3, show_charts=False)

st.markdown("---")

# Test render_section
st.header("📦 Section Test")
render_section(df, "Fed Liquidity Core", ['ON_RRP', 'Reserves', 'TGA'], num_cols=3)

st.markdown("---")

# Show page indicators
st.header("📄 Page Indicators")

page = st.selectbox("Select page", [
    '01_liquidity',
    '02_global_money', 
    '03_us_economic',
    '04_crypto',
    '09_banking',
    '10_market_lab',
])

indicators = get_indicators_for_page(page)
st.write(f"**{page}**: {len(indicators)} indicators")

with st.expander("Show indicator list"):
    for key, config in indicators.items():
        pattern = config.get('display_pattern', 'standard')
        source = config.get('source', '?')
        st.write(f"- `{key}` ({source}, {pattern})")

if st.button(f"Render all indicators for {page}"):
    results = render_indicators_for_page(df, page)
    st.success(f"Rendered {sum(results.values())}/{len(results)} indicators successfully")
