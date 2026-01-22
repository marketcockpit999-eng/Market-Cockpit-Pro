# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 2: Global Money & FX
グローバル流動性、為替、コモディティ、仮想通貨

NOTE: Non-US M2 data (CN, JP, EU) removed due to unreliable FRED data sources.
      Only US M2 and Global Liquidity Proxy (Fed+ECB) are maintained.
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import show_metric_with_sparkline, styled_line_chart, EXPLANATIONS, DATA_FREQUENCY, t

# Get data from session state
df = st.session_state.get('df')
df_original = st.session_state.get('df_original')

if df is None:
    st.error(t('error_data_not_loaded'))
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader("🌏 Global Money & FX")
st.caption(t('global_money_subtitle'))

# === US M2 Section ===
st.markdown("---")
st.markdown(f"### 💵 US Money Supply (M2)")
st.caption(t('us_m2_desc'))

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🇺🇸 US M2 (Nominal)")
    show_metric_with_sparkline("US M2", df.get('M2SL'), 'M2SL', "T", "M2SL", notes=t('m2_nominal_notes'))
    if 'M2SL' in df.columns and not df.get('M2SL', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['M2SL']], height=150)

with col2:
    st.markdown("#### 🇺🇸 US M2 (Real)")
    show_metric_with_sparkline("US M2 Real", df.get('M2REAL'), 'M2REAL', "T", "M2REAL", notes=t('m2_real_notes'))
    if 'M2REAL' in df.columns and not df.get('M2REAL', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['M2REAL']], height=150)


# === FX Section ===
st.markdown("---")
st.markdown(f"### {t('fx_section')}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### DXY")
    show_metric_with_sparkline(t('dollar_index'), df.get('DXY'), 'DXY', "pt", "DXY", notes=t('dollar_strength'), decimal_places=3)
    if 'DXY' in df.columns and not df.get('DXY', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['DXY']], height=150)

with col2:
    st.markdown("#### USD/JPY")
    show_metric_with_sparkline("USD/JPY", df.get('USDJPY'), 'USDJPY', "¥", "USDJPY", notes=t('yen_carry'), decimal_places=3)
    if 'USDJPY' in df.columns and not df.get('USDJPY', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['USDJPY']], height=150)

with col3:
    st.markdown("#### EUR/USD")
    show_metric_with_sparkline("EUR/USD", df.get('EURUSD'), 'EURUSD', "$", "EURUSD", notes=t('euro_dollar'), decimal_places=3)
    if 'EURUSD' in df.columns and not df.get('EURUSD', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['EURUSD']], height=150)

with col4:
    st.markdown("#### USD/CNY")
    show_metric_with_sparkline("USD/CNY", df.get('USDCNY'), 'USDCNY', "CNY", "USDCNY", notes=t('yuan'), decimal_places=3)
    if 'USDCNY' in df.columns and not df.get('USDCNY', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['USDCNY']], height=150)

# === Global Indices Section ===
st.markdown("---")
st.markdown(f"### {t('global_indices')}")
st.caption(t('global_indices_desc'))

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🇯🇵 Nikkei 225")
    show_metric_with_sparkline("Nikkei 225", df.get('NIKKEI'), 'NIKKEI', "¥", "NIKKEI", notes=t('nikkei_notes'), decimal_places=0)
    if 'NIKKEI' in df.columns and not df.get('NIKKEI', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['NIKKEI']], height=150)

with col2:
    st.markdown("#### 🇺🇸 S&P 500")
    show_metric_with_sparkline("S&P 500", df.get('SP500'), 'SP500', "pt", "SP500", notes=t('sp500_notes'), decimal_places=0)
    if 'SP500' in df.columns and not df.get('SP500', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['SP500']], height=150)

# === Commodities Section ===
st.markdown("---")
st.markdown(f"### {t('commodities_section')}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Gold")
    show_metric_with_sparkline("Gold", df.get('Gold'), 'Gold', "$", "Gold", notes=t('gold_futures'), decimal_places=3)
    if 'Gold' in df.columns and not df.get('Gold', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['Gold']], height=150)

with col2:
    st.markdown("#### Silver")
    show_metric_with_sparkline("Silver", df.get('Silver'), 'Silver', "$", "Silver", notes=t('silver_futures'), decimal_places=3)
    if 'Silver' in df.columns and not df.get('Silver', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['Silver']], height=150)

with col3:
    st.markdown("#### Oil (WTI)")
    show_metric_with_sparkline("Oil", df.get('Oil'), 'Oil', "$", "Oil", notes=t('oil_futures'), decimal_places=3)
    if 'Oil' in df.columns and not df.get('Oil', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['Oil']], height=150)

with col4:
    st.markdown("#### Copper")
    show_metric_with_sparkline("Copper", df.get('Copper'), 'Copper', "$", "Copper", notes=t('copper_futures'), decimal_places=3)
    if 'Copper' in df.columns and not df.get('Copper', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['Copper']], height=150)

# === Crypto Section ===
st.markdown("---")
st.markdown(f"### {t('crypto_section')}")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Bitcoin (BTC)")
    show_metric_with_sparkline("BTC", df.get('BTC'), 'BTC', "$", "BTC", notes=t('risk_on_indicator'), decimal_places=3)
    if 'BTC' in df.columns and not df.get('BTC', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['BTC']], height=200)

with col2:
    st.markdown("#### Ethereum (ETH)")
    show_metric_with_sparkline("ETH", df.get('ETH'), 'ETH', "$", "ETH", notes=t('defi_base'), decimal_places=3)
    if 'ETH' in df.columns and not df.get('ETH', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[['ETH']], height=200)


