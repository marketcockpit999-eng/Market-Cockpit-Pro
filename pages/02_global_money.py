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

from utils import show_metric_with_sparkline, EXPLANATIONS, DATA_FREQUENCY, t

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
st.caption("💡 米国のマネーサプライ - FREDから自動取得")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🇺🇸 US M2 (Nominal)")
    show_metric_with_sparkline("US M2", df.get('M2SL'), 'M2SL', "T", "M2SL", notes="名目M2")
    if 'M2SL' in df.columns and not df.get('M2SL', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['M2SL']].dropna(), height=150)

with col2:
    st.markdown("#### 🇺🇸 US M2 (Real)")
    show_metric_with_sparkline("US M2 Real", df.get('M2REAL'), 'M2REAL', "T", "M2REAL", notes="実質M2 (1982-84基準)")
    if 'M2REAL' in df.columns and not df.get('M2REAL', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['M2REAL']].dropna(), height=150)


# === FX Section ===
st.markdown("---")
st.markdown(f"### {t('fx_section')}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### DXY")
    show_metric_with_sparkline(t('dollar_index'), df.get('DXY'), 'DXY', "pt", "DXY", notes=t('dollar_strength'), decimal_places=3)
    if 'DXY' in df.columns and not df.get('DXY', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['DXY']].dropna(), height=150)

with col2:
    st.markdown("#### USD/JPY")
    show_metric_with_sparkline("USD/JPY", df.get('USDJPY'), 'USDJPY', "¥", "USDJPY", notes=t('yen_carry'), decimal_places=3)
    if 'USDJPY' in df.columns and not df.get('USDJPY', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['USDJPY']].dropna(), height=150)

with col3:
    st.markdown("#### EUR/USD")
    show_metric_with_sparkline("EUR/USD", df.get('EURUSD'), 'EURUSD', "$", "EURUSD", notes=t('euro_dollar'), decimal_places=3)
    if 'EURUSD' in df.columns and not df.get('EURUSD', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['EURUSD']].dropna(), height=150)

with col4:
    st.markdown("#### USD/CNY")
    show_metric_with_sparkline("USD/CNY", df.get('USDCNY'), 'USDCNY', "CNY", "USDCNY", notes=t('yuan'), decimal_places=3)
    if 'USDCNY' in df.columns and not df.get('USDCNY', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['USDCNY']].dropna(), height=150)

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
        st.line_chart(df[['NIKKEI']].dropna(), height=150)

with col2:
    st.markdown("#### 🇺🇸 S&P 500")
    show_metric_with_sparkline("S&P 500", df.get('SP500'), 'SP500', "pt", "SP500", notes=t('sp500_notes'), decimal_places=0)
    if 'SP500' in df.columns and not df.get('SP500', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['SP500']].dropna(), height=150)

# === Commodities Section ===
st.markdown("---")
st.markdown(f"### {t('commodities_section')}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Gold")
    show_metric_with_sparkline("Gold", df.get('Gold'), 'Gold', "$", "Gold", notes=t('gold_futures'), decimal_places=3)
    if 'Gold' in df.columns and not df.get('Gold', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['Gold']].dropna(), height=150)

with col2:
    st.markdown("#### Silver")
    show_metric_with_sparkline("Silver", df.get('Silver'), 'Silver', "$", "Silver", notes=t('silver_futures'), decimal_places=3)
    if 'Silver' in df.columns and not df.get('Silver', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['Silver']].dropna(), height=150)

with col3:
    st.markdown("#### Oil (WTI)")
    show_metric_with_sparkline("Oil", df.get('Oil'), 'Oil', "$", "Oil", notes=t('oil_futures'), decimal_places=3)
    if 'Oil' in df.columns and not df.get('Oil', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['Oil']].dropna(), height=150)

with col4:
    st.markdown("#### Copper")
    show_metric_with_sparkline("Copper", df.get('Copper'), 'Copper', "$", "Copper", notes=t('copper_futures'), decimal_places=3)
    if 'Copper' in df.columns and not df.get('Copper', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['Copper']].dropna(), height=150)

# === Crypto Section ===
st.markdown("---")
st.markdown(f"### {t('crypto_section')}")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Bitcoin (BTC)")
    show_metric_with_sparkline("BTC", df.get('BTC'), 'BTC', "$", "BTC", notes=t('risk_on_indicator'), decimal_places=3)
    if 'BTC' in df.columns and not df.get('BTC', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['BTC']].dropna(), height=200)

with col2:
    st.markdown("#### Ethereum (ETH)")
    show_metric_with_sparkline("ETH", df.get('ETH'), 'ETH', "$", "ETH", notes=t('defi_base'), decimal_places=3)
    if 'ETH' in df.columns and not df.get('ETH', pd.Series()).isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        st.line_chart(df[['ETH']].dropna(), height=200)

# === Fiat Health Monitor Section ===
st.markdown("---")
st.markdown("### 📉 Fiat Health Monitor")
st.caption(t('fiat_health_subtitle'))

def calculate_fiat_health_data(df):
    """Calculate Gold-denominated and BTC-denominated currency values
    
    Returns:
        tuple: (DataFrame or None, list of missing columns)
    """
    result = {}
    
    # Required columns check
    required = ['Gold', 'BTC', 'USDJPY', 'EURUSD', 'USDCNY', 'GBPUSD', 'USDCHF', 'AUDUSD']
    missing = [col for col in required if col not in df.columns or df[col].isna().all()]
    if missing:
        return None, missing
    
    # Get Gold and BTC prices
    gold = df['Gold']
    btc = df['BTC']
    
    # Calculate Gold-denominated values (how many oz of Gold per 1 currency unit)
    # Higher = stronger currency (can buy more Gold)
    result['Gold_USD'] = 1 / gold  # 1 USD buys X oz of Gold
    result['Gold_EUR'] = df['EURUSD'] / gold  # EUR -> USD -> Gold
    result['Gold_JPY'] = (1 / df['USDJPY']) / gold  # JPY -> USD -> Gold
    result['Gold_GBP'] = df['GBPUSD'] / gold  # GBP -> USD -> Gold
    result['Gold_CNY'] = (1 / df['USDCNY']) / gold  # CNY -> USD -> Gold
    result['Gold_CHF'] = (1 / df['USDCHF']) / gold  # CHF -> USD -> Gold
    result['Gold_AUD'] = df['AUDUSD'] / gold  # AUD -> USD -> Gold
    
    # Calculate BTC-denominated values (how many BTC per 1 currency unit)
    result['BTC_USD'] = 1 / btc
    result['BTC_EUR'] = df['EURUSD'] / btc
    result['BTC_JPY'] = (1 / df['USDJPY']) / btc
    result['BTC_GBP'] = df['GBPUSD'] / btc
    result['BTC_CNY'] = (1 / df['USDCNY']) / btc
    result['BTC_CHF'] = (1 / df['USDCHF']) / btc
    result['BTC_AUD'] = df['AUDUSD'] / btc
    
    # Gold-denominated BTC (how many oz of Gold per 1 BTC)
    result['Gold_BTC'] = btc / gold
    
    return pd.DataFrame(result), []

# Calculate Fiat Health data
fiat_health, missing_cols = calculate_fiat_health_data(df)

if fiat_health is not None and len(fiat_health) > 0:
    # Normalize to 2 years ago = 100
    lookback = min(504, len(fiat_health))  # ~2 years of trading days
    base_idx = -lookback
    
    # Create normalized DataFrames
    gold_cols = ['Gold_USD', 'Gold_EUR', 'Gold_JPY', 'Gold_GBP', 'Gold_CNY', 'Gold_CHF', 'Gold_AUD']
    btc_cols = ['BTC_USD', 'BTC_EUR', 'BTC_JPY', 'BTC_GBP', 'BTC_CNY', 'BTC_CHF', 'BTC_AUD']
    
    # Gold-denominated chart
    st.markdown(f"#### {t('fiat_gold_denominated')}")
    st.caption(t('fiat_decline_note'))
    
    gold_normalized = pd.DataFrame()
    for col in gold_cols:
        if col in fiat_health.columns:
            base_val = fiat_health[col].iloc[base_idx]
            if base_val != 0 and not pd.isna(base_val):
                gold_normalized[col.replace('Gold_', '')] = (fiat_health[col] / base_val) * 100
    
    if not gold_normalized.empty:
        st.line_chart(gold_normalized.dropna(), height=300)
        
        # Current values
        cols = st.columns(7)
        currencies = ['USD', 'EUR', 'JPY', 'GBP', 'CNY', 'CHF', 'AUD']
        for i, curr in enumerate(currencies):
            if curr in gold_normalized.columns:
                current = gold_normalized[curr].iloc[-1]
                change = current - 100
                cols[i].metric(curr, f"{current:.1f}", f"{change:+.1f}")
    
    # BTC-denominated chart
    st.markdown(f"#### {t('fiat_btc_denominated')}")
    st.caption(t('fiat_decline_note'))
    
    btc_normalized = pd.DataFrame()
    for col in btc_cols:
        if col in fiat_health.columns:
            base_val = fiat_health[col].iloc[base_idx]
            if base_val != 0 and not pd.isna(base_val):
                btc_normalized[col.replace('BTC_', '')] = (fiat_health[col] / base_val) * 100
    
    if not btc_normalized.empty:
        st.line_chart(btc_normalized.dropna(), height=300)
        
        # Current values
        cols = st.columns(7)
        for i, curr in enumerate(currencies):
            if curr in btc_normalized.columns:
                current = btc_normalized[curr].iloc[-1]
                change = current - 100
                cols[i].metric(curr, f"{current:.1f}", f"{change:+.1f}")
    
    # Gold-denominated BTC
    st.markdown(f"#### {t('fiat_gold_btc')}")
    st.caption(t('fiat_btc_gold_oz'))
    
    if 'Gold_BTC' in fiat_health.columns:
        gold_btc = fiat_health['Gold_BTC'].dropna()
        if len(gold_btc) > 0:
            current_oz = gold_btc.iloc[-1]
            base_oz = gold_btc.iloc[base_idx]
            change_pct = ((current_oz / base_oz) - 1) * 100 if base_oz != 0 else 0
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("1 BTC =", f"{current_oz:.1f} oz Gold", f"{change_pct:+.1f}% (2Y)")
            with col2:
                st.line_chart(gold_btc, height=200)
else:
    # Show which columns are missing for debugging
    if missing_cols:
        missing_str = ', '.join(missing_cols)
        st.warning(f"{t('fiat_health_no_data')} (Missing: {missing_str})")
    else:
        st.warning(t('fiat_health_no_data'))

