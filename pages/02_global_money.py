# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 2: Global Money & FX
グローバル流動性、為替、コモディティ、仮想通貨
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import show_metric_with_sparkline, EXPLANATIONS, DATA_FREQUENCY

# Manual Global M2 data
MANUAL_GLOBAL_M2 = {
    'CN_M2': {'value': 336.9, 'date': '2025-11', 'source': 'PBoC', 'cpi': 0.2},
    'JP_M2': {'value': 1260, 'date': '2025-11', 'source': 'BOJ', 'cpi': 2.9},
    'EU_M2': {'value': 15.6, 'date': '2025-11', 'source': 'ECB', 'cpi': 2.1},
}

# Get data from session state
df = st.session_state.get('df')
df_original = st.session_state.get('df_original')

if df is None:
    st.error("データが読み込まれていません。main.pyから起動してください。")
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader("🌏 Global Money & FX")
st.caption("💡 グローバル流動性、為替、コモディティ、仮想通貨の動向")

# === Global M2 Section ===
st.markdown("---")
st.markdown("### 💵 Global M2 Money Supply")
st.caption("💡 世界の主要国マネーサプライ動向")

# Get exchange rates
usdjpy = df.get('USDJPY').iloc[-1] if df.get('USDJPY') is not None and len(df.get('USDJPY', pd.Series()).dropna()) > 0 else 157.0
eurusd = df.get('EURUSD').iloc[-1] if df.get('EURUSD') is not None and len(df.get('EURUSD', pd.Series()).dropna()) > 0 else 1.04
usdcny = df.get('USDCNY').iloc[-1] if df.get('USDCNY') is not None and len(df.get('USDCNY', pd.Series()).dropna()) > 0 else 7.30

# === Global M2 TOTAL (BTC相関指標) ===
if 'Global_M2' in df.columns and not df.get('Global_M2', pd.Series()).isna().all():
    st.markdown("### 🌍 Global M2 Total (USD換算)")
    st.caption("💡 世界主要4地域（US+CN+JP+EU）のM2合計 - BTCとの相関で有名な指標")
    
    global_m2_series = df['Global_M2'].dropna()
    if len(global_m2_series) > 0:
        gm2_val = global_m2_series.iloc[-1]
        gm2_change = gm2_val - global_m2_series.iloc[-2] if len(global_m2_series) > 1 else 0
        
        col_gm2_1, col_gm2_2 = st.columns([1, 2])
        
        with col_gm2_1:
            st.metric(
                "🌍 Global M2 Total", 
                f"${gm2_val:.1f}T",
                delta=f"{gm2_change:+.2f}T vs 前日",
                help="US M2 + CN M2/USDCNY + JP M2/USDJPY + EU M2*EURUSD"
            )
            st.caption("計算式: US + CN/CNY + JP/JPY + EU*EUR")
        
        with col_gm2_2:
            # Global M2 vs BTC comparison
            if 'BTC' in df.columns:
                st.markdown("##### 📊 Global M2 vs BTC (過去2年間)")
                import plotly.graph_objects as go
                from plotly.subplots import make_subplots
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['Global_M2'], name='Global M2 (T)', line=dict(color='cyan')),
                    secondary_y=False
                )
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['BTC'], name='BTC ($)', line=dict(color='orange')),
                    secondary_y=True
                )
                fig.update_layout(
                    template='plotly_dark',
                    height=250,
                    hovermode='x unified',
                    margin=dict(l=0, r=0, t=30, b=0)
                )
                fig.update_yaxes(title_text="Global M2 ($T)", secondary_y=False)
                fig.update_yaxes(title_text="BTC ($)", secondary_y=True)
                st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# US & China
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🇺🇸 US M2")
    show_metric_with_sparkline("US M2 (Nominal)", df.get('M2SL'), 'M2SL', "T", notes="名目")
    show_metric_with_sparkline("US M2 (Real)", df.get('M2REAL'), 'M2REAL', "T", notes="実質(1982-84基準)")
    if 'M2SL' in df.columns and not df.get('M2SL', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['M2SL']].dropna(), height=150)

with col2:
    st.markdown("#### 🇨🇳 China M2")
    if 'CN_M2' in df.columns and not df.get('CN_M2', pd.Series()).isna().all():
        if 'CN_M2' in MANUAL_GLOBAL_M2:
             m = MANUAL_GLOBAL_M2['CN_M2']
             st.caption(f"📅 {m['date']} (手動更新)")
             st.caption(f"⚠️ 自動取得不可・{m['source']}発表より")
        show_metric_with_sparkline("CN M2 (Nominal)", df.get('CN_M2'), 'CN_M2', "T CNY", notes="名目")
        cn_m2_val = df.get('CN_M2').iloc[-1]
        st.markdown(f"**💵 ≈ ${cn_m2_val/usdcny:.1f}T USD** (1 USD = {usdcny:.2f} CNY)")
        
        if 'CN_CPI' in df.columns:
            cn_cpi = df.get('CN_CPI').iloc[-1]
            show_metric_with_sparkline("CN M2 (Real)", df.get('CN_M2_Real'), 'CN_M2_Real', "T CNY", notes=f"CPI {cn_cpi}%調整")
            cn_m2_real_val = df.get('CN_M2_Real').iloc[-1]
            st.markdown(f"**💵 ≈ ${cn_m2_real_val/usdcny:.1f}T USD**")
        
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['CN_M2']].dropna(), height=150)
    else:
        st.warning("⚠️ China M2 Data Unavailable (FRED Source Outdated)")
    
    st.markdown("---")
    st.markdown("##### 📊 Credit Impulse（信用刺激指数）")
    st.caption("⚠️ 代用計算: BIS経由FRED四半期信用残高データ(CRDQCNAPABIS)使用")
    show_metric_with_sparkline("Credit Impulse", df.get('CN_Credit_Impulse'), 'CN_Credit_Impulse', "%", notes="(信用フロー変化/GDP)")
    if 'CN_Credit_Impulse' in df.columns and not df.get('CN_Credit_Impulse', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去5年間)")
        st.line_chart(df[['CN_Credit_Impulse']].dropna(), height=150)

# Japan & Euro
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 🇯🇵 Japan M2")
    if 'JP_M2' in df.columns and not df.get('JP_M2', pd.Series()).isna().all():
        if 'JP_M2' in MANUAL_GLOBAL_M2:
             m = MANUAL_GLOBAL_M2['JP_M2']
             st.caption(f"📅 {m['date']} (手動更新)")
             st.caption(f"⚠️ 自動取得不可・{m['source']}発表より")
        show_metric_with_sparkline("JP M2 (Nominal)", df.get('JP_M2'), 'JP_M2', "T JPY", notes="名目")
        jp_m2_val = df.get('JP_M2').iloc[-1]
        st.markdown(f"**💵 ≈ ${jp_m2_val/usdjpy*1000/1000:.1f}T USD** (1 USD = {usdjpy:.1f} JPY)")
        
        if 'JP_CPI' in df.columns:
            jp_cpi = df.get('JP_CPI').iloc[-1]
            show_metric_with_sparkline("JP M2 (Real)", df.get('JP_M2_Real'), 'JP_M2_Real', "T JPY", notes=f"CPI {jp_cpi}%調整")
            jp_m2_real_val = df.get('JP_M2_Real').iloc[-1]
            st.markdown(f"**💵 ≈ ${jp_m2_real_val/usdjpy*1000/1000:.1f}T USD**")
            
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['JP_M2']].dropna(), height=150)
    else:
        st.warning("⚠️ Japan M2 Data Unavailable")

with col4:
    st.markdown("#### 🇪🇺 Euro M2")
    if 'EU_M2' in df.columns and not df.get('EU_M2', pd.Series()).isna().all():
        if 'EU_M2' in MANUAL_GLOBAL_M2:
             m = MANUAL_GLOBAL_M2['EU_M2']
             st.caption(f"📅 {m['date']} (手動更新)")
             st.caption(f"⚠️ 自動取得不可・{m['source']}発表より")
        show_metric_with_sparkline("EU M2 (Nominal)", df.get('EU_M2'), 'EU_M2', "T EUR", notes="名目")
        eu_m2_val = df.get('EU_M2').iloc[-1]
        st.markdown(f"**💵 ≈ ${eu_m2_val*eurusd:.1f}T USD** (1 EUR = {eurusd:.2f} USD)")
        
        if 'EU_CPI' in df.columns:
            eu_cpi = df.get('EU_CPI').iloc[-1]
            show_metric_with_sparkline("EU M2 (Real)", df.get('EU_M2_Real'), 'EU_M2_Real', "T EUR", notes=f"CPI {eu_cpi}%調整")
            eu_m2_real_val = df.get('EU_M2_Real').iloc[-1]
            st.markdown(f"**💵 ≈ ${eu_m2_real_val*eurusd:.1f}T USD**")
            
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['EU_M2']].dropna(), height=150)
    else:
        st.warning("⚠️ Euro M2 Data Unavailable")

# === FX Section ===
st.markdown("---")
st.markdown("### 💱 Foreign Exchange")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### DXY")
    show_metric_with_sparkline("Dollar Index", df.get('DXY'), 'DXY', "pt", notes="ドル強弱指数", decimal_places=3)
    if 'DXY' in df.columns and not df.get('DXY', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend")
        st.line_chart(df[['DXY']].dropna(), height=150)

with col2:
    st.markdown("#### USD/JPY")
    show_metric_with_sparkline("USD/JPY", df.get('USDJPY'), 'USDJPY', "¥", notes="円キャリー", decimal_places=3)
    if 'USDJPY' in df.columns and not df.get('USDJPY', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend")
        st.line_chart(df[['USDJPY']].dropna(), height=150)

with col3:
    st.markdown("#### EUR/USD")
    show_metric_with_sparkline("EUR/USD", df.get('EURUSD'), 'EURUSD', "$", notes="ユーロドル", decimal_places=3)
    if 'EURUSD' in df.columns and not df.get('EURUSD', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend")
        st.line_chart(df[['EURUSD']].dropna(), height=150)

with col4:
    st.markdown("#### USD/CNY")
    show_metric_with_sparkline("USD/CNY", df.get('USDCNY'), 'USDCNY', "CNY", notes="人民元", decimal_places=3)
    if 'USDCNY' in df.columns and not df.get('USDCNY', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend")
        st.line_chart(df[['USDCNY']].dropna(), height=150)

# === Global Indices Section ===
st.markdown("---")
st.markdown("### 📈 Global Indices")
st.caption("💡 主要株価指数")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🇯🇵 Nikkei 225")
    show_metric_with_sparkline("Nikkei 225", df.get('NIKKEI'), 'NIKKEI', "¥", notes="日経平均株価", decimal_places=0)
    if 'NIKKEI' in df.columns and not df.get('NIKKEI', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['NIKKEI']].dropna(), height=150)

with col2:
    st.markdown("#### 🇺🇸 S&P 500")
    show_metric_with_sparkline("S&P 500", df.get('SP500'), 'SP500', "pt", notes="米国大型株指数", decimal_places=0)
    if 'SP500' in df.columns and not df.get('SP500', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['SP500']].dropna(), height=150)

# === Commodities Section ===
st.markdown("---")
st.markdown("### 🛢️ Commodities")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Gold")
    show_metric_with_sparkline("Gold", df.get('Gold'), 'Gold', "$", notes="金先物", decimal_places=3)
    if 'Gold' in df.columns and not df.get('Gold', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend")
        st.line_chart(df[['Gold']].dropna(), height=150)

with col2:
    st.markdown("#### Silver")
    show_metric_with_sparkline("Silver", df.get('Silver'), 'Silver', "$", notes="銀先物", decimal_places=3)
    if 'Silver' in df.columns and not df.get('Silver', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend")
        st.line_chart(df[['Silver']].dropna(), height=150)

with col3:
    st.markdown("#### Oil (WTI)")
    show_metric_with_sparkline("Oil", df.get('Oil'), 'Oil', "$", notes="原油先物", decimal_places=3)
    if 'Oil' in df.columns and not df.get('Oil', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend")
        st.line_chart(df[['Oil']].dropna(), height=150)

with col4:
    st.markdown("#### Copper")
    show_metric_with_sparkline("Copper", df.get('Copper'), 'Copper', "$", notes="銅先物（景気先行指標）", decimal_places=3)
    if 'Copper' in df.columns and not df.get('Copper', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend")
        st.line_chart(df[['Copper']].dropna(), height=150)

# === Crypto Section ===
st.markdown("---")
st.markdown("### 🪙 Cryptocurrency")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Bitcoin (BTC)")
    show_metric_with_sparkline("BTC", df.get('BTC'), 'BTC', "$", notes="リスクオン指標", decimal_places=3)
    if 'BTC' in df.columns and not df.get('BTC', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['BTC']].dropna(), height=200)

with col2:
    st.markdown("#### Ethereum (ETH)")
    show_metric_with_sparkline("ETH", df.get('ETH'), 'ETH', "$", notes="DeFi基盤", decimal_places=3)
    if 'ETH' in df.columns and not df.get('ETH', pd.Series()).isna().all():
        st.markdown("###### Long-term Trend (過去2年間)")
        st.line_chart(df[['ETH']].dropna(), height=200)
