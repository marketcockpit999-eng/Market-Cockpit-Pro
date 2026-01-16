# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 4: Crypto Liquidity
ステーブルコイン、トークン化国債、RWA
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    show_metric_with_sparkline,
    get_stablecoin_data,
    get_stablecoin_historical,
    get_tokenized_treasury_data,
    EXPLANATIONS,
    DATA_FREQUENCY,
)

# Get data from session state
df = st.session_state.get('df')

if df is None:
    st.error("データが読み込まれていません。main.pyから起動してください。")
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader("🪙 Crypto Liquidity")
st.caption("💡 クリプト市場の流動性とRWA（実世界資産）トークン化の動向")

# Fetch data
stablecoin_data = get_stablecoin_data()
stablecoin_hist = get_stablecoin_historical()
treasury_data = get_tokenized_treasury_data()

# Cache crypto summary for AI tab
if stablecoin_data or treasury_data:
    crypto_cache = []
    if stablecoin_data:
        crypto_cache.append(f"Total Stablecoin Supply: ${stablecoin_data['total_supply']:.1f}B")
        for coin in stablecoin_data.get('top_coins', [])[:3]:
            delta_1d = coin['circulating'] - coin.get('prev_day', coin['circulating'])
            crypto_cache.append(f"  {coin['symbol']}: ${coin['circulating']:.1f}B (24h: {delta_1d:+.2f}B)")
    if treasury_data:
        crypto_cache.append(f"Tokenized Treasuries TVL: ${treasury_data['treasury']['total_tvl']:.2f}B")
        crypto_cache.append(f"Tokenized Gold TVL: ${treasury_data['gold']['total_tvl']:.2f}B")
    st.session_state['crypto_summary_cache'] = crypto_cache

# === Stablecoin Supply Section ===
st.markdown("### 💵 Stablecoin Supply")
st.caption("クリプト市場の「血液」- 増加 = 資金流入")

if stablecoin_data:
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        total_supply = stablecoin_data['total_supply']
        st.metric("Total Stablecoin Supply", f"${total_supply:.1f} B", help="全ステーブルコインの総供給量")
        if 'timestamp' in stablecoin_data:
            st.caption(f"🔄 提供元更新: {stablecoin_data['timestamp'][:16].replace('T', ' ')} (DeFiLlama)")
    
    with col2:
        top_coins = stablecoin_data['top_coins']
        usdt = next((c for c in top_coins if c['symbol'] == 'USDT'), None)
        if usdt:
            delta_1d = usdt['circulating'] - usdt.get('prev_day', usdt['circulating'])
            st.metric("USDT Supply", f"${usdt['circulating']:.1f} B", delta=f"{delta_1d:+.2f} B (24h)")
    
    with col3:
        usdc = next((c for c in top_coins if c['symbol'] == 'USDC'), None)
        if usdc:
            delta_1d = usdc['circulating'] - usdc.get('prev_day', usdc['circulating'])
            st.metric("USDC Supply", f"${usdc['circulating']:.1f} B", delta=f"{delta_1d:+.2f} B (24h)")
    
    # Historical Chart
    st.markdown("#### 📈 Stablecoin Supply History")
    if stablecoin_hist is not None and not stablecoin_hist.empty:
        col_short, col_long = st.columns(2)
        with col_short:
            st.markdown("##### 短期 (90日)")
            recent_90d = stablecoin_hist.tail(90)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=recent_90d.index, y=recent_90d['Total'], 
                                    mode='lines', fill='tozeroy', 
                                    line=dict(color='#26a69a'), name='Total'))
            fig.update_layout(template='plotly_dark', height=250, 
                             title='Total Stablecoin Supply (90d)',
                             yaxis_title='Supply ($B)', showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="stbl_short")
        
        with col_long:
            st.markdown("##### 長期 (全期間)")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=stablecoin_hist.index, y=stablecoin_hist['Total'], 
                                    mode='lines', fill='tozeroy', 
                                    line=dict(color='#42a5f5'), name='Total'))
            fig.update_layout(template='plotly_dark', height=250, 
                             title='Total Stablecoin Supply (All Time)',
                             yaxis_title='Supply ($B)', showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="stbl_long")
    
    # Top Stablecoins Table
    st.markdown("#### Top 10 Stablecoins by Supply")
    top_10 = stablecoin_data['top_coins'][:10]
    
    stablecoin_df = pd.DataFrame([
        {
            'Symbol': coin['symbol'],
            'Name': coin['name'],
            'Supply ($B)': round(coin['circulating'], 2),
            'Mechanism': coin['mechanism'],
            '24h Δ': round(coin['circulating'] - coin.get('prev_day', coin['circulating']), 3),
            '7d Δ': round(coin['circulating'] - coin.get('prev_week', coin['circulating']), 3),
        }
        for coin in top_10
    ])
    st.dataframe(stablecoin_df, use_container_width=True, hide_index=True)
    
    # Pie Chart
    st.markdown("#### Supply Distribution")
    fig = go.Figure(data=[
        go.Pie(
            labels=[c['symbol'] for c in top_10[:6]] + ['Others'],
            values=[c['circulating'] for c in top_10[:6]] + [sum(c['circulating'] for c in top_10[6:])],
            hole=0.4,
            marker=dict(colors=['#26a69a', '#42a5f5', '#7e57c2', '#ff7043', '#78909c', '#ab47bc', '#bdbdbd'])
        )
    ])
    fig.update_layout(template='plotly_dark', height=350, showlegend=True, legend=dict(orientation='h', y=-0.1))
    st.plotly_chart(fig, use_container_width=True, key="stablecoin_pie")
    
    st.caption(f"📅 最終更新: {stablecoin_data['timestamp'][:19]}")
else:
    st.warning("⚠️ ステーブルコインデータの取得に失敗しました。")

st.markdown("---")

# === Tokenized Treasury Section ===
if treasury_data:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📜 Tokenized Treasuries")
        st.metric("Treasury TVL", f"${treasury_data['treasury']['total_tvl']:.2f} B", help="トークン化米国債")
    with col2:
        st.markdown("### 🪙 Tokenized Gold")
        st.metric("Gold TVL", f"${treasury_data['gold']['total_tvl']:.2f} B", help="トークン化金")
    with col3:
        st.markdown("### 🏢 Other RWA")
        st.metric("Other RWA TVL", f"${treasury_data['other_rwa']['total_tvl']:.2f} B", help="その他実世界資産")
    
    if 'timestamp' in treasury_data:
        st.caption(f"🔄 提供元更新: {treasury_data['timestamp'][:16].replace('T', ' ')} (DeFiLlama)")
    
    # Treasury Protocols
    st.markdown("---")
    st.markdown("#### 📜 Tokenized US Treasuries")
    treasury_protocols = treasury_data['treasury']['protocols']
    if treasury_protocols:
        treasury_df = pd.DataFrame([
            {
                'Protocol': p['name'],
                'Symbol': p.get('symbol', '-'),
                'TVL ($B)': round(p.get('tvl') or 0, 3),
                '24h Δ (%)': round(p.get('change_1d') or 0, 2),
                '7d Δ (%)': round(p.get('change_7d') or 0, 2),
            }
            for p in treasury_protocols
        ])
        st.dataframe(treasury_df, use_container_width=True, hide_index=True)
        
        fig = go.Figure(data=[
            go.Bar(x=[p['name'][:15] for p in treasury_protocols[:8]], y=[p['tvl'] for p in treasury_protocols[:8]], marker_color='steelblue')
        ])
        fig.update_layout(template='plotly_dark', height=250, xaxis_title="Protocol", yaxis_title="TVL ($B)")
        st.plotly_chart(fig, use_container_width=True, key="treasury_bar")
    
    # Gold Protocols
    st.markdown("---")
    st.markdown("#### 🪙 Tokenized Gold")
    gold_protocols = treasury_data['gold']['protocols']
    if gold_protocols:
        gold_df = pd.DataFrame([
            {'Protocol': p['name'], 'Symbol': p.get('symbol', '-'), 'TVL ($B)': round(p['tvl'], 3)}
            for p in gold_protocols
        ])
        st.dataframe(gold_df, use_container_width=True, hide_index=True)
    
    # Other RWA
    with st.expander("🏢 Other RWA Protocols"):
        other_protocols = treasury_data['other_rwa']['protocols']
        if other_protocols:
            other_df = pd.DataFrame([
                {'Protocol': p['name'], 'Symbol': p.get('symbol', '-'), 'TVL ($B)': round(p['tvl'], 3)}
                for p in other_protocols
            ])
            st.dataframe(other_df, use_container_width=True, hide_index=True)
    
    st.caption(f"📅 最終更新: {treasury_data['timestamp'][:19]}")
else:
    st.warning("⚠️ RWAデータの取得に失敗しました。")

# === Market Depth Section ===
st.markdown("---")
st.subheader("💧 Market Depth (Liquidity Quality)")
st.caption("Centralized (CEX) vs Decentralized (DEX) Liquidity Cost")

import requests

@st.cache_data(ttl=300)
def fetch_btc_depth():
    # CEX: Bitcoin
    cex_url = "https://api.coingecko.com/api/v3/coins/bitcoin/tickers?include_exchange_logo=false&depth=false"
    # DEX: Wrapped Bitcoin
    dex_url = "https://api.coingecko.com/api/v3/coins/wrapped-bitcoin/tickers?include_exchange_logo=false&depth=false"
    
    data = []
    
    try:
        # Fetch CEX
        r_cex = requests.get(cex_url, timeout=5).json()
        tickers = r_cex.get('tickers', [])
        # Filter top exchanges
        targets = ['Binance', 'Coinbase Exchange', 'Kraken', 'Bybit', 'Bitfinex']
        for t in tickers:
            market = t['market']['name']
            if market in targets and t['target'] in ['USDT', 'USD']:
                spread = t.get('bid_ask_spread_percentage')
                if spread:
                    data.append({'Type': 'CEX', 'Market': market, 'Spread (%)': spread})
                    
        # Fetch DEX
        r_dex = requests.get(dex_url, timeout=5).json()
        tickers = r_dex.get('tickers', [])
        # Filter Uniswap/Curve
        for t in tickers:
            market = t['market']['name']
            if ('Uniswap' in market or 'Curve' in market) and t['target'] in ['USDT', 'USDC', 'DAI', 'WETH']:
                spread = t.get('bid_ask_spread_percentage')
                if spread:
                     data.append({'Type': 'DEX', 'Market': market, 'Spread (%)': spread})
    except:
        pass
        
    return pd.DataFrame(data)

depth_df = fetch_btc_depth()
if not depth_df.empty and 'Spread (%)' in depth_df.columns:
    # Aggregation
    cex_rows = depth_df[depth_df['Type']=='CEX']
    dex_rows = depth_df[depth_df['Type']=='DEX']
    
    avg_cex = cex_rows['Spread (%)'].mean() if not cex_rows.empty else 0
    avg_dex = dex_rows['Spread (%)'].mean() if not dex_rows.empty else 0
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Avg CEX Spread", f"{avg_cex:.4f}%", help="Binance, Coinbase, Kraken...")
        if avg_cex > 0:
            st.metric("Avg DEX Spread", f"{avg_dex:.4f}%", delta=f"{(avg_dex/avg_cex):.1f}x Higher Cost", delta_color="inverse", help="Uniswap, Curve (WBTC)")
        else:
             st.metric("Avg DEX Spread", f"{avg_dex:.4f}%")
    
    with col2:
        # Bar chart
        fig = go.Figure()
        # CEX Bar
        cex_sorted = cex_rows.sort_values('Spread (%)')
        fig.add_trace(go.Bar(x=cex_sorted['Market'], y=cex_sorted['Spread (%)'], name='CEX', marker_color='#00e676'))
        # DEX Bar
        dex_sorted = dex_rows.sort_values('Spread (%)').head(5) # Limit to top 5 DEX pools
        fig.add_trace(go.Bar(x=dex_sorted['Market'], y=dex_sorted['Spread (%)'], name='DEX', marker_color='#ff1744'))
        
        fig.update_layout(title="Bid-Ask Spread (%) Comparison", template='plotly_dark', height=300)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Market Depth data unavailable (CoinGecko API limit or timeout)")

st.info("""
💡 **なぜこれが重要？**
- **ステーブルコイン**: クリプト市場への資金流入/流出を測定
- **トークン化国債**: 機関投資家の参入度合い
- **トークン化金**: 伝統的安全資産のデジタル化
""")
