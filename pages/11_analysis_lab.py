# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import show_metric_with_sparkline, EXPLANATIONS, DATA_FREQUENCY

df = st.session_state.get('df')
if df is None:
    st.error("Data not loaded.")
    st.stop()

st.subheader("Market Analysis Lab")
st.caption("Macro analysis: GLP, M2 Velocity, Financial Stress")

st.markdown("---")
st.markdown("### Global Liquidity Proxy")
if 'Global_Liquidity_Proxy' in df.columns and not df.get('Global_Liquidity_Proxy', pd.Series()).isna().all():
    gl = df['Global_Liquidity_Proxy'].dropna()
    col1, col2 = st.columns([1,2])
    with col1:
        st.metric("GLP", f"${gl.iloc[-1]/1000:.2f}T")
    with col2:
        if 'SP500' in df.columns:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Scatter(x=gl.index, y=gl, name='GLP'), secondary_y=False)
            fig.add_trace(go.Scatter(x=df.index, y=df['SP500'], name='SP500'), secondary_y=True)
            fig.update_layout(template='plotly_dark', height=280)
            st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("GLP Data Unavailable")

st.markdown("---")
st.markdown("### M2 Velocity")
if 'M2_Velocity' in df.columns and not df.get('M2_Velocity', pd.Series()).isna().all():
    m2v = df['M2_Velocity'].dropna()
    st.metric("M2V", f"{m2v.iloc[-1]:.2f}")
    st.line_chart(m2v, height=200)
else:
    st.info("M2V Data Unavailable")

st.markdown("---")
st.markdown("### Financial Stress Index")
if 'Financial_Stress' in df.columns and not df.get('Financial_Stress', pd.Series()).isna().all():
    fs = df['Financial_Stress'].dropna()
    st.metric("FSI", f"{fs.iloc[-1]:.2f}")
    st.line_chart(fs.tail(500), height=200)
else:
    st.info("FSI Data Unavailable")
