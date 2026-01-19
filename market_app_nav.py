# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Main Entry Point
Streamlitアプリのメインファイル
"""

import streamlit as st
import os

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Market Cockpit Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import utils after page config
from utils import (
    PAGE_TITLE,
    get_market_data,
    init_ai_clients,
    check_for_market_alerts,
    get_data_freshness_status,
    t,
    render_language_selector,
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    /* Dark theme adjustments */
    .stMetric {
        background-color: rgba(28, 131, 225, 0.1);
        padding: 10px;
        border-radius: 5px;
    }
    
    /* Back to Top Button - Always visible, CSS-only */
    .back-to-top-btn {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        text-decoration: none;
    }
    .back-to-top-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        color: white;
    }
    .back-to-top-btn svg {
        width: 24px;
        height: 24px;
    }
    /* Page top anchor */
    #page-top {
        position: absolute;
        top: 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Alert boxes */
    .alert-high {
        background-color: rgba(255, 0, 0, 0.1);
        border-left: 4px solid red;
        padding: 10px;
        margin: 5px 0;
    }
    .alert-medium {
        background-color: rgba(255, 165, 0, 0.1);
        border-left: 4px solid orange;
        padding: 10px;
        margin: 5px 0;
    }
    .alert-info {
        background-color: rgba(0, 123, 255, 0.1);
        border-left: 4px solid #007bff;
        padding: 10px;
        margin: 5px 0;
    }
</style>

<div id="page-top"></div>

<a href="#page-top" class="back-to-top-btn" title="Back to top">
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
    </svg>
</a>
""", unsafe_allow_html=True)

# ========== PAGE TITLE (MUST BE FIRST VISIBLE ELEMENT) ==========
st.title(f"📊 {PAGE_TITLE}")
st.caption(t('app_subtitle'))

# ========== INITIALIZE DATA ==========
@st.cache_data(ttl=3600, show_spinner="📊 市場データを読み込み中...")  # 1時間キャッシュ
def load_data(force_refresh=False):
    """Load market data with caching"""
    return get_market_data(_force_refresh=force_refresh)

# Check for force refresh
force_refresh = st.session_state.get('force_refresh', False)
if force_refresh:
    st.cache_data.clear()
    st.session_state['force_refresh'] = False

# Load data
df, df_original = load_data(force_refresh)

# Store in session state for page access
st.session_state['df'] = df
st.session_state['df_original'] = df_original

# ========== INITIALIZE AI CLIENTS ==========
if 'gemini_client' not in st.session_state or 'claude_client' not in st.session_state:
    gemini_client, claude_client = init_ai_clients()
    st.session_state['gemini_client'] = gemini_client
    st.session_state['claude_client'] = claude_client

# ========== SIDEBAR ==========
with st.sidebar:
    # Language Selector (TOP of sidebar)
    render_language_selector()
    
    st.caption("v2.2.0 - i18n Edition")
    
    st.divider()
    
    # Force Update Button
    if st.button(t('sidebar_force_update'), type="primary", use_container_width=True):
        st.session_state['force_refresh'] = True
        st.rerun()
    
    # CSV Download Button
    if df is not None:
        csv_data = df.to_csv()
        st.download_button(
            t('sidebar_download_csv'),
            csv_data,
            "market_cockpit_data.csv",
            "text/csv",
            key="download_csv_sidebar",
            use_container_width=True
        )
    
    # Data Freshness Status
    st.divider()
    st.subheader(t('sidebar_update_status'))
    
    if hasattr(df, 'attrs') and 'last_valid_dates' in df.attrs:
        freshness = get_data_freshness_status(
            df.attrs['last_valid_dates'],
            df.attrs.get('fred_release_dates', {})
        )
        
        col1, col2 = st.columns(2)
        col1.metric(t('sidebar_fresh'), freshness['summary']['fresh_count'])
        col2.metric(t('sidebar_stale'), freshness['summary']['stale_count'])
        
        if freshness['summary']['critical_count'] > 0:
            st.warning(t('sidebar_critical_warning', count=freshness['summary']['critical_count']))
        
        st.caption(t('sidebar_health_score', score=freshness['summary']['health_score']))
    
    # Market Alerts
    st.divider()
    st.subheader(t('sidebar_alerts'))
    
    alerts = check_for_market_alerts(df)
    if alerts:
        for alert in alerts:
            severity_class = f"alert-{alert['severity']}"
            st.markdown(f'<div class="{severity_class}">{alert["message"]}</div>', unsafe_allow_html=True)
    else:
        st.success(t('sidebar_no_alerts'))
    
    # AI Status
    st.divider()
    st.subheader(t('sidebar_ai_status'))
    
    gemini_status = t('sidebar_ready') if st.session_state.get('gemini_client') else t('sidebar_not_configured')
    claude_status = t('sidebar_ready') if st.session_state.get('claude_client') else t('sidebar_not_configured')
    
    st.caption(f"Gemini: {gemini_status}")
    st.caption(f"Claude: {claude_status}")
    
    # Footer
    st.divider()
    st.caption(t('sidebar_data_sources'))
    last_update_date = df.index[-1].strftime('%Y-%m-%d %H:%M') if len(df) > 0 else 'N/A'
    st.caption(t('sidebar_last_update', date=last_update_date))

# ========== PAGE NAVIGATION ==========
pages = {
    "📊 Liquidity & Rates": "pages/01_liquidity.py",
    "🌏 Global Money & FX": "pages/02_global_money.py",
    "📈 US Economic Data": "pages/03_us_economic.py",
    "🪙 Crypto Liquidity": "pages/04_crypto.py",
    "🤖 AI Analysis": "pages/05_ai_analysis.py",
    "🎲 Monte Carlo": "pages/06_monte_carlo.py",
    "📰 Market Voices": "pages/07_market_voices.py",
    "🎭 Market Sentiment": "pages/08_sentiment.py",
}

# Create navigation
pg = st.navigation([
    st.Page("pages/01_liquidity.py", title="📊 Liquidity & Rates", default=True),
    st.Page("pages/02_global_money.py", title="🌏 Global Money & FX"),
    st.Page("pages/03_us_economic.py", title="📈 US Economic Data"),
    st.Page("pages/04_crypto.py", title="🪙 Crypto Liquidity"),
    st.Page("pages/05_ai_analysis.py", title="🤖 AI Analysis"),
    st.Page("pages/06_monte_carlo.py", title="🎲 Monte Carlo"),
    st.Page("pages/07_market_voices.py", title="📰 Market Voices"),
    st.Page("pages/08_sentiment.py", title="🎭 Market Sentiment"),
    st.Page("pages/09_banking.py", title="🏦 Banking Sector"),
    st.Page("pages/11_analysis_lab.py", title="🧪 Market Analysis Lab"),
    st.Page("pages/12_currency_lab.py", title="💱 Currency Lab"),
])

pg.run()
