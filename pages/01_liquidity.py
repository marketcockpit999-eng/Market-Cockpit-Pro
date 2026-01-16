# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 1: Liquidity & Rates
流動性、金利、Fed バランスシート、銀行セクター
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
    get_pe_ratios,
    get_crypto_leverage_data,
    show_metric,
    show_metric_with_sparkline,
    plot_dual_axis,
    plot_soma_composition,
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
st.subheader("🏦 Liquidity & The Fed")

# === VALUATION & LEVERAGE SECTION ===
st.markdown("#### 📊 バリュエーション & レバレッジ指標")
st.caption("市場の過熱度とレバレッジ状況を一目で確認")

pe_data = get_pe_ratios()
leverage_data = get_crypto_leverage_data()

col_val1, col_val2, col_val3, col_val4 = st.columns(4)

with col_val1:
    if pe_data and pe_data.get('sp500_pe'):
        pe = pe_data['sp500_pe']
        avg = pe_data['sp500_pe_avg']
        delta = pe - avg
        color = "🔴" if pe > 25 else "🟡" if pe > 20 else "🟢"
        st.metric(
            f"{color} S&P 500 P/E",
            f"{pe:.1f}",
            delta=f"{delta:+.1f} vs avg ({avg:.1f})",
            help="歴史的平均は約19.5。25以上は過熱、15以下は割安"
        )
    else:
        st.metric("S&P 500 P/E", "取得中...")

with col_val2:
    if pe_data and pe_data.get('nasdaq_pe'):
        pe = pe_data['nasdaq_pe']
        color = "🔴" if pe > 35 else "🟡" if pe > 28 else "🟢"
        st.metric(
            f"{color} NASDAQ P/E (QQQ)",
            f"{pe:.1f}",
            help="ハイテク株のバリュエーション指標"
        )
    else:
        st.metric("NASDAQ P/E", "取得中...")

with col_val3:
    if leverage_data and leverage_data.get('btc_funding_rate') is not None:
        fr = leverage_data['btc_funding_rate']
        if fr > 0.05:
            color = "🔴"
            status = "ロング過多"
        elif fr < -0.05:
            color = "🔵"
            status = "ショート過多"
        else:
            color = "🟢"
            status = "中立"
        st.metric(
            f"{color} BTC Funding Rate",
            f"{fr:.4f}%",
            delta=status,
            help="Funding Rate > 0.1% はロングポジション過多（過熱）。< -0.1% はショート過多"
        )
    else:
        st.metric("BTC Funding Rate", "取得中...")

with col_val4:
    if leverage_data and leverage_data.get('btc_long_short_ratio'):
        ratio = leverage_data['btc_long_short_ratio']
        if ratio > 1.5:
            color = "🔴"
            status = "ロング偏り"
        elif ratio < 0.7:
            color = "🔵"
            status = "ショート偏り"
        else:
            color = "🟢"
            status = "均衡"
        st.metric(
            f"{color} BTC Long/Short Ratio",
            f"{ratio:.2f}",
            delta=status,
            help="ロング口座/ショート口座の比率。1.0が均衡"
        )
    else:
        st.metric("BTC L/S Ratio", "取得中...")

# === Open Interest ===
if leverage_data:
    st.markdown("#### 📈 Open Interest (レバレッジ積み上がり)")
    
    col_btc, col_eth = st.columns(2)
    
    with col_btc:
        oi = leverage_data.get('btc_open_interest', 0)
        avg = leverage_data.get('btc_oi_avg_30d')
        ath = leverage_data.get('btc_oi_ath')
        
        if oi and avg:
            pct_vs_avg = ((oi - avg) / avg) * 100
            pct_vs_ath = (oi / ath * 100) if ath else 0
            
            if pct_vs_avg > 20:
                color = "🔴"
                status = "危険ゾーン"
            elif pct_vs_avg > 5:
                color = "🟡"
                status = "高め"
            elif pct_vs_avg < -20:
                color = "🔵"
                status = "低め"
            else:
                color = "🟢"
                status = "正常"
            
            st.metric(
                f"{color} BTC Open Interest",
                f"{oi:,.0f} BTC",
                delta=f"{pct_vs_avg:+.1f}% vs 30日平均",
                help=f"30日平均: {avg:,.0f} BTC | ATH: {ath:,.0f} BTC ({pct_vs_ath:.0f}%)"
            )
            st.caption(f"📊 ATH比: **{pct_vs_ath:.0f}%** | 状態: **{status}**")
        else:
            st.metric("BTC Open Interest", f"{oi:,.0f} BTC" if oi else "取得中...")
    
    with col_eth:
        oi = leverage_data.get('eth_open_interest', 0)
        avg = leverage_data.get('eth_oi_avg_30d')
        ath = leverage_data.get('eth_oi_ath')
        
        if oi and avg:
            pct_vs_avg = ((oi - avg) / avg) * 100
            pct_vs_ath = (oi / ath * 100) if ath else 0
            
            if pct_vs_avg > 20:
                color = "🔴"
                status = "危険ゾーン"
            elif pct_vs_avg > 5:
                color = "🟡"
                status = "高め"
            elif pct_vs_avg < -20:
                color = "🔵"
                status = "低め"
            else:
                color = "🟢"
                status = "正常"
            
            st.metric(
                f"{color} ETH Open Interest",
                f"{oi:,.0f} ETH",
                delta=f"{pct_vs_avg:+.1f}% vs 30日平均",
                help=f"30日平均: {avg:,.0f} ETH | ATH: {ath:,.0f} ETH ({pct_vs_ath:.0f}%)"
            )
            st.caption(f"📊 ATH比: **{pct_vs_ath:.0f}%** | 状態: **{status}**")
        else:
            st.metric("ETH Open Interest", f"{oi:,.0f} ETH" if oi else "取得中...")
    
    st.caption("""
    💡 **Open Interest の見方**
    - **30日平均比 +20%以上** 🔴: レバレッジ過多 → 清算連鎖リスク高
    - **30日平均比 ±5%** 🟢: 正常レンジ
    - **ATH比**: 過去30日の最高値に対する現在位置
    """)

st.markdown("---")

# === Net Liquidity ===
st.markdown("#### Net Liquidity")

col1, col2 = st.columns([1, 3])
with col1:
    show_metric_with_sparkline("Net Liquidity", df.get('Net_Liquidity'), 'Net_Liquidity', "B", "Net_Liquidity", notes="市場の真の燃料")
with col2:
    st.markdown("##### Net Liquidity vs S&P 500 (過去2年間)")
    plot_dual_axis(df, 'Net_Liquidity', 'SP500', 'Net Liquidity (L)', 'S&P 500 (R)')

st.markdown("---")

# === ON RRP, Reserves, TGA ===
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### ON RRP")
    show_metric_with_sparkline("ON RRP", df.get('ON_RRP'), 'ON_RRP', "B", "ON_RRP", notes="余剰資金")
    if 'ON_RRP' in df.columns and not df.get('ON_RRP', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['ON_RRP']].dropna(), height=250)
    
    st.markdown("")
    
    st.markdown("#### TGA")
    show_metric_with_sparkline("TGA", df.get('TGA'), 'TGA', "B", "TGA", notes="政府口座")
    if 'TGA' in df.columns and not df.get('TGA', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['TGA']].dropna(), height=250)

with col2:
    st.markdown("#### Reserves")
    show_metric_with_sparkline("Reserves", df.get('Reserves'), 'Reserves', "B", "Reserves", notes="銀行準備預金")
    if 'Reserves' in df.columns and not df.get('Reserves', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['Reserves']].dropna(), height=250)

st.markdown("---")
st.subheader("🔧 Market Plumbing (Repo & Liquidity)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### SRF")
    show_metric_with_sparkline("SRF", df.get('SRF'), 'SRF', "B", "SRF", notes="国内リポ市場")
    if 'SRF' in df.columns and not df.get('SRF', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['SRF']].dropna(), height=200)
    
    st.markdown("")
    
    st.markdown("#### SOFR")
    show_metric_with_sparkline("SOFR", df.get('SOFR'), 'SOFR', "%", "SOFR", notes="担保付金利", decimal_places=3)
    if 'SOFR' in df.columns and not df.get('SOFR', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['SOFR']].dropna(), height=200)

with col2:
    st.markdown("#### FIMA")
    show_metric_with_sparkline("FIMA", df.get('FIMA'), 'FIMA', "B", "FIMA", notes="海外ドル流動性")
    if 'FIMA' in df.columns and not df.get('FIMA', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['FIMA']].dropna(), height=200)
    
    st.markdown("")
    
    st.markdown("#### EFFR - IORB")
    diff = None
    if 'EFFR' in df.columns and 'IORB' in df.columns:
        diff = (df['EFFR'] - df['IORB']) * 100
    show_metric("EFFR - IORB", diff, "bps", notes="連銀準備金状況")
    
    rate_cols = ['EFFR', 'IORB']
    valid_rates = [c for c in rate_cols if c in df.columns and not df.get(c, pd.Series()).isna().all()]
    if valid_rates:
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[valid_rates].dropna(), height=200)

st.markdown("---")
st.subheader("🏛️ Fed Balance Sheet (SOMA)")

# RMP Status
rmp_status_series = df.get('RMP_Status_Text')
rmp_status = rmp_status_series.iloc[-1] if hasattr(rmp_status_series, 'iloc') and len(rmp_status_series) > 0 else "データ取得中..."
rmp_active_series = df.get('RMP_Alert_Active', pd.Series([False]))
rmp_active = rmp_active_series.iloc[-1] if hasattr(rmp_active_series, 'iloc') and len(rmp_active_series) > 0 else False

if rmp_active:
    st.info(f"📊 **RMP状況**: {rmp_status}")
else:
    st.warning(f"ℹ️ **RMP状況**: {rmp_status}")

st.markdown("##### SOMA Composition (Total & Bills Ratio)")
plot_soma_composition(df)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### SOMA Total")
    show_metric_with_sparkline("SOMA Total", df.get('SOMA_Total'), 'SOMA_Total', "B", "SOMA_Total", notes="保有資産総額")

with col2:
    st.markdown("#### SOMA Bills")
    show_metric_with_sparkline("SOMA Bills", df.get('SOMA_Bills'), 'SOMA_Bills', "B", "SOMA_Bills", notes="短期国債保有高")
    if 'SOMA_Bills' in df.columns and not df.get('SOMA_Bills', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['SOMA_Bills']].dropna(), height=200)

with col3:
    st.markdown("#### Bills Ratio")
    show_metric_with_sparkline("Bills Ratio", df.get('SomaBillsRatio'), 'SomaBillsRatio', "%", "SomaBillsRatio", notes="短期国債構成比")

st.markdown("---")
st.subheader("🚨 Emergency Loans (Discount Window)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Total Loans")
    show_metric_with_sparkline("Total Loans", df.get('Total_Loans'), 'Total_Loans', "B", "Window", notes="緊急貸出総額")
    if 'Total_Loans' in df.columns and not df.get('Total_Loans', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['Total_Loans']].dropna(), height=250)

with col2:
    st.markdown("#### Primary Credit")
    show_metric_with_sparkline("Primary Credit", df.get('Primary_Credit'), 'Primary_Credit', "B", "Primary", notes="健全行向け", alert_func=lambda x: x>1)
    if 'Primary_Credit' in df.columns and not df.get('Primary_Credit', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['Primary_Credit']].dropna(), height=250)


st.markdown("---")
st.markdown("---")
st.subheader("⚠️ Risk & Bonds")
st.caption("💡 市場のリスク状態と債券市場の動向を監視")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### VIX Index")
    show_metric_with_sparkline("VIX Index", df.get('VIX'), 'VIX', "pt", "VIX", notes="恐怖指数", alert_func=lambda x: x>20)
    if 'VIX' in df.columns and not df.get('VIX', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['VIX']].dropna(), height=200)

with col2:
    st.markdown("#### Credit Spread")
    show_metric_with_sparkline("Credit Spread", df.get('Credit_Spread'), 'Credit_Spread', "%", notes="ジャンク債スプレッド", decimal_places=3)
    if 'Credit_Spread' in df.columns and not df.get('Credit_Spread', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['Credit_Spread']].dropna(), height=200)

with col3:
    st.markdown("#### US 10Y Yield")
    show_metric_with_sparkline("US 10Y Yield", df.get('US_TNX'), 'US_TNX', "%", notes="長期金利", decimal_places=3)
    if 'US_TNX' in df.columns and not df.get('US_TNX', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['US_TNX']].dropna(), height=200)
