# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 9: Banking Sector
銀行セクター（H.8週次データ、SLOOS四半期調査）
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import uuid
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    show_metric_with_sparkline,
    EXPLANATIONS,
    DATA_FREQUENCY,
)

# Get data from session state
df = st.session_state.get('df')
df_original = st.session_state.get('df_original')

if df is None:
    st.error("データが読み込まれていません。main.pyから起動してください。")
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader("🏦 Banking Sector")
st.caption("💡 FRB H.8週次データ & SLOOS四半期調査 - 銀行の融資行動と信用状況を監視")

# === H.8 Weekly Data ===
st.markdown("### 📊 H.8 Weekly Data (週次銀行集計)")
st.caption("FRBが毎週発表する全米商業銀行の集計データ")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Bank Cash Holdings")
    show_metric_with_sparkline("Bank Cash", df.get('Bank_Cash'), 'Bank_Cash', "B", "Bank_Cash", notes="銀行の現金退蔵")
    if 'Bank_Cash' in df.columns and not df.get('Bank_Cash', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['Bank_Cash']].dropna(), height=200)

with col2:
    st.markdown("#### C&I Loans Outstanding")
    show_metric_with_sparkline("C&I Loans", df.get('CI_Loans'), 'CI_Loans', "B", "CI_Loans", notes="商工業融資残高")
    if 'CI_Loans' in df.columns and not df.get('CI_Loans', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['CI_Loans']].dropna(), height=200)

with col3:
    st.markdown("#### CRE Loans Outstanding")
    show_metric_with_sparkline("CRE Loans", df.get('CRE_Loans'), 'CRE_Loans', "B", "CRE_Loans", notes="商業用不動産融資残高")
    if 'CRE_Loans' in df.columns and not df.get('CRE_Loans', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['CRE_Loans']].dropna(), height=200)

# Additional H.8 Data row
st.markdown("---")
st.markdown("### 💳 H.8 Consumer & Deposits (新規追加)")
st.caption("消費者信用と銀行の調達状況")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Credit Card Loans")
    show_metric_with_sparkline("Credit Card", df.get('Credit_Card_Loans'), 'Credit_Card_Loans', "B", notes="消費者信用の強さ")
    if 'Credit_Card_Loans' in df.columns and not df.get('Credit_Card_Loans', pd.Series()).isna().all():
        st.line_chart(df[['Credit_Card_Loans']].dropna(), height=150)

with col2:
    st.markdown("#### Consumer Loans")
    show_metric_with_sparkline("Consumer", df.get('Consumer_Loans'), 'Consumer_Loans', "B", notes="消費者ローン残高")
    if 'Consumer_Loans' in df.columns and not df.get('Consumer_Loans', pd.Series()).isna().all():
        st.line_chart(df[['Consumer_Loans']].dropna(), height=150)

with col3:
    st.markdown("#### Bank Securities")
    show_metric_with_sparkline("Securities", df.get('Bank_Securities'), 'Bank_Securities', "B", notes="金利リスク指標")
    if 'Bank_Securities' in df.columns and not df.get('Bank_Securities', pd.Series()).isna().all():
        st.line_chart(df[['Bank_Securities']].dropna(), height=150)

with col4:
    st.markdown("#### Bank Deposits")
    show_metric_with_sparkline("Deposits", df.get('Bank_Deposits'), 'Bank_Deposits', "B", notes="調達力の変化")
    if 'Bank_Deposits' in df.columns and not df.get('Bank_Deposits', pd.Series()).isna().all():
        st.line_chart(df[['Bank_Deposits']].dropna(), height=150)

# === NEW: Financial Stress Indicators (Gemini推奨 2026-01-16) ===
st.markdown("---")
st.markdown("### ⚠️ 金融ストレス指標 (Gemini推奨)")
st.caption("💡 SVB危機先行警報・地銀取り付け騒ぎ検知・金融環境の本当の締め付け度")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### MOVE Index")
    st.caption("債券恐怖指数（VIXより先に反応）")
    show_metric_with_sparkline("MOVE", df.get('MOVE'), 'MOVE', "pt", notes="SVB破綻時に急騰")
    if 'MOVE' in df.columns and not df.get('MOVE', pd.Series()).isna().all():
        st.line_chart(df[['MOVE']].dropna(), height=150)

with col2:
    st.markdown("#### Small Bank Deposits")
    st.caption("地銀預金残高（取り付け騒ぎ警報）")
    show_metric_with_sparkline("Small Banks", df.get('Small_Bank_Deposits'), 'Small_Bank_Deposits', "B", notes="急減で地銀危機")
    if 'Small_Bank_Deposits' in df.columns and not df.get('Small_Bank_Deposits', pd.Series()).isna().all():
        st.line_chart(df[['Small_Bank_Deposits']].dropna(), height=150)

with col3:
    st.markdown("#### NFCI")
    st.caption("シカゴ連銀金融環境指数")
    show_metric_with_sparkline("NFCI", df.get('NFCI'), 'NFCI', "", notes="+で引締、-で緩和")
    if 'NFCI' in df.columns and not df.get('NFCI', pd.Series()).isna().all():
        st.line_chart(df[['NFCI']].dropna(), height=150)

with col4:
    st.markdown("#### CC Delinquency")
    st.caption("クレカ延滞率（消費者ストレス）")
    show_metric_with_sparkline("Delinquency", df.get('CC_Delinquency'), 'CC_Delinquency', "%", notes="上昇でリセッション警報")
    if 'CC_Delinquency' in df.columns and not df.get('CC_Delinquency', pd.Series()).isna().all():
        st.line_chart(df[['CC_Delinquency']].dropna(), height=150)

# Row 2: More stress indicators
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Breakeven 10Y")
    st.caption("期待インフレ率")
    show_metric_with_sparkline("Breakeven", df.get('Breakeven_10Y'), 'Breakeven_10Y', "%", notes="2.2-2.3%が安定")
    if 'Breakeven_10Y' in df.columns and not df.get('Breakeven_10Y', pd.Series()).isna().all():
        st.line_chart(df[['Breakeven_10Y']].dropna(), height=150)

with col2:
    st.markdown("#### CP Spread")
    st.caption("企業短期資金調達ストレス")
    show_metric_with_sparkline("CP-FF", df.get('CP_Spread'), 'CP_Spread', "%", notes="急騰でリーマン級警報")
    if 'CP_Spread' in df.columns and not df.get('CP_Spread', pd.Series()).isna().all():
        st.line_chart(df[['CP_Spread']].dropna(), height=150)

with col3:
    st.markdown("#### Total Loans")
    st.caption("融資総額（信用創造）")
    show_metric_with_sparkline("Loans", df.get('Total_Loans'), 'Total_Loans', "B", notes="減少でクレジットクランチ")
    if 'Total_Loans' in df.columns and not df.get('Total_Loans', pd.Series()).isna().all():
        st.line_chart(df[['Total_Loans']].dropna(), height=150)

with col4:
    st.markdown("#### Copper/Gold Ratio")
    st.caption("景気先行指標")
    if 'Copper' in df.columns and 'Gold' in df.columns:
        copper = df.get('Copper')
        gold = df.get('Gold')
        if copper is not None and gold is not None:
            # Calculate ratio series
            ratio_series = (copper / gold) * 1000
            
            # Get latest value
            latest_val = ratio_series.dropna().iloc[-1] if not ratio_series.dropna().empty else 0
            
            # Display Metric
            st.metric("Cu/Au Ratio", f"{latest_val:.2f}", help="Copper($)/Gold($) * 1000")
            
            # Display Chart
            if not ratio_series.dropna().empty:
                st.markdown("###### Long-term Trend (過去2年間)")
                st.line_chart(ratio_series.dropna(), height=150)

st.markdown("---")

# === SLOOS C&I Section ===
st.markdown("### 💰 C&I Lending (商工業融資) - SLOOS")
st.caption("💡 融資基準の厳格化と需要の乖離、残高減少はクレジットクランチの前兆")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### C&I Lending Tightening")
    st.caption("商工業融資基準の厳格化（純割合）")
    
    lending_val = df.get('Lending_Standards')
    if lending_val is not None and not lending_val.isna().all():
        val = lending_val.iloc[-1]
        delta = val - lending_val.iloc[-2] if len(lending_val) > 1 else None
        val_str = f"+{val:.1f}" if val >= 0 else f"{val:.1f}"
        st.metric(
            "Net %", 
            f"{val_str} pts",
            delta=f"{delta:+.1f}" if delta is not None else None,
            help=EXPLANATIONS.get('Lending_Standards', '')
        )
        
        if hasattr(df, 'attrs') and 'last_valid_dates' in df.attrs:
            if 'Lending_Standards' in df.attrs['last_valid_dates']:
                latest_date = df.attrs['last_valid_dates']['Lending_Standards']
                st.caption(f"📅 {latest_date} (四半期)")
        
        if 'Lending_Standards' in df.columns:
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['Lending_Standards']].dropna(), height=200)
    else:
        st.metric("Net %", "N/A")
    
    st.markdown("---")
    
    st.markdown("#### 融資基準（大・中堅企業）")
    show_metric_with_sparkline("Large/Mid Firms", df.get('CI_Std_Large'), 'CI_Std_Large', "pts", "CI_Std_Large", notes="0超で貸し渋り、20%超で警戒")
    if 'CI_Std_Large' in df.columns and not df.get('CI_Std_Large', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['CI_Std_Large']].dropna(), height=200)

with col2:
    st.markdown("#### 融資基準（小企業）")
    show_metric_with_sparkline("Small Firms", df.get('CI_Std_Small'), 'CI_Std_Small', "pts", "CI_Std_Small", notes="雇用悪化の先行指標")
    if 'CI_Std_Small' in df.columns and not df.get('CI_Std_Small', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['CI_Std_Small']].dropna(), height=200)
    
    st.markdown("---")
    
    st.markdown("#### 融資需要（大・中堅企業）")
    show_metric_with_sparkline("Demand", df.get('CI_Demand'), 'CI_Demand', "pts", "CI_Demand", notes="基準との乖離に注目")
    if 'CI_Demand' in df.columns and not df.get('CI_Demand', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['CI_Demand']].dropna(), height=200)

st.markdown("---")

# === SLOOS CRE Section ===
st.markdown("### 🏢 CRE Lending (商業用不動産融資) - SLOOS")
st.caption("💡 不動産開発・オフィスクライシス・借り換えリスクを監視")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 融資基準（建設・土地開発）")
    show_metric_with_sparkline("Construction", df.get('CRE_Std_Construction'), 'CRE_Std_Construction', "pts", "CRE_Std_Construction", notes="不動産開発の蛇口")
    if 'CRE_Std_Construction' in df.columns and not df.get('CRE_Std_Construction', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['CRE_Std_Construction']].dropna(), height=200)
    
    st.markdown("---")
    
    st.markdown("#### 融資基準（集合住宅）")
    show_metric_with_sparkline("Multifamily", df.get('CRE_Std_Multifamily'), 'CRE_Std_Multifamily', "pts", "CRE_Std_Multifamily", notes="住宅供給に影響")
    if 'CRE_Std_Multifamily' in df.columns and not df.get('CRE_Std_Multifamily', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['CRE_Std_Multifamily']].dropna(), height=200)

with col2:
    st.markdown("#### 融資基準（オフィス等）")
    show_metric_with_sparkline("Office/NonRes", df.get('CRE_Std_Office'), 'CRE_Std_Office', "pts", "CRE_Std_Office", notes="オフィスクライシス警戒")
    if 'CRE_Std_Office' in df.columns and not df.get('CRE_Std_Office', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['CRE_Std_Office']].dropna(), height=200)
    
    st.markdown("---")
    
    st.markdown("#### 融資需要")
    show_metric_with_sparkline("CRE Demand", df.get('CRE_Demand'), 'CRE_Demand', "pts", "CRE_Demand", notes="不動産投資意欲")
    if 'CRE_Demand' in df.columns and not df.get('CRE_Demand', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['CRE_Demand']].dropna(), height=200)

# === Loan Comparison Chart ===
st.markdown("---")
st.markdown("### 📈 融資残高の推移比較")

loan_cols = [c for c in ['CI_Loans', 'CRE_Loans'] if c in df.columns and not df[c].isna().all()]
if loan_cols:
    st.line_chart(df[loan_cols].tail(520), height=250)
