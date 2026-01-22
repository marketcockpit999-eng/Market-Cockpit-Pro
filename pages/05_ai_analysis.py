# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 5: AI Analysis
Gemini/Claudeによる市場分析
"""

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    t,
    get_current_language,
    GEMINI_MODEL,
    run_gemini_analysis,
    generate_category_report,
    REPORT_CATEGORIES,
    get_indicators_for_ai,
    get_data_freshness_status,
)

# Get AI client and data from session state
gemini_client = st.session_state.get('gemini_client')
df = st.session_state.get('df')

if df is None:
    st.error(t('error_data_not_loaded'))
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader(t('ai_analysis_title'))
st.caption(t('ai_analysis_desc'))

# Show Data Count Status
ai_indicators = get_indicators_for_ai()
defined_count = len(ai_indicators)  # Total defined in INDICATORS with ai_include=True

# Get actual data status
total_freshness = get_data_freshness_status(df.attrs.get('last_valid_dates', {})) if hasattr(df, 'attrs') else {'summary': {'total': 0, 'fresh_count': 0, 'stale_count': 0, 'critical_count': 0, 'missing_count': 0}}
# Available = Total - Missing (Fresh + Stale + Critical = データが存在するものすべて)
available_count = total_freshness['summary']['total'] - total_freshness['summary'].get('missing_count', 0)
missing_count = total_freshness['summary'].get('missing_count', 0)

col_info1, col_info2, col_info3 = st.columns([1, 1, 2])
with col_info1:
    st.metric("👁️", t('ai_data_count', ai_count=available_count, total_count=defined_count))
with col_info2:
    if missing_count > 0:
        st.warning(t('ai_data_excluded', count=missing_count))
    else:
        st.success(t('ai_all_monitored'))

# ========== CATEGORY REPORTS SECTION ==========
st.divider()
st.subheader(t('ai_category_reports'))
st.caption(t('ai_category_reports_desc'))

# Get current language for category names
current_lang = get_current_language()

# Create category buttons in a grid
st.markdown(f"**{t('ai_select_category')}**")

# 3 columns x 2 rows for 6 categories
col1, col2, col3 = st.columns(3)

category_keys = list(REPORT_CATEGORIES.keys())

with col1:
    if st.button(REPORT_CATEGORIES['fed_policy']['name_ja' if current_lang == 'ja' else 'name_en'], key='cat_fed', use_container_width=True):
        st.session_state['selected_category'] = 'fed_policy'
    if st.button(REPORT_CATEGORIES['employment']['name_ja' if current_lang == 'ja' else 'name_en'], key='cat_emp', use_container_width=True):
        st.session_state['selected_category'] = 'employment'

with col2:
    if st.button(REPORT_CATEGORIES['liquidity']['name_ja' if current_lang == 'ja' else 'name_en'], key='cat_liq', use_container_width=True):
        st.session_state['selected_category'] = 'liquidity'
    if st.button(REPORT_CATEGORIES['banking']['name_ja' if current_lang == 'ja' else 'name_en'], key='cat_bank', use_container_width=True):
        st.session_state['selected_category'] = 'banking'

with col3:
    if st.button(REPORT_CATEGORIES['inflation_rates']['name_ja' if current_lang == 'ja' else 'name_en'], key='cat_inf', use_container_width=True):
        st.session_state['selected_category'] = 'inflation_rates'
    if st.button(REPORT_CATEGORIES['crypto']['name_ja' if current_lang == 'ja' else 'name_en'], key='cat_crypto', use_container_width=True):
        st.session_state['selected_category'] = 'crypto'

# Generate report if category selected
if 'selected_category' in st.session_state and st.session_state['selected_category']:
    selected_cat = st.session_state['selected_category']
    cat_name = REPORT_CATEGORIES[selected_cat]['name_ja' if current_lang == 'ja' else 'name_en']
    
    with st.spinner(t('ai_generating_report', category=cat_name)):
        try:
            report = generate_category_report(
                gemini_client,
                GEMINI_MODEL,
                selected_cat,
                df,
                lang=current_lang
            )
            st.markdown(f"### {t('ai_report_generated', category=cat_name)}")
            st.info(t('ai_web_search_note'))
            st.markdown(report)
        except Exception as e:
            st.error(f"Report generation error: {e}")
    
    # Clear selection after displaying
    st.session_state['selected_category'] = None
