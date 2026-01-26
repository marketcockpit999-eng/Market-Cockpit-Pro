# -*- coding: utf-8 -*-
"""
Auto Render Test Page v2
================================================================================
完全自動レンダリングシステムのテストページ

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
    render_page,
    render_indicator,
    render_in_columns,
    render_section,
    get_render_stats,
    show_render_debug,
    get_page_layout,
    get_all_page_names,
    validate_layout_indicators,
    t,
)

st.set_page_config(page_title="Auto Render Test v2", layout="wide")

st.title("🧪 Auto Render System Test v2")
st.caption("完全自動レンダリングシステム - 消えない構造")

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

# Validate layouts
st.header("✅ Layout Validation")
errors = validate_layout_indicators()
if errors:
    st.error(f"Found {len(errors)} errors:")
    for e in errors:
        st.write(f"  - {e}")
else:
    st.success("All layout indicators valid!")

# Page selector
st.header("📄 Page Render Test")

available_pages = get_all_page_names()
selected_page = st.selectbox("Select page to render", available_pages)

# Show layout info
layout = get_page_layout(selected_page)
if layout:
    sections = layout.get('sections', [])
    total_indicators = sum(len(s.get('indicators', [])) for s in sections)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Sections", len(sections))
    col2.metric("Indicators", total_indicators)
    col3.metric("Page Title", t(layout.get('title_key', selected_page)))
    
    with st.expander("Section Details"):
        for section in sections:
            st.write(f"**{section['id']}** ({section.get('type', 'standard')})")
            st.write(f"  Indicators: {section.get('indicators', [])}")

st.markdown("---")

# Render the page
if st.button(f"🚀 Render {selected_page}", type="primary"):
    st.markdown("---")
    with st.spinner(f"Rendering {selected_page}..."):
        stats = render_page(df, selected_page, show_debug=True)
    
    st.markdown("---")
    st.success(f"Rendered {stats['sections_rendered']} sections, {stats['indicators_rendered']} indicators")
    
    if stats.get('errors'):
        st.warning(f"Errors: {stats['errors']}")

# Individual indicator test
st.markdown("---")
st.header("🔬 Individual Indicator Test")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Standard: ON_RRP")
    render_indicator(df, 'ON_RRP')

with col2:
    st.subheader("Standard: VIX")
    render_indicator(df, 'VIX')

# Debug stats
st.markdown("---")
show_render_debug()
