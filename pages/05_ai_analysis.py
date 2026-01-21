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
    GEMINI_MODEL, CLAUDE_MODEL,
    get_market_summary,
    run_gemini_analysis, run_claude_analysis,
    search_google_news,
    get_indicators_for_ai,
    get_data_freshness_status,
)

# Get AI clients and data from session state
gemini_client = st.session_state.get('gemini_client')
claude_client = st.session_state.get('claude_client')
df = st.session_state.get('df')

if df is None:
    st.error(t('error_data_not_loaded'))
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader(t('ai_analysis_title'))
st.caption(t('ai_analysis_desc'))

# Show Data Count Status
ai_indicators = get_indicators_for_ai()
ai_count = len(ai_indicators)
total_freshness = get_data_freshness_status(df.attrs.get('last_valid_dates', {})) if hasattr(df, 'attrs') else {'summary': {'total': 0}}
total_count = total_freshness['summary']['total']

col_info1, col_info2, col_info3 = st.columns([1, 1, 2])
with col_info1:
    st.metric("👁️", t('ai_data_count', ai_count=ai_count, total_count=total_count))
with col_info2:
    if ai_count < total_count:
        st.warning(t('ai_data_excluded', count=total_count - ai_count))
    else:
        st.success(t('ai_all_monitored'))

# Fetch market summary
with st.spinner(t('ai_collecting_data')):
    market_summary = get_market_summary(df)

# Sidebar settings
with st.sidebar:
    st.divider()
    st.header(t('ai_settings'))
    selected_ai = st.multiselect(t('ai_select'), ["Gemini 3 Flash", "Claude 4.5 Opus"], default=["Gemini 3 Flash"])
    
    st.subheader(t('ai_focus_areas'))
    focus_options = [
        t('ai_focus_liquidity'),
        t('ai_focus_inflation'),
        t('ai_focus_employment'),
        t('ai_focus_banking'),
        t('ai_focus_geopolitics'),
        t('ai_focus_crypto')
    ]
    # Fix: Validate stored defaults against current language options
    stored_focus = st.session_state.get('ai_focus_categories', [])
    valid_defaults = [opt for opt in stored_focus if opt in focus_options]
    if not valid_defaults:
        valid_defaults = [focus_options[0]]
    
    focus_selection = st.multiselect(
        t('ai_focus_prompt'),
        focus_options,
        default=valid_defaults
    )
    st.session_state['ai_focus_categories'] = focus_selection

# Get localized policy context and language instruction
policy_context = t('ai_policy_context')
analysis_instruction = t('ai_analysis_instruction')
response_language = t('ai_response_language')

col_main, col_custom = st.columns([2, 1])

with col_main:
    if st.button(t('ai_full_analysis')):
        if "Gemini" in str(selected_ai):
            with st.spinner(t('ai_gemini_analyzing')):
                try:
                    prompt = f"{policy_context}\n\n{response_language}\n\n{analysis_instruction}\n{market_summary}"
                    result = run_gemini_analysis(gemini_client, GEMINI_MODEL, prompt)
                    st.markdown("### 🔷 Gemini Analysis")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Gemini Error: {e}")
        
        if "Claude" in str(selected_ai):
            with st.spinner(t('ai_claude_analyzing')):
                try:
                    prompt = f"{policy_context}\n\n{response_language}\n\n{analysis_instruction}\n{market_summary}"
                    result = run_claude_analysis(claude_client, CLAUDE_MODEL, prompt)
                    st.markdown("### 🟣 Claude Analysis")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Claude Error: {e}")

with col_custom:
    st.markdown(f"### {t('ai_custom_analysis')}")
    user_question = st.text_area(
        t('ai_custom_prompt'),
        placeholder=t('ai_custom_placeholder'),
        height=100
    )
    
    if st.button(t('ai_run_custom')) and user_question:
        news_context = ""
        if any(kw in user_question for kw in ["ニュース", "最新", "直近", "今日", "今週", "出来事", "news", "latest", "recent"]):
            with st.spinner("🔍 Searching news..."):
                news_headlines = search_google_news(user_question, num_results=3)
                news_context = f"\n\n【Latest News】\n{news_headlines}"

        custom_prompt = f"{policy_context}\n\n{response_language}\n\nMarket Data:\n{market_summary}\n{news_context}\n\nQuestion: {user_question}"
        
        if "Gemini" in str(selected_ai):
            with st.spinner(t('ai_gemini_analyzing')):
                try:
                    result = run_gemini_analysis(gemini_client, GEMINI_MODEL, custom_prompt)
                    st.markdown("### 💡 Gemini Response")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Gemini Error: {e}")
        elif "Claude" in str(selected_ai):
            with st.spinner(t('ai_claude_analyzing')):
                try:
                    result = run_claude_analysis(claude_client, CLAUDE_MODEL, custom_prompt)
                    st.markdown("### 💡 Claude Response")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Claude Error: {e}")
