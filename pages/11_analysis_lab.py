# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 11: Market Analysis Lab
マクロ分析ラボ
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import show_metric_with_sparkline, EXPLANATIONS, DATA_FREQUENCY

df = st.session_state.get('df')
if df is None:
    st.error("データが読み込まれていません。")
    st.stop()

st.subheader("🔬 Market Analysis Lab")
st.caption("💡 マクロ流動性と金融環境を分析するラボ")

# ========== Global Liquidity Proxy ==========
st.markdown("---")
st.markdown("### 🌊 Global Liquidity Proxy (GLP)")

with st.expander("📖 GLPとは？", expanded=False):
    st.markdown("""
    **Global Liquidity Proxy（グローバル流動性プロキシ）** は、世界の金融市場に流れている「お金の量」を推定する指標です。
    
    **計算式**: `FRB資産 + ECB資産(ドル換算) - TGA - RRP`
    
    | 要素 | 説明 |
    |------|------|
    | **FRB資産** | アメリカ中央銀行のバランスシート（QEで増加） |
    | **ECB資産** | 欧州中央銀行のバランスシート（ユーロ→ドル換算） |
    | **TGA** | 米財務省の預金口座（多い = 市場から吸収） |
    | **RRP** | 翌日物リバースレポ（多い = 市場から吸収） |
    
    **見方**:
    - 📈 **GLP上昇** = 市場に流動性が増加 → 株・BTCに追い風
    - 📉 **GLP下降** = 流動性引き締め → リスク資産に逆風
    
    **チャートの読み方**: S&P500とGLPは高い相関があります。GLPが先行して動くことが多いため、「流動性の変化→株価の変化」として活用できます。
    """)

if 'Global_Liquidity_Proxy' in df.columns and not df.get('Global_Liquidity_Proxy', pd.Series()).isna().all():
    gl = df['Global_Liquidity_Proxy'].dropna()
    col1, col2 = st.columns([1,2])
    with col1:
        st.metric("GLP", f"${gl.iloc[-1]/1000:.2f}T", help="Fed + ECB - TGA - RRP")
    with col2:
        if 'SP500' in df.columns:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Scatter(x=gl.index, y=gl, name='GLP', line=dict(color='cyan')), secondary_y=False)
            fig.add_trace(go.Scatter(x=df.index, y=df['SP500'], name='S&P500', line=dict(color='orange', dash='dot')), secondary_y=True)
            fig.update_layout(template='plotly_dark', height=280, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("GLP データなし")

# ========== M2 Velocity ==========
st.markdown("---")
st.markdown("### 🔄 M2 Velocity（通貨回転率）")

with st.expander("📖 M2 Velocityとは？", expanded=False):
    st.markdown("""
    **M2 Velocity（M2通貨回転率）** は、お金が経済の中でどれだけ「回っている」かを示す指標です。
    
    **計算式**: `名目GDP ÷ M2マネーサプライ`
    
    **イメージ**:
    - 💰 お金が1枚あって、1年間に10回使われたら → Velocity = 10
    - 💰 同じお金が5回しか使われなかったら → Velocity = 5
    
    **見方**:
    - 📉 **低下** = お金が滞留している（貯蓄増加、消費控え）→ デフレ圧力
    - 📈 **上昇** = お金が活発に回っている（消費活発化）→ インフレ圧力
    
    **現在の状況**: コロナ後、M2 Velocityは歴史的低水準にあります。中央銀行が大量のお金を刷っても、経済に回っていないことを示しています。
    
    **注意**: 四半期データのため、急激な変化は見られません。長期トレンドの把握に使います。
    """)

if 'M2_Velocity' in df.columns and not df.get('M2_Velocity', pd.Series()).isna().all():
    m2v = df['M2_Velocity'].dropna()
    m2v_val = m2v.iloc[-1]
    
    # Status label
    if m2v_val < 1.2:
        status = "🔵 歴史的低水準（マネー滞留）"
    elif m2v_val < 1.5:
        status = "🟡 低水準"
    else:
        status = "🟢 正常範囲"
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("M2V", f"{m2v_val:.2f}", help="GDP ÷ M2")
        st.caption(status)
    with col2:
        st.line_chart(m2v, height=200)
else:
    st.info("M2V データなし")

# ========== Financial Stress Index ==========
st.markdown("---")
st.markdown("### 🌡️ Financial Stress Index（金融ストレス指数）")

with st.expander("📖 FSIとは？", expanded=False):
    st.markdown("""
    **Financial Stress Index（金融ストレス指数）** は、セントルイス連銀が発表する金融市場の「緊張度」を測る指標です。
    
    **構成要素**: 金利スプレッド、株式ボラティリティ、債券市場の動き など18のデータから算出
    
    **基準**:
    | 値 | 状態 | 意味 |
    |----|------|------|
    | **< -0.5** | 🟢 緩和 | リスクオン環境、投資に有利 |
    | **-0.5 〜 0.5** | 🟡 正常 | 通常の市場環境 |
    | **0.5 〜 1.5** | 🟠 警戒 | ストレス上昇中、注意 |
    | **> 1.5** | 🔴 危機 | 金融危機レベル（2008年、2020年3月など） |
    
    **見方**:
    - **マイナス** = 市場は楽観的、リスク資産に有利
    - **プラス上昇** = 何かがおかしい、リスク回避の兆候
    
    **使い方**: FSIが急上昇したら、ポジションの縮小や現金比率の引き上げを検討するサインです。
    """)

if 'Financial_Stress' in df.columns and not df.get('Financial_Stress', pd.Series()).isna().all():
    fs = df['Financial_Stress'].dropna()
    fs_val = fs.iloc[-1]
    
    # Status label
    if fs_val < -0.5:
        status = "🟢 緩和（リスクオン環境）"
    elif fs_val < 0.5:
        status = "🟡 正常"
    elif fs_val < 1.5:
        status = "🟠 警戒"
    else:
        status = "🔴 危機レベル"
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("FSI", f"{fs_val:.2f}", help="St. Louis Fed Financial Stress Index")
        st.caption(status)
    with col2:
        st.line_chart(fs.tail(500), height=200)
else:
    st.info("FSI データなし")
