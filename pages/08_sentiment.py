# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 8: Market Sentiment
市場心理指標（Fear & Greed、VIX、AAII、Put/Call）
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    show_metric_with_sparkline, 
    get_crypto_fear_greed, 
    get_cnn_fear_greed,
    get_aaii_sentiment, 
    get_put_call_ratio,
    EXPLANATIONS,
    DATA_FREQUENCY,
)

# Get data from session state
df = st.session_state.get('df')

if df is None:
    st.error("データが読み込まれていません。main.pyから起動してください。")
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader("🎭 Market Sentiment")
st.caption("💡 市場心理を一目で把握 - Fear & Greed、Put/Call Ratio、投資家心理調査")

# Fetch sentiment data
crypto_fg = get_crypto_fear_greed()
cnn_fg = get_cnn_fear_greed()
aaii = get_aaii_sentiment()
vix_value = df.get('VIX').iloc[-1] if df.get('VIX') is not None else None

# === ROW 1: Fear & Greed Gauges ===
st.markdown("### 🎯 Fear & Greed Index")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📈 CNN Fear & Greed (株式)")
    if cnn_fg and cnn_fg.get('current'):
        fg_value = cnn_fg['current']
        
        if fg_value <= 25:
            color, label = "🔴", "Extreme Fear"
        elif fg_value <= 45:
            color, label = "🟠", "Fear"
        elif fg_value <= 55:
            color, label = "🟡", "Neutral"
        elif fg_value <= 75:
            color, label = "🟢", "Greed"
        else:
            color, label = "🟣", "Extreme Greed"
        
        st.metric(f"{color} {label}", f"{fg_value}")
        st.progress(fg_value / 100)
        
        if cnn_fg.get('history') is not None and len(cnn_fg['history']) > 0:
            st.caption("📊 30日間の推移")
            st.line_chart(cnn_fg['history']['value'], height=120)
    else:
        st.info("📊 CNN Fear & Greed は現在取得できません（API制限）")

with col2:
    st.markdown("#### ₿ Crypto Fear & Greed")
    if crypto_fg:
        cfg_value = crypto_fg['current']
        cfg_class = crypto_fg.get('classification', '')
        
        if cfg_value <= 25:
            color = "🔴"
        elif cfg_value <= 45:
            color = "🟠"
        elif cfg_value <= 55:
            color = "🟡"
        elif cfg_value <= 75:
            color = "🟢"
        else:
            color = "🟣"
        
        st.metric(f"{color} {cfg_class}", f"{cfg_value}")
        st.progress(cfg_value / 100)
        
        if crypto_fg.get('history') is not None and len(crypto_fg['history']) > 0:
            latest_date = crypto_fg['history'].index[-1]
            st.caption(f"🔄 提供元更新日: {latest_date.strftime('%Y-%m-%d %H:%M')}")
            st.caption("📊 30日間の推移")
            st.line_chart(crypto_fg['history']['value'], height=120)
    else:
        st.warning("⚠️ Crypto Fear & Greed 取得エラー")

with col3:
    st.markdown("#### 📊 VIX (恐怖指数)")
    if vix_value is not None:
        if vix_value < 15:
            vix_label = "🟢 Low Volatility"
        elif vix_value < 20:
            vix_label = "🟡 Normal"
        elif vix_value < 30:
            vix_label = "🟠 Elevated"
        else:
            vix_label = "🔴 High Fear"
        
        st.metric(vix_label, f"{vix_value:.1f}")
        
        vix_series = df.get('VIX')
        if vix_series is not None and not vix_series.isna().all():
            latest_vix_date = vix_series.dropna().index[-1]
            st.caption(f"🔄 提供元更新日: {latest_vix_date.strftime('%Y-%m-%d')}")
            st.caption("📊 60日間の推移")
            st.line_chart(vix_series.tail(60), height=120)
    else:
        st.warning("⚠️ VIXデータなし")

st.markdown("---")

# === ROW 2: AAII Investor Sentiment ===
st.markdown("### 👥 AAII Investor Sentiment Survey")
st.caption("個人投資家の心理調査（週次更新）- 逆張り指標として有名")

if aaii:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🐂 Bullish (強気)", f"{aaii['bullish']:.1f}%")
    with col2:
        st.metric("😐 Neutral (中立)", f"{aaii['neutral']:.1f}%")
    with col3:
        st.metric("🐻 Bearish (弱気)", f"{aaii['bearish']:.1f}%")
    with col4:
        spread = aaii['bull_bear_spread']
        if spread >= 20:
            spread_emoji, spread_hint = "🔴", "(過熱注意)"
        elif spread >= 10:
            spread_emoji, spread_hint = "🟠", "(やや強気)"
        elif spread >= -10:
            spread_emoji, spread_hint = "🟢", "(中立)"
        elif spread >= -20:
            spread_emoji, spread_hint = "🟠", "(やや弱気)"
        else:
            spread_emoji, spread_hint = "🔴", "(底打ちサイン?)"
        st.metric(f"{spread_emoji} Bull-Bear Spread", f"{spread:+.1f}%")
        st.caption(spread_hint)
    
    if aaii.get('date'):
        st.caption(f"🔄 提供元更新日: {aaii['date']} (週次)")
    
    st.markdown("**センチメント分布:**")
    bar_data = pd.DataFrame({
        'カテゴリ': ['Bullish', 'Neutral', 'Bearish'],
        '割合': [aaii['bullish'], aaii['neutral'], aaii['bearish']]
    })
    st.bar_chart(bar_data.set_index('カテゴリ'), height=150)
    
    with st.expander("📈 Bull-Bear Spread の読み方"):
        st.markdown("""
        **Bull-Bear Spread** = Bullish(強気)% − Bearish(弱気)%
        
        | 数値 | 意味 | 解釈 |
        |-----|------|------|
        | **+20%以上** | 強気優勢 | 🔴 過熱注意（天井サイン？） |
        | **+10%〜+20%** | やや強気 | 🟠 楽観的 |
        | **−10%〜+10%** | 中立 | 🟢 バランス良し |
        | **−10%〜−20%** | やや弱気 | 🟠 悲観的 |
        | **−20%以下** | 弱気優勢 | 🔴 底打ちサイン？ |
        
        💡 **逆張り戦略**: みんなが強気の時は天井、弱気の時は底になりやすい！
        """)
    
    if aaii.get('note'):
        st.caption(f"📝 {aaii['note']}")
else:
    st.warning("⚠️ AAIIデータ取得エラー")

st.markdown("---")

# === ROW 3: Put/Call Ratio ===
st.markdown("### 📊 Put/Call Ratio")
st.caption("オプション市場の弱気/強気度 - 高い = 弱気、低い = 強気")

pc_ratio = get_put_call_ratio()
if pc_ratio:
    st.metric("Equity P/C Ratio", f"{pc_ratio:.2f}")
else:
    st.info("📝 Put/Call Ratioのデータソースを準備中です。VIXで代替表示しています。")
    if vix_value is not None:
        st.caption(f"VIX (参考): {vix_value:.1f}")

st.markdown("---")

# === Interpretation Guide ===
st.markdown("### 📚 センチメント指標の読み方")
with st.expander("💡 指標の解釈ガイド"):
    st.markdown("""
    | 指標 | 極端な恐怖 | 恐怖 | 中立 | 強欲 | 極端な強欲 |
    |------|-----------|------|------|------|-----------|
    | **Fear & Greed** | 0-25 | 25-45 | 45-55 | 55-75 | 75-100 |
    | **VIX** | >30 | 20-30 | 15-20 | 10-15 | <10 |
    | **Put/Call** | >1.2 | 0.9-1.2 | 0.7-0.9 | 0.5-0.7 | <0.5 |
    
    **逆張り戦略のヒント:**
    - 「Extreme Fear」は買いのチャンスかも
    - 「Extreme Greed」は利確のサインかも
    - AAIIで強気が極端に多い時は注意
    """)
