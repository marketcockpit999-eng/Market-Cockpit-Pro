# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 7: Market Voices
ニュース、RSS、インテリジェンススキャナー
"""

import streamlit as st
import datetime
import json
import re
import feedparser
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    GEMINI_MODEL,
    CONTEXT_KEYWORDS,
    RSS_FEEDS,
    search_google_news,
    get_time_diff_str,
    run_gemini_analysis,
)

# Get AI client from session state
gemini_client = st.session_state.get('gemini_client')

# ========== PAGE CONTENT ==========
st.subheader("📰 Market Voices")
st.caption("💡 AI が世界中の一次情報を自動スキャン - 重要度でランク付け")

# === Auto Intelligence Scanner ===
st.markdown("### 🤖 全自動インテリジェンス・スキャナー")
st.caption("主要カテゴリを自動巡回し、AIが重要度を判定して上位のみ表示")

col_btn1, col_btn2 = st.columns([3, 1])

with col_btn2:
    if 'daily_briefing_time' in st.session_state:
        st.caption(f"✅ 最終スキャン: {st.session_state['daily_briefing_time']}")

if st.button("🛰️ 全カテゴリを一斉スキャン (AI重要度判定付)", type="primary"):
    if gemini_client:
        all_findings = []
        with st.status("🌐 インテリジェンス網を走査中...") as status:
            for cat_name, config in CONTEXT_KEYWORDS.items():
                st.write(f"📡 {cat_name} をスキャン中...")
                try:
                    news = search_google_news(config['main_keyword'], num_results=3, mode='primary')
                    if news and "見つかりませんでした" not in news:
                        all_findings.append({
                            "category": cat_name,
                            "keyword": config['main_keyword'],
                            "headlines": news
                        })
                except:
                    pass
            status.update(label="✅ スキャン完了", state="complete")
        
        if all_findings:
            analysis_prompt = f"""あなたは敏腕ヘッジファンドのリサーチ責任者です。
以下のカテゴリ別一次情報から、市場への構造的インパクトが最も大きい情報を特定し、
日本語で戦略的レポートを作成してください。

【スキャンデータ】
{json.dumps(all_findings, indent=2, ensure_ascii=False)}
"""
            with st.spinner("🧠 AIが重要度を分析中..."):
                try:
                    report = run_gemini_analysis(gemini_client, GEMINI_MODEL, analysis_prompt, use_search=False)
                    st.session_state['daily_briefing_cache'] = all_findings
                    st.session_state['daily_briefing_report'] = report
                    st.session_state['daily_briefing_time'] = datetime.datetime.now().strftime('%H:%M')
                except Exception as e:
                    st.error(f"AI分析エラー: {e}")
        else:
            st.warning("⚠️ 有益な情報が見つかりませんでした。")
    else:
        st.error("⚠️ AI設定が不完全です。")

# Display results
if st.session_state.get('daily_briefing_report'):
    st.info(st.session_state['daily_briefing_report'])
    with st.expander("🔍 収集ソース詳細"):
        for f in st.session_state.get('daily_briefing_cache', []):
            st.markdown(f"**{f['category']}**")
            st.markdown(f['headlines'])
            st.divider()

st.markdown("---")

# === Manual Hunter ===
st.markdown("### 🔍 手動インテリジェンス・ハンター")
with st.expander("🔧 詳細検索設定", expanded=False):
    search_query = st.text_input("キーワードを入力", placeholder="例: Treasury buyback, Meta nuclear power")
    gl_choice = st.radio("検索地域", ["US", "JP", "GB", "SG"], horizontal=True)
    
    if st.button("🔍 ハンティング開始") and search_query:
        if gemini_client:
            with st.spinner("🕵️ 情報を収集中..."):
                results = search_google_news(search_query, num_results=5, gl=gl_choice, mode='primary')
                eval_prompt = f"以下の情報を評価し、市場へのインパクトを分析してください:\n\n{results}"
                try:
                    report = run_gemini_analysis(gemini_client, GEMINI_MODEL, eval_prompt, use_search=False)
                    st.markdown("### 💎 AI分析結果")
                    st.success(report)
                    with st.expander("📄 ソース一覧"):
                        st.markdown(results)
                except Exception as e:
                    st.error(f"AIエラー: {e}")

st.markdown("---")

# === News Feeds ===
st.markdown("### 📡 Global News Feeds")

feed_tabs = st.tabs(list(RSS_FEEDS.keys()))
for idx, (name, url) in enumerate(RSS_FEEDS.items()):
    with feed_tabs[idx]:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                time_str = get_time_diff_str(entry.get('published', ''))
                with st.expander(f"⏳ {time_str} - {entry.get('title')}"):
                    st.write(re.sub('<[^<]+?>', '', entry.get('summary', ''))[:500])
                    st.markdown(f"[🔗 Link]({entry.get('link')})")
        except:
            st.caption("取得エラー")
