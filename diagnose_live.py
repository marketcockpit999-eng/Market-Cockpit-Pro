# -*- coding: utf-8 -*-
"""
診断スクリプト v2: 実際のデータ取得状況を確認
実行方法: cd market_monitor && streamlit run diagnose_live.py

このスクリプトは実際にデータを取得し、どの指標がmissingかを表示します。
"""

import streamlit as st
import sys
import os

# Page config
st.set_page_config(page_title="Missing Indicators診断", page_icon="🔍", layout="wide")

# Import utils
from utils.indicators import INDICATORS, get_freshness_rules, DATA_FRESHNESS_RULES
from utils.data_fetcher import get_market_data
from utils.data_processor import get_data_freshness_status

st.title("🔍 Missing Indicators 診断ツール")

# Display indicator definitions
st.subheader("【1】INDICATORS定義")
st.write(f"定義数: **{len(INDICATORS)}件**")

sources = {}
for k, v in INDICATORS.items():
    src = v.get('source', 'UNKNOWN')
    if src not in sources:
        sources[src] = []
    sources[src].append(k)

for src, items in sources.items():
    st.write(f"- {src}: {len(items)}件")

# DATA_FRESHNESS_RULES
st.subheader("【2】DATA_FRESHNESS_RULES")
rules = get_freshness_rules()
total_in_rules = sum(len(r['indicators']) for r in rules.values())
st.write(f"ルール登録数: **{total_in_rules}件**")

# Load actual data
st.subheader("【3】実データ取得状況")

if st.button("🔄 データを取得して診断", type="primary"):
    with st.spinner("データ取得中..."):
        df, df_original = get_market_data(_force_refresh=True)
        
        st.success(f"DataFrame列数: {len(df.columns)}")
        
        # Get freshness status
        last_valid_dates = df.attrs.get('last_valid_dates', {})
        freshness = get_data_freshness_status(last_valid_dates)
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🟢 Fresh", freshness['summary']['fresh_count'])
        col2.metric("🟡 Stale", freshness['summary']['stale_count'])
        col3.metric("🔴 Critical", freshness['summary']['critical_count'])
        col4.metric("⚪ Missing", freshness['summary']['missing_count'])
        
        # Show missing indicators
        if freshness['missing']:
            st.subheader("【4】Missing Indicators (データ取得失敗)")
            st.error(f"以下の {len(freshness['missing'])}件がmissing:")
            for ind in freshness['missing']:
                info = INDICATORS.get(ind, {})
                st.write(f"- **{ind}**: source={info.get('source')}, id={info.get('id')}")
        else:
            st.success("Missing Indicatorなし！全て取得成功")
        
        # Compare INDICATORS vs DataFrame columns
        st.subheader("【5】INDICATORS vs DataFrame比較")
        
        indicator_names = set(INDICATORS.keys())
        df_columns = set(df.columns)
        
        # In INDICATORS but not in DataFrame
        missing_in_df = indicator_names - df_columns
        if missing_in_df:
            st.warning(f"INDICATORSにあるがDataFrameにない: {len(missing_in_df)}件")
            for ind in sorted(missing_in_df):
                info = INDICATORS.get(ind, {})
                st.write(f"- {ind}: source={info.get('source')}, id={info.get('id')}")
        else:
            st.success("全INDICATORSがDataFrameに存在")
        
        # Extra columns in DataFrame (calculated, etc)
        extra_in_df = df_columns - indicator_names
        if extra_in_df:
            st.info(f"DataFrameにあるがINDICATORSにない（計算列等）: {len(extra_in_df)}件")
            st.write(", ".join(sorted(extra_in_df)))
        
        # Show all columns with last valid dates
        st.subheader("【6】全列の最終有効日")
        with st.expander("詳細を表示"):
            for col in sorted(df.columns):
                date = last_valid_dates.get(col, 'N/A')
                status = freshness['details'].get(col, {}).get('status', 'unknown')
                st.write(f"- {col}: {date} ({status})")
