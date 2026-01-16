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
    GEMINI_MODEL, CLAUDE_MODEL,
    get_market_summary,
    run_gemini_analysis, run_claude_analysis,
    search_google_news,
)

# Get AI clients and data from session state
gemini_client = st.session_state.get('gemini_client')
claude_client = st.session_state.get('claude_client')
df = st.session_state.get('df')

if df is None:
    st.error("データが読み込まれていません。main.pyから起動してください。")
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader("🤖 AI Market Analysis")
st.caption("💡 膨大な市場データから相関性と構造を抽出")

# Fetch market summary
with st.spinner("📊 市場データを集約中..."):
    market_summary = get_market_summary(df)

# Sidebar settings
with st.sidebar:
    st.divider()
    st.header("⚙️ Analysis Settings")
    selected_ai = st.multiselect("使用する AI", ["Gemini 3 Flash", "Claude 4.5 Opus"], default=["Gemini 3 Flash"])
    
    st.subheader("🎯 Focus Areas")
    focus_selection = st.multiselect(
        "AIに特に注目させる項目",
        ["流動性 (Plumbing)", "インフレ・金利", "雇用・景気後退", "銀行・信用危機", "地政学・コモディティ", "仮想通貨"],
        default=st.session_state.get('ai_focus_categories', ["流動性 (Plumbing)"])
    )
    st.session_state['ai_focus_categories'] = focus_selection

policy_context = """
あなたは伝説的なグローバル・マクロ・ストラテジストです。
単なるニュースの要約ではなく、データの背後にある「配管（Plumbing）」、つまり流動性の動きと市場参加者のインセンティブを分析します。
"""

col_main, col_custom = st.columns([2, 1])

with col_main:
    if st.button("🚀 最新市場データを全分析"):
        if "Gemini" in str(selected_ai):
            with st.spinner("🔷 Gemini 3 Flash が分析中..."):
                try:
                    prompt = f"{policy_context}\n\n以下の市場データを構造的に分析してください:\n{market_summary}"
                    result = run_gemini_analysis(gemini_client, GEMINI_MODEL, prompt)
                    st.markdown("### 🔷 Gemini Analysis")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Gemini Error: {e}")
        
        if "Claude" in str(selected_ai):
            with st.spinner("🟣 Claude 4.5 Opus が分析中..."):
                try:
                    prompt = f"{policy_context}\n\n以下の市場データを構造的に分析してください:\n{market_summary}"
                    result = run_claude_analysis(claude_client, CLAUDE_MODEL, prompt)
                    st.markdown("### 🟣 Claude Analysis")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Claude Error: {e}")

with col_custom:
    st.markdown("### 💬 カスタム質問")
    user_question = st.text_area(
        "市場データについて質問してください",
        placeholder="例: 現在のNet Liquidityの水準は歴史的にどうですか？",
        height=100
    )
    
    if st.button("📨 質問を送信") and user_question:
        news_context = ""
        if any(kw in user_question for kw in ["ニュース", "最新", "直近", "今日", "今週", "出来事"]):
            with st.spinner("🔍 関連するニュースを検索中..."):
                news_headlines = search_google_news(user_question, num_results=3)
                news_context = f"\n\n【最新ニュース検索結果】\n{news_headlines}"

        custom_prompt = f"{policy_context}\n\n市場データ:\n{market_summary}\n{news_context}\n\n質問: {user_question}"
        
        if "Gemini" in str(selected_ai):
            with st.spinner("🔷 Gemini 3 Flash が回答中..."):
                try:
                    result = run_gemini_analysis(gemini_client, GEMINI_MODEL, custom_prompt)
                    st.markdown("### 💡 Gemini 回答")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Gemini Error: {e}")
        elif "Claude" in str(selected_ai):
            with st.spinner("🟣 Claude Opus 4.5 が回答中..."):
                try:
                    result = run_claude_analysis(claude_client, CLAUDE_MODEL, custom_prompt)
                    st.markdown("### 💡 Claude 回答")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Claude Error: {e}")
