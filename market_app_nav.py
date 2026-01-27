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
    get_api_status,
    prefetch_api_indicators,
    t,
    render_language_selector,
)

# ========== GOOGLE ANALYTICS ==========
st.markdown("""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-GJ68XJ5RZK"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-GJ68XJ5RZK');
</script>
""", unsafe_allow_html=True)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    /* Main background - lighter dark theme */
    .stApp {
        background-color: #1a1a2e !important;
    }
    
    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background-color: #16213e !important;
    }
    
    /* Dark theme adjustments */
    .stMetric {
        background-color: rgba(78, 205, 196, 0.1);
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
    
    /* Navigation group headers - make them larger and more visible */
    /* Selector found via DevTools inspection */
    [data-testid="stNavSectionHeader"] {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.4rem !important;
        padding-bottom: 0.3rem !important;
        border-bottom: 1px solid rgba(78, 205, 196, 0.3) !important;
    }
    
    [data-testid="stNavSectionHeader"] span {
        color: #4ECDC4 !important;
        font-weight: 700 !important;
    }
    
    /* Alert boxes - Eye-friendly colors */
    .alert-high {
        background-color: rgba(255, 107, 107, 0.15);
        border-left: 4px solid #FF6B6B;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .alert-medium {
        background-color: rgba(255, 217, 61, 0.15);
        border-left: 4px solid #FFD93D;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .alert-info {
        background-color: rgba(78, 205, 196, 0.15);
        border-left: 4px solid #4ECDC4;
        padding: 10px;
        margin: 5px 0;
        border-radius: 4px;
    }
    
</style>

<link rel="apple-touch-icon" href="./app/static/apple-touch-icon.png">
<link rel="icon" type="image/png" href="./app/static/apple-touch-icon.png">

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
@st.cache_data(ttl=3600, show_spinner="📊 Loading market data...")  # 1 hour cache
def load_data(force_refresh=False):
    """Load market data with caching"""
    return get_market_data(_force_refresh=force_refresh)

# Check for force refresh
force_refresh = st.session_state.get('force_refresh', False)
if force_refresh:
    st.cache_data.clear()
    # Also clear disk cache
    disk_cache_file = os.path.join(os.path.dirname(__file__), '.market_data_cache.pkl')
    if os.path.exists(disk_cache_file):
        try:
            os.remove(disk_cache_file)
        except Exception:
            pass
    st.session_state['force_refresh'] = False

# Load data
df, df_original = load_data(force_refresh)

# Store in session state for page access
st.session_state['df'] = df
st.session_state['df_original'] = df_original

# ========== PREFETCH API INDICATORS ==========
# Fetch API-based indicators at startup so health check has complete status
if 'api_prefetch_done' not in st.session_state:
    with st.spinner("🔄 Checking API indicators..."):
        prefetch_api_indicators()
    st.session_state['api_prefetch_done'] = True

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
            df.attrs.get('fred_release_dates', {}),
            get_api_status()  # Include API indicator status
        )
        
        col1, col2 = st.columns(2)
        col1.metric(t('sidebar_fresh'), freshness['summary']['fresh_count'], help="🟢 Fresh")
        col2.metric(t('sidebar_stale'), freshness['summary']['stale_count'], help="🟡 Stale")
        
        # Show critical warning
        if freshness['summary']['critical_count'] > 0:
            st.warning(t('sidebar_critical_warning', count=freshness['summary']['critical_count']))
        
        # Show stale items WITH NAMES (for easy identification)
        if freshness['stale']:
            names = ', '.join(freshness['stale'][:3])  # Max 3 items for sidebar width
            suffix = f" +{len(freshness['stale'])-3}" if len(freshness['stale']) > 3 else ""
            st.caption(f"🟡 Stale: {names}{suffix}")
        
        # Show missing items WITH NAMES AND COUNT
        if freshness['missing']:
            names = ', '.join(freshness['missing'][:3])
            suffix = f" +{len(freshness['missing'])-3}" if len(freshness['missing']) > 3 else ""
            st.caption(f"⚪ Missing ({len(freshness['missing'])}): {names}{suffix}")
        
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
# 3-Group Structure: Markets / Analysis / Info & Tools
# Build navigation dict with translated group names
_nav_pages = {
    t('nav_group_markets'): [
        st.Page("pages/01_liquidity.py", title=t('page_liquidity'), default=True),
        st.Page("pages/02_global_money.py", title=t('page_global_money')),
        st.Page("pages/03_us_economic.py", title=t('page_us_economic')),
        st.Page("pages/09_banking.py", title=t('page_banking')),
        st.Page("pages/04_crypto.py", title=t('page_crypto')),
        st.Page("pages/08_sentiment.py", title=t('page_sentiment')),
        st.Page("pages/13_verdict.py", title=t('page_verdict')),
    ],
    t('nav_group_analysis'): [
        st.Page("pages/05_ai_analysis.py", title=t('page_ai_analysis')),
        st.Page("pages/11_analysis_lab.py", title=t('page_analysis_lab')),
        st.Page("pages/12_currency_lab.py", title=t('page_currency_lab')),
        st.Page("pages/06_monte_carlo.py", title=t('page_monte_carlo')),
    ],
    t('nav_group_tools'): [
        st.Page("pages/07_market_voices.py", title=t('page_market_voices')),
        st.Page("pages/99_admin.py", title=t('page_admin', '🔧 Admin')),
    ],
}
pg = st.navigation(_nav_pages)
pg.run()
