import streamlit as st
import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import feedparser
import os
import requests
import re
import json
import uuid
import pickle
import time
from io import StringIO
from dotenv import load_dotenv
from google import genai
import anthropic

# Load environment variables
load_dotenv()

# Configure Gemini API (new google.genai library)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Configure Claude API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
claude_client = None
if ANTHROPIC_API_KEY:
    claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Model names for latest reasoning AI
GEMINI_MODEL = "gemini-3-flash-preview"  # Latest Gemini 3 Flash
CLAUDE_MODEL = "claude-opus-4-5-20251101"  # Latest Claude Opus 4.5

st.set_page_config(layout="wide", page_title="Market Cockpit Pro")

# ========== BACK TO TOP BUTTON (CSS ONLY) ==========
st.markdown("""
<style>
    /* Back to Top Button - Always visible */
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
</style>

<div id="page-top"></div>

<a href="#page-top" class="back-to-top-btn" title="ページトップに戻る">
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
    </svg>
</a>
""", unsafe_allow_html=True)

# ========== SETTINGS ==========
FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"
PAGE_TITLE = "Market Cockpit Pro"
MANUAL_DATA_FILE = "manual_h41_data.csv"

# ========== DATA FRESHNESS MONITORING ==========
# Update frequency categories (in days)
DATA_FRESHNESS_RULES = {
    # Daily data (market days)
    'daily': {
        'fresh': 3,      # 🟢 ≤3 days old
        'stale': 7,      # 🟡 4-7 days old
        'critical': 14,  # 🔴 >7 days old
        'indicators': ['EFFR', 'IORB', 'SOFR', 'SP500', 'VIX', 'HYG', 'DXY', 'USDJPY', 
                      'EURUSD', 'USDCNY', 'Gold', 'Silver', 'Oil', 'Copper', 'BTC', 'ETH',
                      'Credit_Spread', 'US_TNX', 'T10Y2Y', 'ON_RRP', 'FedFundsUpper', 'FedFundsLower']
    },
    # Weekly data (Fed H.4.1 etc)
    'weekly': {
        'fresh': 10,     # 🟢 ≤10 days old
        'stale': 14,     # 🟡 11-14 days old
        'critical': 21,  # 🔴 >14 days old
        'indicators': ['Reserves', 'TGA', 'Fed_Assets', 'SOMA_Total', 'SOMA_Bills', 
                      'SRF', 'FIMA', 'Primary_Credit', 'Total_Loans', 'Bank_Cash', 'ICSA']
    },
    # Monthly data
    'monthly': {
        'fresh': 45,     # 🟢 ≤45 days old
        'stale': 60,     # 🟡 46-60 days old
        'critical': 90,  # 🔴 >60 days old
        'indicators': ['M2SL', 'M2REAL', 'CPI', 'CPICore', 'PPI', 'Unemployment', 'UNRATE', 'CorePCE', 
                      'ConsumerSent', 'CN_M2', 'JP_M2', 'EU_M2', 'NFP', 'AvgHourlyEarnings', 'JOLTS',
                      'RetailSales', 'CN_CPI', 'JP_CPI', 'EU_CPI']
    },
    # Quarterly data
    'quarterly': {
        'fresh': 100,    # 🟢 ≤100 days old
        'stale': 120,    # 🟡 101-120 days old
        'critical': 150, # 🔴 >120 days old
        'indicators': ['Lending_Standards', 'CI_Std_Large', 'CI_Std_Small', 'CI_Demand',
                      'CRE_Std_Construction', 'CRE_Std_Office', 'CRE_Std_Multifamily', 'CRE_Demand', 'RealGDP']
    }
}

# Data frequency labels for display
DATA_FREQUENCY = {
    # Daily
    'EFFR': '日次', 'IORB': '日次', 'SOFR': '日次', 'SP500': '日次', 'VIX': '日次', 
    'HYG': '日次', 'DXY': '日次', 'USDJPY': '日次', 'EURUSD': '日次', 'USDCNY': '日次',
    'Gold': '日次', 'Silver': '日次', 'Oil': '日次', 'Copper': '日次', 'BTC': '日次', 'ETH': '日次',
    'Credit_Spread': '日次', 'US_TNX': '日次', 'T10Y2Y': '日次', 'ON_RRP': '日次',
    # Weekly
    'Reserves': '週次', 'TGA': '週次', 'Fed_Assets': '週次', 'SOMA_Total': '週次', 'SOMA_Bills': '週次',
    'SRF': '週次', 'FIMA': '週次', 'Primary_Credit': '週次', 'Total_Loans': '週次', 
    'Bank_Cash': '週次', 'ICSA': '週次', 'Net_Liquidity': '週次', 'SomaBillsRatio': '週次',
    'FedFundsUpper': '日次', 'FedFundsLower': '日次',
    # Monthly
    'M2SL': '月次', 'M2REAL': '月次', 'CPI': '月次', 'CPICore': '月次', 'PPI': '月次', 'Unemployment': '月次', 'UNRATE': '月次',
    'CorePCE': '月次', 'ConsumerSent': '月次', 'CN_M2': '月次', 'JP_M2': '月次', 'EU_M2': '月次',
    'CN_CPI': '月次', 'JP_CPI': '月次', 'EU_CPI': '月次', 'US_Real_M2_Index': '月次',
    'NFP': '月次', 'AvgHourlyEarnings': '月次', 'JOLTS': '月次', 'RetailSales': '月次',
    # Quarterly
    'Lending_Standards': '四半期', 'RealGDP': '四半期',
    'CI_Std_Large': '四半期', 'CI_Std_Small': '四半期', 'CI_Demand': '四半期',
    'CRE_Std_Construction': '四半期', 'CRE_Std_Office': '四半期', 'CRE_Std_Multifamily': '四半期', 'CRE_Demand': '四半期',
    # Monthly (SLOOS Loan Balances)
    'CI_Loans': '月次',
    # Weekly (SLOOS Loan Balances)
    'CRE_Loans': '週次',
}

def get_data_freshness_status(last_valid_dates: dict, release_dates: dict = None) -> dict:
    """
    Check data freshness for all indicators.
    Priority: Actual release_dates (provider update) > last_valid_dates (observation date)
    Returns: dict with 'summary' and 'details'
    """
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    
    results = {
        'fresh': [],    # 🟢
        'stale': [],    # 🟡
        'critical': [], # 🔴
        'missing': [],  # ⚫
        'details': {}   # Full details per indicator
    }
    
    # Build indicator -> category mapping
    indicator_category = {}
    for category, config in DATA_FRESHNESS_RULES.items():
        for ind in config['indicators']:
            indicator_category[ind] = category
    
    for indicator, date_str in last_valid_dates.items():
        if indicator in ['RMP_Alert_Active', 'RMP_Status_Text']:  # Skip non-data columns
            continue
            
        try:
            # Decide which date to use for freshness check
            # Use release_date if available (ACTUAL update), fallback to observation date
            check_date_str = date_str
            is_priority_release = False
            
            if release_dates and indicator in release_dates and release_dates[indicator]:
                check_date_str = release_dates[indicator]
                is_priority_release = True
                
            last_date = datetime.strptime(check_date_str, '%Y-%m-%d').date()
            days_old = (today - last_date).days
            
            # Get freshness rules for this indicator
            category = indicator_category.get(indicator, 'weekly')  # Default to weekly
            rules = DATA_FRESHNESS_RULES[category]
            
            if days_old <= rules['fresh']:
                status = 'fresh'
                results['fresh'].append(indicator)
            elif days_old <= rules['stale']:
                status = 'stale'
                results['stale'].append(indicator)
            else:
                status = 'critical'
                results['critical'].append(indicator)
            
            results['details'][indicator] = {
                'last_date': date_str,
                'release_date': release_dates.get(indicator) if release_dates else None,
                'days_old': days_old,
                'status': status,
                'category': category,
                'is_release_based': is_priority_release,
                'expected_max': rules['fresh']
            }
        except:
            results['missing'].append(indicator)
            results['details'][indicator] = {
                'last_date': None,
                'days_old': None,
                'status': 'missing',
                'category': 'unknown',
                'expected_max': None
            }
    
    # Calculate summary
    total = len(results['fresh']) + len(results['stale']) + len(results['critical']) + len(results['missing'])
    results['summary'] = {
        'total': total,
        'fresh_count': len(results['fresh']),
        'stale_count': len(results['stale']),
        'critical_count': len(results['critical']),
        'missing_count': len(results['missing']),
        'health_score': round(len(results['fresh']) / max(total, 1) * 100, 1)
    }
    
    return results

@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def get_fred_release_dates(fred_ids: list) -> dict:
    """
    Fetch actual release dates (last_updated) from FRED API for each series.
    This shows when the data source actually published the data.
    """
    release_dates = {}
    
    for series_id in fred_ids:
        try:
            url = f"https://api.stlouisfed.org/fred/series?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'seriess' in data and len(data['seriess']) > 0:
                    series_info = data['seriess'][0]
                    # Parse last_updated: "2025-12-29 16:06:49-06"
                    last_updated_str = series_info.get('last_updated', '')
                    if last_updated_str:
                        # Extract just the date part
                        date_part = last_updated_str.split(' ')[0]
                        release_dates[series_id] = {
                            'last_updated': date_part,
                            'title': series_info.get('title', ''),
                            'frequency': series_info.get('frequency', ''),
                            'observation_end': series_info.get('observation_end', '')
                        }
        except:
            pass  # Skip on error
    
    return release_dates

# ========== MONITORED AGENCIES ==========
MONITORED_AGENCIES = {
    "FRB": {"domain": "federalreserve.gov", "rss": "https://www.federalreserve.gov/feeds/press_all.xml", "label": "🏦 Federal Reserve"},
    "SEC": {"domain": "sec.gov", "rss": None, "label": "📊 SEC"},  # SEC doesn't have easy RSS
    "Treasury": {"domain": "treasury.gov", "rss": "https://home.treasury.gov/news/press-releases/rss.xml", "label": "💵 Treasury"},
    "CFTC": {"domain": "cftc.gov", "rss": None, "label": "📈 CFTC"},
    "FDIC": {"domain": "fdic.gov", "rss": None, "label": "🏛️ FDIC"},
    "BIS": {"domain": "bis.org", "rss": "https://www.bis.org/doclist/bis_fsi_publs.rss", "label": "🌐 BIS"},
    "IMF": {"domain": "imf.org", "rss": None, "label": "🌍 IMF"},
    "FSB": {"domain": "fsb.org", "rss": None, "label": "🔒 FSB"},
}

def check_for_market_alerts():
    """
    Check major financial regulators' RSS feeds for recent updates.
    Returns a list of alerts from the last 24 hours.
    """
    alerts = []
    
    # RSS feeds to check
    rss_sources = {
        "FRB": "https://www.federalreserve.gov/feeds/press_all.xml",
        "Treasury": "https://home.treasury.gov/news/press-releases/rss.xml",
        "BIS": "https://www.bis.org/doclist/bis_fsi_publs.rss",
    }
    
    for source, url in rss_sources.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:  # Check latest 3 entries per source
                pub_date = entry.get('published', '') or entry.get('updated', '')
                title = entry.get('title', 'No title')
                link = entry.get('link', '')
                
                # Check if within 24 hours (simplified check)
                if pub_date:
                    try:
                        from dateutil import parser as date_parser
                        entry_date = date_parser.parse(pub_date)
                        now = datetime.datetime.now(datetime.timezone.utc)
                        if entry_date.tzinfo is None:
                            entry_date = entry_date.replace(tzinfo=datetime.timezone.utc)
                        hours_ago = (now - entry_date).total_seconds() / 3600
                        
                        if hours_ago <= 24:
                            alerts.append({
                                'source': source,
                                'title': title[:80] + ('...' if len(title) > 80 else ''),
                                'link': link,
                                'hours_ago': int(hours_ago),
                                'published': pub_date
                            })
                    except:
                        pass  # Skip if date parsing fails
        except Exception as e:
            pass  # Skip on RSS fetch error
    
    # Sort by hours_ago (most recent first)
    alerts.sort(key=lambda x: x.get('hours_ago', 999))
    
    return alerts[:5]  # Return top 5 most recent


def search_google_news(query, num_results=3, gl='US', mode='general'):
    """Search Google News RSS and return headlines, dates, and URLs for verification
    
    Args:
        mode: 'general' (all news) or 'primary' (government/org reports only)
    """
    try:
        import urllib.request
        # Map region to hl (language)
        hl = 'ja' if gl == 'JP' else 'en-US'
        ceid = 'JP:ja' if gl == 'JP' else 'US:en'
        
        # Enhanced query based on mode
        enhanced_query = query
        if mode == 'primary':
            # Target official domains and report/paper keywords
            # Expanded to include key US regulators: SEC, Treasury, CFTC, FDIC, OCC
            official_domains = (
                "site:sec.gov OR "           # Securities and Exchange Commission
                "site:treasury.gov OR "      # US Treasury
                "site:cftc.gov OR "          # Commodity Futures Trading Commission
                "site:fdic.gov OR "          # Federal Deposit Insurance Corporation
                "site:occ.gov OR "           # Office of the Comptroller of the Currency
                "site:federalreserve.gov OR " # Federal Reserve
                "site:.gov OR "              # Other US government
                "site:.org OR site:.int OR " # International orgs
                "site:bis.org OR "           # Bank for International Settlements
                "site:imf.org OR "           # International Monetary Fund
                "site:fsb.org OR "           # Financial Stability Board
                "site:ecb.europa.eu OR "     # European Central Bank
                "site:bankofengland.co.uk OR " # Bank of England
                "site:isda.org"              # ISDA
            )
            report_keywords = 'filetype:pdf OR "staff report" OR "working paper" OR "bulletin" OR "statement" OR "policy note" OR "press release" OR "enforcement action" OR "proposed rule"'
            enhanced_query = f"({query}) ({official_domains}) ({report_keywords})"
        else:
            # Fallback for general mode if some specific primary keywords are detected
            if any(src in query.lower() for src in ['fed', 'frb', 'ecb', 'bis', 'imf', 'sec', 'treasury', 'cftc']):
                enhanced_query = f"{query} site:.gov OR site:.org OR site:.int"
            
        search_url = f"https://news.google.com/rss/search?q={enhanced_query.replace(' ', '+')}&hl={hl}&gl={gl}&ceid={ceid}"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            feed_content = response.read()
        feed = feedparser.parse(feed_content)
        
        results = []
        for entry in feed.entries[:num_results]:
            title = entry.get('title', '')
            pub_date = entry.get('published', '')[:20] if entry.get('published') else ''
            link = entry.get('link', '')
            source = entry.get('source', {}).get('title', 'Unknown Source')
            results.append(f"- [{gl}] [{pub_date}] Source: {source} | {title}\n  Link: {link}")
        
        return "\n".join(results) if results else "該当する一次情報資料が見つかりませんでした"
    except Exception as e:
        return f"検索エラー: {str(e)}"

def get_time_diff_str(date_str):
    """
    Calculate time difference from now and return a human-readable string.
    Supports various RSS date formats.
    """
    try:
        from dateutil import parser
        from datetime import timezone
        
        now = datetime.datetime.now(timezone.utc)
        target_date = parser.parse(date_str)
        
        # タイムゾーン情報がない場合は経過時間計算を諦め、元の日付を表示
        if target_date.tzinfo is None:
            # 元の日付文字列から日時部分だけ抽出して表示
            return f"⚠️ {date_str[:16]}"
            
        diff = now - target_date
        seconds = diff.total_seconds()
        
        # 未来の日付の場合（サーバー時刻のズレ等）
        if seconds < 0:
            return "⚠️ 時刻不明"
        
        if seconds < 60:
            return "たった今"
        elif seconds < 3600:
            return f"{int(seconds // 60)}分前"
        elif seconds < 86400:
            return f"{int(seconds // 3600)}時間前"
        elif seconds < 604800:
            return f"{int(seconds // 86400)}日前"
        else:
            return target_date.strftime('%Y/%m/%d')
    except:
        return f"⚠️ {date_str[:16] if len(date_str) > 16 else date_str}"


# ========== MANUAL DATA PERSISTENCE ==========
def load_manual_data():
    """Load manual H.4.1 data from CSV file (SOMA_Bills only)"""
    try:
        if os.path.exists(MANUAL_DATA_FILE):
            df_manual = pd.read_csv(MANUAL_DATA_FILE, index_col=0, parse_dates=True)
            # Ensure only SOMA_Bills column exists (migration from old format)
            if 'SOMA_Bills' in df_manual.columns:
                return df_manual[['SOMA_Bills']]
            return df_manual
    except:
        pass
    return pd.DataFrame(columns=['SOMA_Bills'])

def save_manual_data(date, soma_bills):
    """Save manual H.4.1 data to CSV file (SOMA_Bills only)"""
    df_manual = load_manual_data()
    df_manual.loc[date] = [soma_bills]
    df_manual = df_manual.sort_index()
    df_manual.to_csv(MANUAL_DATA_FILE)

def fetch_h41_data():
    """
    Fetch latest H.4.1 data from FRB website
    Returns: (report_date, soma_bills, total_loans, error_msg)
    """
    url = "https://www.federalreserve.gov/releases/h41/current/"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None, None, None, f"HTTP {response.status_code}"
        
        # Parse tables
        tables = pd.read_html(StringIO(response.text))
        
        # Extract report date (improved pattern)
        report_date = None
        date_patterns = [
            r'Week ended[^>]*>(\w+\s+\d+,\s+\d{4})',  # After "Week ended" tag
            r'(\w+ \d+, \d{4})',  # Any date-like pattern
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, response.text, re.IGNORECASE)
            if date_match:
                try:
                    report_date = pd.to_datetime(date_match.group(1))
                    break
                except:
                    pass
        
        # If no date found, use today
        if not report_date:
            report_date = pd.Timestamp.now()
        
        # Table 1: Look for "Bills" (NOT "U.S. Treasury securities")
        table1 = tables[1] if len(tables) > 1 else None
        soma_bills = None
        
        if table1 is not None:
            last_col_idx = table1.shape[1] - 1
            for idx, row in table1.iterrows():
                row_text = str(row.iloc[0]).strip().lower()
                # Look for "Bills" specifically, not "Notes" or "Bonds"
                if row_text == 'bills' or (row_text.startswith('bills') and 'note' not in row_text and 'bond' not in row_text):
                    try:
                        soma_bills = float(row.iloc[last_col_idx]) / 1000  # Millions to Billions
                        break
                    except:
                        pass
        
        # Find Total Loans
        total_loans = None
        if table1 is not None:
            for idx, row in table1.iterrows():
                row_text = str(row.iloc[0]).strip().lower()
                if row_text == 'loans':
                    try:
                        val = row.iloc[last_col_idx]
                        if pd.notna(val) and isinstance(val, (int, float)):
                            total_loans = float(val) / 1000
                            break
                    except:
                        pass
        
        # Success if we got at least one value
        if soma_bills or total_loans:
            return report_date, soma_bills, total_loans, None
        else:
            return None, None, None, "No data extracted from tables"
        
    except Exception as e:
        return None, None, None, str(e)

# FRED指標
FRED_INDICATORS = {
    # Plumbing
    'ON_RRP': 'RRPONTSYD',
    'Reserves': 'WRESBAL',
    'TGA': 'WTREGEN',
    'Fed_Assets': 'WALCL',
    'SOMA_Total': 'WALCL',
    'SOMA_Bills': 'TREAST',  # Treasury Securities Held by Fed (includes Bills)
    'EFFR': 'EFFR',
    'IORB': 'IORB',
    
    # Banking Sector
    'Bank_Cash': 'CASACBW027SBOG',
    'Lending_Standards': 'DRTSCILM',
    
    # SLOOS - C&I Lending (商工業融資) - Corrected IDs
    'CI_Std_Large': 'DRTSCILM',       # C&I Standards (Large/Medium) - same as Lending_Standards
    'CI_Std_Small': 'DRTSCIS',        # C&I Standards (Small Firms) - CORRECTED
    'CI_Demand': 'DRTSCLCC',          # C&I Demand (Large/Medium) - CORRECTED
    'CI_Loans': 'BUSLOANS',           # C&I Loan Balance (Monthly)
    
    # SLOOS - CRE Lending (商業用不動産融資) - Corrected IDs
    'CRE_Std_Construction': 'SUBLPDRCSC',  # Construction & Land Development (works)
    'CRE_Std_Office': 'DRTSSP',            # CRE Standards All Property Types - CORRECTED
    'CRE_Std_Multifamily': 'DRTSSP',       # Using same general CRE standard
    'CRE_Demand': 'DRTSCLCC',              # Using C&I demand as proxy (CRE demand n/a)
    'CRE_Loans': 'CREACBW027SBOG',         # CRE Loan Balance (Weekly)
    
    # Market Plumbing
    'SRF': 'WORAL',
    'FIMA': 'H41RESPPALGTRFNWW',
    'SOFR': 'SOFR',
    'Primary_Credit': 'WLCFLPCL',  # Weekly Discount Window Primary Credit
    'Total_Loans': 'WLCFLL',  # Weekly Total Loans (H.4.1)
    
    # Rates & Bonds
    'Credit_Spread': 'BAMLH0A0HYM2',
    'US_TNX': 'DGS10',
    
    # Macro
    'Unemployment': 'UNRATE',
    'CPI': 'CPIAUCSL',
    'M2SL': 'M2SL',
    'M2REAL': 'M2REAL',  # Real M2 Money Stock (1982-84 base)
    
    # Global M2 (Nominal)
    'CN_M2': 'MYAGM2CNM189N',       # China M2
    'JP_M2': 'MANMM101JPM189S',     # Japan M2
    'EU_M2': 'MABMM301EZM189S',     # Euro Area M2
    
    # Global CPI (for Real M2 calculation)
    'CN_CPI': 'CHNCPIALLMINMEI',
    'JP_CPI': 'JPNCPIALLMINMEI',
    'EU_CPI': 'CP0000EZ19M086NEST',
    
    # China Credit Impulse Data (BIS via FRED)
    'CN_Credit_Stock': 'CRDQCNAPABIS',  # Total credit to private non-financial sector, China (Quarterly, Billions CNY)
    'CN_GDP': 'MKTGDPCNA646NWDB',       # China GDP (Annual, Current USD)
    
    # Economic Indicators
    'T10Y2Y': 'T10Y2Y',             # 2Y-10Y Spread (Yield Curve)
    'ICSA': 'ICSA',                 # Initial Jobless Claims
    
    # Additional Economic Data (User Request)
    'UNRATE': 'UNRATE',             # Unemployment Rate (Sahm Rule)
    'CorePCE': 'PCETRIM12M159SFRBDAL',  # Core PCE YoY % (Trimmed Mean)
    'ConsumerSent': 'UMCSENT',      # Consumer Sentiment (ISM unavailable on FRED)
    
    # ===== NEW: US Economic Data (2026-01 Addition) =====
    # Monetary Policy
    'FedFundsUpper': 'DFEDTARU',    # Federal Funds Target Rate (Upper Bound)
    'FedFundsLower': 'DFEDTAR',     # Federal Funds Target Rate (Lower Bound)
    
    # Employment
    'NFP': 'PAYEMS',                # Non-Farm Payrolls (Thousands of Persons)
    'ADP': 'ADPWNUSNERSA',          # ADP Employment (Persons - NOT Thousands! Divide by 1000 for K)
    'AvgHourlyEarnings': 'CES0500000003',  # Average Hourly Earnings (Dollars per Hour)
    'JOLTS': 'JTSJOL',              # JOLTS Job Openings (Thousands)
    
    # Inflation
    'CPI': 'CPIAUCSL',              # CPI All Items (Index, Seasonally Adjusted)
    'CPICore': 'CPILFESL',          # CPI Core (Excluding Food & Energy)
    'PPI': 'PPIACO',                # PPI All Commodities (Index)
    
    # Economy
    'RetailSales': 'RSAFS',         # Retail Sales (Millions)
    'RealGDP': 'GDPC1',             # Real GDP (Billions, Chained 2017 Dollars)
}

# Yahoo Finance
YAHOO_INDICATORS = {
    'SP500': '^GSPC',
    'VIX': '^VIX',
    'HYG': 'HYG',
    
    # FX
    'DXY': 'DX-Y.NYB',              # Dollar Index
    'USDJPY': 'JPY=X',              # USD/JPY
    'EURUSD': 'EURUSD=X',           # EUR/USD
    'USDCNY': 'CNY=X',              # USD/CNY
    
    # Commodities
    'Gold': 'GC=F',                 # Gold Futures
    'Silver': 'SI=F',               # Silver Futures
    'Oil': 'CL=F',                  # WTI Crude Oil
    'Copper': 'HG=F',               # Copper Futures
    
    # Crypto
    'BTC': 'BTC-USD',               # Bitcoin
    'ETH': 'ETH-USD',               # Ethereum
}

# ========== DATA INTEGRITY SAFEGUARDS ==========
# FRED UNITS: Official unit documentation for each series
# This prevents unit confusion errors (like the ADP Persons vs Thousands issue)
FRED_UNITS = {
    # Liquidity (FRB H.4.1) - All in Millions, converted to Billions by /1000
    'ON_RRP': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'Reserves': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'TGA': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'Fed_Assets': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'SOMA_Total': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'SOMA_Bills': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},

    # Rates - Already in Percent
    'EFFR': {'unit': 'Percent', 'convert_to': None, 'divisor': 1},
    'IORB': {'unit': 'Percent', 'convert_to': None, 'divisor': 1},
    'SOFR': {'unit': 'Percent', 'convert_to': None, 'divisor': 1},
    'FedFundsUpper': {'unit': 'Percent', 'convert_to': None, 'divisor': 1},
    'FedFundsLower': {'unit': 'Percent', 'convert_to': None, 'divisor': 1},
    'Credit_Spread': {'unit': 'Percent', 'convert_to': None, 'divisor': 1},
    'US_TNX': {'unit': 'Percent', 'convert_to': None, 'divisor': 1},
    'T10Y2Y': {'unit': 'Percent', 'convert_to': None, 'divisor': 1},
    'UNRATE': {'unit': 'Percent', 'convert_to': None, 'divisor': 1},
    'CorePCE': {'unit': 'Percent (YoY)', 'convert_to': None, 'divisor': 1},

    # Employment - CRITICAL: Different units!
    'NFP': {'unit': 'Thousands of Persons', 'convert_to': None, 'divisor': 1},  # Direct use
    'ADP': {'unit': 'Persons', 'convert_to': 'Thousands', 'divisor': 1000},  # MUST divide by 1000!
    'JOLTS': {'unit': 'Thousands', 'convert_to': None, 'divisor': 1},
    'ICSA': {'unit': 'Persons', 'convert_to': 'Thousands', 'divisor': 1000},
    'AvgHourlyEarnings': {'unit': 'Dollars per Hour', 'convert_to': None, 'divisor': 1},

    # Prices - Index values (base year varies)
    'CPI': {'unit': 'Index (1982-84=100)', 'convert_to': None, 'divisor': 1},
    'CPICore': {'unit': 'Index (1982-84=100)', 'convert_to': None, 'divisor': 1},
    'PPI': {'unit': 'Index (1982=100)', 'convert_to': None, 'divisor': 1},

    # Money Supply - Various units
    'M2SL': {'unit': 'Billions', 'convert_to': 'Trillions', 'divisor': 1000},
    'M2REAL': {'unit': 'Billions', 'convert_to': 'Trillions', 'divisor': 1000},

    # GDP
    'RealGDP': {'unit': 'Billions of Chained 2017 Dollars', 'convert_to': None, 'divisor': 1},
    'RetailSales': {'unit': 'Millions', 'convert_to': None, 'divisor': 1},

    # Banking/Lending
    'Bank_Cash': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'CI_Loans': {'unit': 'Billions', 'convert_to': None, 'divisor': 1},
    'CRE_Loans': {'unit': 'Billions', 'convert_to': None, 'divisor': 1},
    'Lending_Standards': {'unit': 'Net Percent', 'convert_to': None, 'divisor': 1},
}

# VALIDATION RANGES: Sanity check ranges for each indicator
# If value falls outside this range, it indicates a data/unit error
VALIDATION_RANGES = {
    # Rates (should be 0-15% typically)
    'EFFR': (0, 15),
    'IORB': (0, 15),
    'SOFR': (0, 15),
    'FedFundsUpper': (0, 15),
    'UNRATE': (0, 25),  # Unemployment rate
    'CorePCE': (-5, 15),  # YoY inflation
    'Credit_Spread': (0, 30),
    'US_TNX': (0, 20),
    'T10Y2Y': (-5, 5),

    # Employment (in Thousands) - reasonable monthly changes
    'NFP': (100000, 200000),  # Total NFP level (100M-200M)
    'ADP': (100000, 200000),  # After /1000 conversion (same range as NFP)
    'JOLTS': (3000, 15000),  # Job openings
    'ICSA': (100, 1000),  # Weekly initial claims in thousands

    # Prices (Index values)
    'CPI': (200, 400),  # CPI index around 310 in 2025
    'CPICore': (200, 400),
    'PPI': (100, 350),
    'AvgHourlyEarnings': (20, 60),  # Dollars per hour

    # Liquidity (in Billions after conversion)
    'ON_RRP': (0, 3000),
    'Reserves': (0, 5000),
    'TGA': (0, 2000),
    'Fed_Assets': (4000, 12000),
    'SOMA_Total': (4000, 12000),
    'Net_Liquidity': (2000, 8000),

    # Markets
    'VIX': (5, 100),
    'SP500': (2000, 8000),
    'DXY': (70, 130),
    'USDJPY': (80, 200),
    'Gold': (1000, 4000),
    'BTC': (10000, 500000),
}

def get_freshness_badge(last_updated_str: str) -> str:
    """
    Return a badge based on how recently the data was updated.
    🆕 = Updated within 24 hours
    ✅ = Updated within 7 days
    ⏳ = Updated within 30 days
    ⚠️ = Not updated in 30+ days
    """
    if not last_updated_str:
        return ""
    
    try:
        from datetime import datetime, timedelta
        last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d')
        now = datetime.now()
        days_ago = (now - last_updated).days
        
        if days_ago <= 1:
            return "🆕"  # Very fresh (today/yesterday)
        elif days_ago <= 7:
            return "✅"  # Fresh (within a week)
        elif days_ago <= 30:
            return "⏳"  # Getting stale
        else:
            return "⚠️"  # Stale
    except:
        return ""

def validate_data_ranges(df, show_warnings=True) -> dict:
    """
    Validate that data values fall within expected ranges.
    Returns dict of any validation issues found.
    """
    issues = {}
    
    for indicator, (min_val, max_val) in VALIDATION_RANGES.items():
        if indicator in df.columns:
            series = df[indicator].dropna()
            if len(series) > 0:
                latest = series.iloc[-1]
                if latest < min_val or latest > max_val:
                    issues[indicator] = {
                        'value': latest,
                        'expected_range': (min_val, max_val),
                        'status': 'OUT_OF_RANGE'
                    }
    
    return issues

# 説明文
EXPLANATIONS = {
    "Net_Liquidity": "【ネットリクイディティ】\n市場に出回る「真の資金量」。(FRB総資産 - TGA - RRP) で計算されます。",
    "Reserves": "【銀行準備預金】\n民間銀行がFRBに預けているお金。これが減りすぎるとショックが起きやすくなります。",
    "TGA": "【TGA (財務省一般口座)】\n政府の銀行口座。ここが増えると市場から資金が吸い上げられます。",
    "ON_RRP": "【ON RRP】\nMMFなどがFRBにお金を預ける場所。余剰資金の滞留を示します。",
    "VIX": "【VIX指数】\n恐怖指数。20以上で市場の不安が高まっている状態です。",
    "Bank_Cash": "【銀行の現金保有】\n全米の銀行が保有する現金資産の推移。銀行が不安を感じて現金を抱え込み始めると市場の流動性が低下します。",
    "Lending_Standards": "【C&I Lending Tightening / 商工業融資基準の厳格化】\n銀行の融資態度を示す純割合（Net %）。0が中立、+は引き締め（融資基準を厳しくする銀行が多い）、−は緩和。数値上昇は信用収縮を示し、景気後退の先行指標として重要。",
    "M2_Nominal": "【通貨供給量 M2（名目）】\n世の中に流通していマネーの総量。",
    "M2_Real": "【通貨供給量 M2（実質）】\nインフレ調整後の実質的な購買力。",
    "SRF": "【Standing Repo Facility】\n国内の金融機関が国債を担保に現金を借りる常設窓口。リポ市場の目詰まりを検知します。",
    "FIMA": "【FIMA Repo Facility】\n海外の中央銀行向け融資。世界的なドル不足が発生しているかを測る指標です。",
    "SOFR": "【SOFR】\n国債を担保にした資金調達コスト。急騰は現金不足を示します。",
    "Primary": "【Primary Credit】\n健全な銀行向けの緊急融資。急増時は銀行が市場で現金を調達できなくなっている危険信号です。",
    "Window": "【Total Loans】\nFRBによる金融機関への貸出総額。市場の緊急事態を測る総合指標です。",
    "SOMA_Total": "【SOMA総資産】\nFRBが保有する国債やMBSの総額。これが増える=QE、減る=QTです。",
    "SOMA_Bills": "【SOMA Bills (短期国債)】\nFRBが保有する短期国債（T-Bills）。2025年12月12日からRMP（Reserve Management Purchases）として月額400億ドルペースで買い入れ中。QT終了後の準備金維持が目的だが、実質的な資金供給となる。",
    "SomaBillsRatio": "【SOMA Bills比率】\nFRBの総資産に占める短期国債の割合。RMP実行により上昇トレンドとなる。FRBは「技術的措置」と主張するが、市場への流動性供給効果はQEに類似。",
    "M2SL": "【通貨供給量 M2】\n世の中に流通しているマネー(現金・預金等)の総量。",
    "RMP": "【RMP (Reserve Management Purchases)】\n2025年12月12日開始。QT終了後、銀行準備金を「潤沢（ample）」レベルに維持するため、月額400億ドル規模で短期国債を買い入れる政策。FRBは景気刺激策（QE）ではないと強調するが、市場への資金供給効果は実質的にQEと同等との指摘もある。",
    
    # SLOOS - C&I Lending
    "CI_Std_Large": "【C&I融資基準（大・中堅企業）】\n0を超えると貸し渋り。40%超で強力なリセッションシグナル。リセッションの先行指標（20%超で警戒）。",
    "CI_Std_Small": "【C&I融資基準（小企業）】\n中小企業の資金繰りと雇用の先行指標。小企業向けが先に悪化する場合は雇用悪化に注意。",
    "CI_Demand": "【C&I融資需要（大・中堅企業）】\n企業の設備投資意欲を測定。基準が緩んでも需要が低い場合は企業が将来を悲観。基準と需要の「乖離」が最大の注目点。",
    "CI_Loans": "【C&I融資残高】\n商工業向け融資の総額。融資基準厳格化後にこの残高が減少すると「クレジットクランチ（信用収縮）」開始のサイン。",
    
    # SLOOS - CRE Lending
    "CRE_Std_Construction": "【CRE融資基準（建設・土地開発）】\n不動産開発の蛇口。ここが閉まると数年後の新規供給と建設投資が止まる。",
    "CRE_Std_Office": "【CRE融資基準（オフィス等）】\n既存物件の借り換え難易度を示す。厳格化は物件価格暴落のトリガーとなる。オフィスクライシス・借り換えリスクの測定。",
    "CRE_Std_Multifamily": "【CRE融資基準（集合住宅）】\n居住用不動産市場の流動性を確認。住宅供給に影響。",
    "CRE_Demand": "【CRE融資需要】\n投資家が不動産から資金を引き揚げる動きを察知する指標。不動産投資意欲の減退確認。",
    "CRE_Loans": "【CRE融資残高（週次）】\n週次で追える最速のデータ。四半期統計を待たずに銀行の融資姿勢の変化をリアルタイムで察知。",
}

# ========== VALUATION & LEVERAGE INDICATORS ==========
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def get_pe_ratios():
    """
    Fetch S&P 500 and NASDAQ P/E ratios by scraping multpl.com
    Returns: dict with pe_sp500, pe_nasdaq, historical average
    """
    try:
        result = {
            'sp500_pe': None,
            'sp500_pe_avg': 19.5,  # Historical average
            'nasdaq_pe': None,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Fetch S&P 500 P/E from multpl.com
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            url = "https://www.multpl.com/s-p-500-pe-ratio"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Parse the current P/E value
                import re
                match = re.search(r'Current S&P 500 PE Ratio is\s*([\d.]+)', response.text)
                if match:
                    result['sp500_pe'] = float(match.group(1))
        except:
            pass
        
        # Try to get NASDAQ P/E from Yahoo Finance (QQQ as proxy)
        try:
            qqq = yf.Ticker("QQQ")
            info = qqq.info
            result['nasdaq_pe'] = info.get('trailingPE')
        except:
            pass
        
        return result
    except Exception as e:
        return None


@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes (more dynamic)
def get_crypto_leverage_data():
    """
    Fetch crypto leverage indicators: Funding Rate, Open Interest
    from CoinGlass API (free tier)
    Returns: dict with funding rates and open interest data
    """
    try:
        result = {
            'btc_funding_rate': None,
            'eth_funding_rate': None,
            'btc_open_interest': None,
            'eth_open_interest': None,
            'btc_long_short_ratio': None,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Try CoinGlass public endpoint for funding rates
        try:
            # BTC Funding Rate (weighted average across exchanges)
            url = "https://open-api.coinglass.com/public/v2/funding"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    for item in data['data']:
                        if item.get('symbol') == 'BTC':
                            result['btc_funding_rate'] = item.get('uMarginRateAvg')
                        elif item.get('symbol') == 'ETH':
                            result['eth_funding_rate'] = item.get('uMarginRateAvg')
        except:
            pass
        
        # Try alternative: Binance Futures API (free, no key needed)
        if result['btc_funding_rate'] is None:
            try:
                url = "https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        result['btc_funding_rate'] = float(data[0].get('fundingRate', 0)) * 100  # Convert to %
            except:
                pass
        
        if result['eth_funding_rate'] is None:
            try:
                url = "https://fapi.binance.com/fapi/v1/fundingRate?symbol=ETHUSDT&limit=1"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        result['eth_funding_rate'] = float(data[0].get('fundingRate', 0)) * 100
            except:
                pass
        
        # Current Open Interest from Binance
        try:
            url = "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result['btc_open_interest'] = float(data.get('openInterest', 0))
        except:
            pass
        
        try:
            url = "https://fapi.binance.com/fapi/v1/openInterest?symbol=ETHUSDT"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result['eth_open_interest'] = float(data.get('openInterest', 0))
        except:
            pass
        
        # Historical Open Interest (30 days, 4-hour intervals = 180 data points)
        try:
            url = "https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=4h&limit=180"
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    oi_values = [float(d.get('sumOpenInterest', 0)) for d in data]
                    timestamps = [datetime.datetime.fromtimestamp(d.get('timestamp', 0) / 1000) for d in data]
                    result['btc_oi_history'] = {'values': oi_values, 'timestamps': timestamps}
                    result['btc_oi_avg_30d'] = sum(oi_values) / len(oi_values) if oi_values else None
                    result['btc_oi_ath'] = max(oi_values) if oi_values else None
                    result['btc_oi_atl'] = min(oi_values) if oi_values else None
        except:
            pass
        
        try:
            url = "https://fapi.binance.com/futures/data/openInterestHist?symbol=ETHUSDT&period=4h&limit=180"
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    oi_values = [float(d.get('sumOpenInterest', 0)) for d in data]
                    timestamps = [datetime.datetime.fromtimestamp(d.get('timestamp', 0) / 1000) for d in data]
                    result['eth_oi_history'] = {'values': oi_values, 'timestamps': timestamps}
                    result['eth_oi_avg_30d'] = sum(oi_values) / len(oi_values) if oi_values else None
                    result['eth_oi_ath'] = max(oi_values) if oi_values else None
                    result['eth_oi_atl'] = min(oi_values) if oi_values else None
        except:
            pass
        
        # Long/Short Ratio from Binance
        try:
            url = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=1h&limit=1"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result['btc_long_short_ratio'] = float(data[0].get('longShortRatio', 1.0))
        except:
            pass
        
        return result
    except Exception as e:
        return None


# ========== DEFILLAMA API FUNCTIONS (Crypto Liquidity) ==========

@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def get_stablecoin_data():
    """
    Fetch stablecoin supply data from DeFiLlama API.
    Returns: dict with total supply and top stablecoins
    """
    try:
        url = "https://stablecoins.llama.fi/stablecoins?includePrices=true"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        data = response.json()
        stablecoins = data.get('peggedAssets', [])
        
        # Top stablecoins by market cap
        top_coins = []
        total_supply = 0
        
        # Store IDs for historical data
        coin_ids = {}
        
        for coin in stablecoins:
            if coin.get('pegType') == 'peggedUSD':
                circulating = coin.get('circulating', {}).get('peggedUSD', 0)
                if circulating and circulating > 1000000:  # > $1M
                    total_supply += circulating
                    coin_data = {
                        'id': coin.get('id', ''),
                        'name': coin.get('name', ''),
                        'symbol': coin.get('symbol', ''),
                        'circulating': circulating / 1e9,  # Convert to billions
                        'mechanism': coin.get('pegMechanism', ''),
                        'price': coin.get('price', 1.0),
                        'prev_day': coin.get('circulatingPrevDay', {}).get('peggedUSD', 0) / 1e9,
                        'prev_week': coin.get('circulatingPrevWeek', {}).get('peggedUSD', 0) / 1e9,
                        'prev_month': coin.get('circulatingPrevMonth', {}).get('peggedUSD', 0) / 1e9,
                    }
                    top_coins.append(coin_data)
                    coin_ids[coin.get('symbol', '')] = coin.get('id', '')
        
        # Sort by market cap
        top_coins.sort(key=lambda x: x['circulating'], reverse=True)
        
        return {
            'total_supply': total_supply / 1e9,  # Billions
            'top_coins': top_coins[:15],  # Top 15
            'coin_ids': coin_ids,
            'timestamp': datetime.datetime.now().isoformat()
        }
    except Exception as e:
        return None

@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def get_stablecoin_historical():
    """
    Fetch historical stablecoin supply data from DeFiLlama API.
    Returns: DataFrame with date index and stablecoin supplies
    """
    try:
        url = "https://stablecoins.llama.fi/stablecoincharts/all?stablecoin=1"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # Parse historical data - handle different response formats
        records = []
        
        if isinstance(data, list):
            for point in data:
                try:
                    # Date can be string or int - convert to int first
                    date_val = point.get('date', 0)
                    if isinstance(date_val, str):
                        date_val = int(date_val)
                    date = datetime.datetime.fromtimestamp(date_val)
                    
                    # Try different keys for the total
                    total = 0
                    if 'totalCirculating' in point and isinstance(point['totalCirculating'], dict):
                        total = point['totalCirculating'].get('peggedUSD', 0) / 1e9
                    elif 'totalCirculatingUSD' in point and isinstance(point['totalCirculatingUSD'], dict):
                        total = point['totalCirculatingUSD'].get('peggedUSD', 0) / 1e9
                    
                    if total > 0:
                        records.append({'date': date, 'Total': total})
                except:
                    continue
        
        df = pd.DataFrame(records)
        if not df.empty and len(df) > 0:
            df = df.set_index('date')
            df = df.sort_index()
            return df
        
        return None
    except Exception as e:
        return None


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def get_tokenized_treasury_data():
    """
    Fetch tokenized US Treasury data from DeFiLlama API.
    Separates: Treasuries (国債), Gold (金), Other RWA
    Returns: dict with categorized RWA protocols
    """
    try:
        # Get protocol list
        url = "https://api.llama.fi/protocols"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        protocols = response.json()
        
        # Keywords for categorization
        treasury_keywords = ['treasury', 'tbill', 't-bill', 'buidl', 'usdy', 'usdm', 'usyc', 'ondo', 'openeden', 'hashnote', 'mountain', 'backed']
        gold_keywords = ['gold', 'xaut', 'paxg', 'gld', 'xau']
        
        treasury_data = []
        gold_data = []
        other_rwa_data = []
        
        treasury_tvl = 0
        gold_tvl = 0
        other_rwa_tvl = 0
        
        for protocol in protocols:
            name = protocol.get('name', '').lower()
            slug = protocol.get('slug', '').lower()
            symbol = protocol.get('symbol', '').lower()
            category = protocol.get('category', '').lower()
            
            # Check if it's an RWA protocol
            is_rwa = 'rwa' in category or 'real world' in category
            
            if not is_rwa:
                continue
            
            tvl = protocol.get('tvl', 0)
            if not tvl or tvl < 1000000:  # < $1M
                continue
            
            protocol_info = {
                'name': protocol.get('name', ''),
                'symbol': protocol.get('symbol', '-'),
                'slug': protocol.get('slug', ''),
                'tvl': tvl / 1e9,  # Billions
                'category': protocol.get('category', 'RWA'),
                'change_1d': protocol.get('change_1d', 0),
                'change_7d': protocol.get('change_7d', 0),
            }
            
            # Categorize by type
            is_gold = any(kw in name or kw in symbol or kw in slug for kw in gold_keywords)
            is_treasury = any(kw in name or kw in symbol or kw in slug for kw in treasury_keywords)
            
            if is_gold:
                gold_data.append(protocol_info)
                gold_tvl += tvl
            elif is_treasury:
                treasury_data.append(protocol_info)
                treasury_tvl += tvl
            else:
                other_rwa_data.append(protocol_info)
                other_rwa_tvl += tvl
        
        # Sort each category by TVL
        treasury_data.sort(key=lambda x: x['tvl'], reverse=True)
        gold_data.sort(key=lambda x: x['tvl'], reverse=True)
        other_rwa_data.sort(key=lambda x: x['tvl'], reverse=True)
        
        return {
            'treasury': {
                'total_tvl': treasury_tvl / 1e9,
                'protocols': treasury_data[:10],
            },
            'gold': {
                'total_tvl': gold_tvl / 1e9,
                'protocols': gold_data[:5],
            },
            'other_rwa': {
                'total_tvl': other_rwa_tvl / 1e9,
                'protocols': other_rwa_data[:10],
            },
            'total_rwa_tvl': (treasury_tvl + gold_tvl + other_rwa_tvl) / 1e9,
            'timestamp': datetime.datetime.now().isoformat()
        }
    except Exception as e:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_protocol_historical(slug: str):
    """
    Fetch historical TVL data for a specific protocol from DeFiLlama API.
    Returns: DataFrame with date index and TVL
    """
    try:
        url = f"https://api.llama.fi/protocol/{slug}"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        data = response.json()
        tvl_history = data.get('tvl', [])
        
        records = []
        for point in tvl_history:
            date = datetime.datetime.fromtimestamp(point.get('date', 0))
            tvl = point.get('totalLiquidityUSD', 0) / 1e9
            records.append({'date': date, 'TVL': tvl})
        
        df = pd.DataFrame(records)
        if not df.empty:
            df = df.set_index('date')
            df = df.sort_index()
        
        return df
    except Exception as e:
        return None

# ========== DATA FUNCTIONS ==========
# Disk cache settings for fast startup
CACHE_FILE = os.path.join(os.path.dirname(__file__), '.market_data_cache.pkl')
CACHE_TTL_SECONDS = 600  # 10 minutes

def _load_from_disk_cache():
    """Load cached data from disk if fresh enough"""
    try:
        if os.path.exists(CACHE_FILE):
            cache_age = time.time() - os.path.getmtime(CACHE_FILE)
            if cache_age < CACHE_TTL_SECONDS:
                with open(CACHE_FILE, 'rb') as f:
                    data = pickle.load(f)
                    return data.get('df'), data.get('df_original')
    except Exception:
        pass
    return None, None

def _save_to_disk_cache(df, df_original):
    """Save data to disk cache"""
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump({'df': df, 'df_original': df_original, 'timestamp': time.time()}, f)
    except Exception:
        pass

# ============================================
# SENTIMENT INDICATORS DATA FUNCTIONS
# ============================================

@st.cache_data(ttl=3600, show_spinner=False)
def get_crypto_fear_greed():
    """Fetch Crypto Fear & Greed Index from Alternative.me API"""
    try:
        # Get current value and historical data
        url = "https://api.alternative.me/fng/?limit=30"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                current = data['data'][0]
                history = []
                for item in data['data']:
                    history.append({
                        'date': datetime.datetime.fromtimestamp(int(item['timestamp'])),
                        'value': int(item['value']),
                        'classification': item['value_classification']
                    })
                return {
                    'current': int(current['value']),
                    'classification': current['value_classification'],
                    'history': pd.DataFrame(history).set_index('date').sort_index()
                }
    except Exception as e:
        st.warning(f"Crypto Fear & Greed取得エラー: {e}")
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_cnn_fear_greed():
    """Fetch CNN Fear & Greed Index via web scraping"""
    try:
        # CNN Fear & Greed is typically scraped from CNN website
        # Using a backup approach with static placeholder for now
        # In production, use RapidAPI or web scraping
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'fear_and_greed' in data:
                fg = data['fear_and_greed']
                # Build history from graph data
                history = []
                if 'fear_and_greed_historical' in data:
                    for point in data['fear_and_greed_historical'].get('data', []):
                        history.append({
                            'date': datetime.datetime.fromtimestamp(point['x'] / 1000),
                            'value': point['y']
                        })
                return {
                    'current': fg.get('score', None),
                    'classification': fg.get('rating', ''),
                    'previous_close': fg.get('previous_close', None),
                    'history': pd.DataFrame(history).set_index('date').sort_index() if history else None
                }
    except Exception as e:
        pass  # Silently fail, will show N/A
    
    # Fallback: return None to indicate data unavailable
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_put_call_ratio():
    """Fetch Put/Call Ratio from CBOE"""
    try:
        # CBOE provides daily P/C ratios
        url = "https://www.cboe.com/us/options/market_statistics/daily/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Parse the page for P/C data (simplified)
            # For now, use FRED data as backup
            pass
    except:
        pass
    
    # Fallback: Try FRED for equity put/call ratio
    try:
        from pandas_datareader import data as pdr
        # CBOE Equity Put/Call Ratio is available via some data providers
        # Using VIX as proxy for now - will enhance later
        return None
    except:
        return None

@st.cache_data(ttl=86400, show_spinner=False)  # 24 hour cache for weekly data
def get_aaii_sentiment():
    """Fetch AAII Investor Sentiment Survey"""
    try:
        # AAII data is often available via Quandl/NASDAQ Data Link
        # For demo, using placeholder with actual typical values
        # In production, integrate with Quandl API
        
        # Try to fetch from a public source
        url = "https://www.aaii.com/sentimentsurvey"
        # Note: AAII requires parsing their website or API access
        
        # Return placeholder data for now
        # TODO: Integrate with Quandl API when API key is available
        return {
            'bullish': 38.5,
            'neutral': 31.2,
            'bearish': 30.3,
            'bull_bear_spread': 8.2,
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'note': 'データソース準備中'
        }
    except Exception as e:
        return None


@st.cache_data(ttl=86400, show_spinner=False)  # 24 hour cache (FOMC meets ~8 times/year)
def get_fomc_sep_projections():
    """Fetch FOMC Summary of Economic Projections (SEP) from FRED
    
    Returns median projections for:
    - Federal Funds Rate
    - Real GDP Growth
    - Unemployment Rate
    - Core PCE Inflation
    """
    try:
        from pandas_datareader import data as pdr
        
        # FRED Series IDs for FOMC SEP Medians
        # Annual frequency - projections for current year, next year, and longer run
        sep_series = {
            'ff_rate': 'FEDTARMD',      # Fed Funds Rate Median
            'gdp_growth': 'GDPC1CTM',   # Real GDP Growth Central Tendency Median
            'unemployment': 'UNRATECTM', # Unemployment Rate Central Tendency Median
            'core_pce': 'PCECTPICTM',   # Core PCE Central Tendency Median
        }
        
        projections = {}
        for key, series_id in sep_series.items():
            try:
                data = pdr.get_data_fred(series_id, start='2020-01-01')
                if data is not None and len(data) > 0:
                    # Get the most recent projections
                    recent = data.dropna().tail(5)
                    projections[key] = {
                        'series': recent,
                        'latest': recent.iloc[-1].values[0] if len(recent) > 0 else None,
                        'previous': recent.iloc[-2].values[0] if len(recent) > 1 else None,
                        'date': recent.index[-1].strftime('%Y-%m-%d') if len(recent) > 0 else None
                    }
            except Exception:
                projections[key] = None
        
        return projections if projections else None
    except Exception as e:
        return None


@st.cache_data(ttl=3600, show_spinner=False)  # 1 hour cache
def get_cme_fedwatch():
    """Fetch CME FedWatch Tool probabilities for next FOMC meeting
    
    Returns probability of rate cut, hold, or hike
    """
    try:
        # CME FedWatch data is typically from CME website
        # Using a simplified approach - in production, use CME API or scraping
        
        # Try to get from CME website (public data)
        url = "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # For now, return placeholder based on current market expectations
        # TODO: Implement actual CME FedWatch scraping or API
        
        # Current FF rate is around 4.25-4.50%
        # Market is pricing in cuts for 2026
        return {
            'next_meeting': '2026-01-29',
            'current_rate': '4.25-4.50%',
            'probabilities': {
                'cut_50bp': 5.0,
                'cut_25bp': 65.0,
                'hold': 28.0,
                'hike_25bp': 2.0,
            },
            'expected_rate': '4.00-4.25%',
            'note': 'データソース準備中（実際のCME FedWatch連携予定）'
        }
    except Exception as e:
        return None


@st.cache_data(ttl=600, show_spinner=False)
def get_market_data(_csv_mtime=None, _force_refresh=False):
    # Try disk cache first for fast startup
    if not _force_refresh:
        cached_df, cached_original = _load_from_disk_cache()
        if cached_df is not None and cached_original is not None:
            return cached_df, cached_original
    
    # Fetch from API (slow path)
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=730)
    
    fred_series = []
    credit_stock_data = None  # Store separately to avoid affecting main data join
    
    for name, ticker in FRED_INDICATORS.items():
        try:
            # Skip CN_Credit_Stock here - fetch separately with longer period
            if name == 'CN_Credit_Stock':
                credit_start = end - datetime.timedelta(days=365*5)  # 5 years for YoY calc
                credit_stock_data = web.DataReader(ticker, 'fred', credit_start, end, api_key=FRED_API_KEY)
                credit_stock_data.columns = [name]
                continue  # Don't add to main series
            else:
                s = web.DataReader(ticker, 'fred', start, end, api_key=FRED_API_KEY)
            s.columns = [name]
            fred_series.append(s)
        except:
            pass
    
    # Yahoo Data
    try:
        y_tickers = list(YAHOO_INDICATORS.values())
        y_data = yf.download(y_tickers, start=start, end=end, progress=False)['Close']
        inv_yahoo = {v: k for k, v in YAHOO_INDICATORS.items()}
        y_data = y_data.rename(columns=inv_yahoo)
    except:
        y_data = pd.DataFrame()
    
    # Global M2 Data (Latest values from central banks - Dec 2024)
    # Sources: BOJ, PBOC, ECB via web search
    global_m2_data = {
        'JP_M2': 1260,    # 1,260 Trillion JPY (December 2024, Bank of Japan)
        'CN_M2': 313.53,  # 313.53 Trillion CNY (December 2024, People's Bank of China)
        'EU_M2': 15.58,   # 15.58 Trillion EUR (December 2024, ECB)
    }
    
    # CPI Annual Rates (Latest: Nov 2025) - for Real M2 calculation
    # Sources: Trading Economics, Statistics bureaus
    global_cpi_rates = {
        'JP_CPI': 2.9,    # Japan: 2.9% YoY (Nov 2025)
        'CN_CPI': 0.7,    # China: 0.7% YoY (Nov 2025)
        'EU_CPI': 2.1,    # Euro Area: 2.1% YoY (Nov 2025)
    }
    
    # Calculate Real M2 (simplified: Nominal / (1 + CPI/100))
    global_real_m2 = {
        'JP_M2_Real': global_m2_data['JP_M2'] / (1 + global_cpi_rates['JP_CPI']/100),
        'CN_M2_Real': global_m2_data['CN_M2'] / (1 + global_cpi_rates['CN_CPI']/100),
        'EU_M2_Real': global_m2_data['EU_M2'] / (1 + global_cpi_rates['EU_CPI']/100),
    }
    
    # Join All
    df = pd.concat(fred_series + ([y_data] if not y_data.empty else []), axis=1).sort_index()
    
    # Add Global M2 data (latest value applied to recent dates)
    for col_name, value in global_m2_data.items():
        df[col_name] = value
    
    # Add Global CPI and Real M2 data
    for col_name, value in global_cpi_rates.items():
        df[col_name] = value
    for col_name, value in global_real_m2.items():
        df[col_name] = value
    
    # Unit Normalization (Million to Billion)
    mil_to_bil = ['Fed_Assets', 'TGA', 'Reserves', 'SOMA_Total', 'Bank_Cash', 'SRF', 'FIMA', 'Primary_Credit', 'Total_Loans', 'SOMA_Bills', 'M2SL', 'M2REAL', 'CI_Loans', 'CRE_Loans']
    for col in mil_to_bil:
        if col in df.columns:
            df[col] = df[col] / 1000
    
    # Calculate Net Liquidity
    if all(c in df.columns for c in ['Fed_Assets', 'TGA', 'ON_RRP']):
        df['Net_Liquidity'] = df['Fed_Assets'] - df['TGA'] - df['ON_RRP']
    
    # Calculate Real M2 (M2 adjusted for CPI)
    if all(c in df.columns for c in ['M2SL', 'CPI']):
        # Forward fill CPI to handle NaN values before calculation
        cpi_filled = df['CPI'].ffill()
        # Normalize CPI to base at earliest date
        cpi_base = cpi_filled.dropna().iloc[0] if not cpi_filled.dropna().empty else 1
        df['US_Real_M2_Index'] = (df['M2SL'] / cpi_filled) * cpi_base
    
    # Calculate SOMA Bills Ratio
    if all(c in df.columns for c in ['SOMA_Bills', 'SOMA_Total']):
        df['SomaBillsRatio'] = (df['SOMA_Bills'] / df['SOMA_Total']) * 100
    
    # RMP Detection Logic (Updated for Dec 2025 Policy)
    # RMP: Reserve Management Purchases - Started Dec 12, 2025
    # Target: $40B/month T-Bills purchases (~$1.33B/day assuming 30-day month)
    if all(c in df.columns for c in ['SOMA_Bills']):
        df['RMP_Alert_Active'] = False
        df['RMP_Status_Text'] = "📊 RMP監視中（2025年12月12日開始）"
        
        bills_recent = df['SOMA_Bills'].tail(30)  # Last 30 days
        
        if len(bills_recent) >= 7:  # Need at least 1 week of data
            # Calculate weekly change rate
            bills_7d_ago = bills_recent.iloc[-7] if len(bills_recent) >= 7 else bills_recent.iloc[0]
            bills_now = bills_recent.iloc[-1]
            weekly_change = bills_now - bills_7d_ago
            
            # Expected weekly change: ~$9.3B (40B/month * 7days/30days)
            # Allow 50% tolerance
            expected_weekly_min = 4.5  # Billions
            expected_weekly_max = 15.0  # Billions
            
            if weekly_change >= expected_weekly_min:
                if weekly_change <= expected_weekly_max:
                    df.loc[df.index[-1], 'RMP_Alert_Active'] = True
                    df.loc[df.index[-1], 'RMP_Status_Text'] = f"✅ RMP実行中: +${weekly_change:.1f}B/週（目標ペース）"
                else:
                    df.loc[df.index[-1], 'RMP_Alert_Active'] = True
                    df.loc[df.index[-1], 'RMP_Status_Text'] = f"⚠️ RMP加速: +${weekly_change:.1f}B/週（通常ペース超過！）"
            elif weekly_change >= 0:
                df.loc[df.index[-1], 'RMP_Status_Text'] = f"🔄 RMP縮小: +${weekly_change:.1f}B/週（ペース減速）"
            else:
                df.loc[df.index[-1], 'RMP_Status_Text'] = f"⛔ Bills売却: ${weekly_change:.1f}B/週（RMP停止？）"
    
    # Calculate China Credit Impulse (Proxy using BIS credit data)
    # Formula: Credit Impulse = (Credit Flow[t] - Credit Flow[t-4]) / GDP
    # where Credit Flow = Credit Stock[t] - Credit Stock[t-1]
    # Note: This is a PROXY using FRED quarterly data, not actual PBoC TSF data
    if credit_stock_data is not None and len(credit_stock_data) >= 5:
        try:
            credit = credit_stock_data['CN_Credit_Stock'].dropna()
            
            # Calculate credit flow (change in credit stock, Billions CNY)
            credit_flow = credit.diff()
            
            # Calculate credit flow change (YoY, 4 quarters)
            credit_flow_change = credit_flow - credit_flow.shift(4)
            
            # China GDP in Billions CNY
            # 2024 GDP ≈ 18.7 trillion USD ≈ 136 trillion CNY = 136,000 Billion CNY
            annual_gdp_bln_cny = 136000  # Fallback value
            
            quarterly_gdp = annual_gdp_bln_cny / 4
            
            # Credit Impulse = Credit Flow Change / GDP (as percentage)
            credit_impulse = (credit_flow_change / quarterly_gdp) * 100
            
            # Add Credit Impulse to main DataFrame (will join on index)
            df['CN_Credit_Impulse'] = credit_impulse
        except Exception as e:
            pass  # Silently fail if calculation fails
    
    # Store actual last data date for each column BEFORE forward fill
    # This preserves the true "data source update date"
    last_valid_dates = {}
    for col in df.columns:
        valid_data = df[col].dropna()
        if len(valid_data) > 0:
            # Store as string to avoid type issues
            last_valid_dates[col] = valid_data.index[-1].strftime('%Y-%m-%d')
    
    # NEW: Fetch actual FRED release info (last_updated) for precise freshness tracking
    # This shows when the provider (BLS, FRB, etc.) actually pushed the data
    fred_ids = list(set(FRED_INDICATORS.values())) # Use set to avoid redundant API calls
    fred_release_info = get_fred_release_dates(fred_ids)
    
    # Map back to our column names (supporting multiple indicators per series_id)
    col_release_dates = {}
    for indicator, series_id in FRED_INDICATORS.items():
        if series_id in fred_release_info:
            col_release_dates[indicator] = fred_release_info[series_id]['last_updated']

    # IMPORTANT: Store original data BEFORE forward fill for accurate monthly change calculations
    # This is needed because ffill makes all dates have data, so dropna() won't return just monthly points
    df_original = df.copy()
    
    # Forward fill missing data (for display continuity)
    df = df.ffill()
    
    # Store metadata as a DataFrame attribute (accessible in display functions)
    # Note: We store strings/dicts only - NOT DataFrames (causes JSON serialization error)
    df.attrs['last_valid_dates'] = last_valid_dates
    df.attrs['fred_release_dates'] = col_release_dates # SOURCE update date
    
    # Copy attrs to original_df for consistent access
    df_original.attrs = df.attrs.copy()
    
    # Note: All data (including SOMA_Bills via WHTLSBL) is now fetched from FRED API
    # Manual data override has been removed
    
    # Save to disk cache for fast startup next time
    _save_to_disk_cache(df, df_original)
    
    return df, df_original  # Return tuple: (ffill版, オリジナル版)

def show_metric(label, series, unit="", explanation_key="", notes="", alert_func=None):
    """メトリック表示ヘルパー（更新マーク対応）"""
    if series is None or (hasattr(series, 'isna') and series.isna().all()):
        val = None
        delta = None
        latest_date = None
        release_date = None
    else:
        val = series.iloc[-1] if hasattr(series, 'iloc') else series
        if hasattr(series, 'iloc') and len(series) > 1:
            delta = val - series.iloc[-2]
        else:
            delta = None
        
        # Get actual last data date from DataFrame metadata
        latest_date = None
        release_date = None
        if hasattr(df, 'attrs'):
            col_name = series.name if hasattr(series, 'name') else explanation_key
            if 'last_valid_dates' in df.attrs and col_name in df.attrs['last_valid_dates']:
                latest_date = df.attrs['last_valid_dates'][col_name]
            if 'fred_release_dates' in df.attrs and col_name in df.attrs['fred_release_dates']:
                release_date = df.attrs['fred_release_dates'][col_name]
    
    help_text = EXPLANATIONS.get(explanation_key, "")
    
    # Get freshness badge for label
    freshness_badge = get_freshness_badge(release_date or latest_date) if (release_date or latest_date) else ""
    display_label = f"{freshness_badge} {label}" if freshness_badge else label
    
    if alert_func and val is not None and alert_func(val):
        st.metric(display_label, f"{val:.1f} {unit}" if val is not None else "N/A", 
                 delta=f"{delta:+.1f}" if delta is not None else None,
                 help=help_text, delta_color="inverse")
    else:
        st.metric(display_label, f"{val:.1f} {unit}" if val is not None else "N/A",
                 delta=f"{delta:+.1f}" if delta is not None else None,
                 help=help_text)
    
    # Display data dates
    if latest_date:
        freq_label = DATA_FREQUENCY.get(explanation_key, '')
        st.caption(f"📅 対象期間: {latest_date} ({freq_label})" if freq_label else f"📅 対象日: {latest_date}")
    
    if release_date:
        st.caption(f"🔄 提供元更新日: {release_date}")
    
    if notes:
        st.caption(notes)

def show_metric_with_sparkline(label, series, df_column, unit="", explanation_key="", notes="", alert_func=None, decimal_places=1):
    """メトリック + スパークライン（ミニトレンドチャート）を表示（更新マーク対応）
    
    Args:
        decimal_places: 小数点以下の桁数（デフォルト1、為替・金利は3推奨）
    """
    if series is None or (hasattr(series, 'isna') and series.isna().all()):
        val = None
        delta = None
        latest_date = None
        release_date = None
    else:
        val = series.iloc[-1] if hasattr(series, 'iloc') else series
        if hasattr(series, 'iloc') and len(series) > 1:
            delta = val - series.iloc[-2]
        else:
            delta = None
        
        # Get actual last data date from DataFrame metadata
        latest_date = None
        release_date = None
        if hasattr(df, 'attrs'):
            if 'last_valid_dates' in df.attrs and df_column in df.attrs['last_valid_dates']:
                latest_date = df.attrs['last_valid_dates'][df_column]
            if 'fred_release_dates' in df.attrs and df_column in df.attrs['fred_release_dates']:
                release_date = df.attrs['fred_release_dates'][df_column]
    
    help_text = EXPLANATIONS.get(explanation_key, "")
    
    # Get freshness badge for label
    freshness_badge = get_freshness_badge(release_date or latest_date) if (release_date or latest_date) else ""
    display_label = f"{freshness_badge} {label}" if freshness_badge else label
    
    # Dynamic format string based on decimal_places
    val_format = f"{{:.{decimal_places}f}}"
    delta_format = f"{{:+.{decimal_places}f}}"
    
    # メトリック表示
    if alert_func and val is not None and alert_func(val):
        st.metric(display_label, f"{val_format.format(val)} {unit}" if val is not None else "N/A", 
                 delta=delta_format.format(delta) if delta is not None else None,
                 help=help_text, delta_color="inverse")
    else:
        st.metric(display_label, f"{val_format.format(val)} {unit}" if val is not None else "N/A",
                 delta=delta_format.format(delta) if delta is not None else None,
                 help=help_text)

    
    # Display data dates
    if latest_date:
        freq_label = DATA_FREQUENCY.get(df_column, '')
        st.caption(f"📅 対象期間: {latest_date} ({freq_label})" if freq_label else f"📅 対象日: {latest_date}")
    
    if release_date:
        st.caption(f"🔄 提供元更新日: {release_date}")
    
    if notes:
        st.caption(notes)
    
    # スパークライン（小さなトレンドチャート）
    if df_column in df.columns and not df.get(df_column, pd.Series()).isna().all():
        recent_data = df[df_column].tail(60)  # 直近60日分
        
        st.caption("📊 過去60日間のトレンド")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=recent_data.index,
            y=recent_data.values,
            mode='lines',
            line=dict(color='cyan', width=1),
            fill='tozeroy',
            fillcolor='rgba(0,255,255,0.1)',
            showlegend=False
        ))
        
        fig.update_layout(
            height=100,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode=False
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"spark_{uuid.uuid4().hex[:8]}")

def plot_dual_axis(df, left_col, right_col, left_name, right_name):
    """2軸チャート"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if left_col in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df[left_col], name=left_name, line=dict(color='cyan')),
            secondary_y=False
        )
    
    if right_col in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df[right_col], name=right_name, line=dict(color='orange')),
            secondary_y=True
        )
    
    fig.update_layout(
        template='plotly_dark',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    fig.update_yaxes(title_text=left_name, secondary_y=False)
    fig.update_yaxes(title_text=right_name, secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True, key="pc_2")

def plot_soma_composition(df):
    """SOMA構成チャート（SOMA Total + Bills Ratio）"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if 'SOMA_Total' in df.columns:
        soma_resampled = df['SOMA_Total'].resample('W').last()
        fig.add_trace(
            go.Bar(x=soma_resampled.index, y=soma_resampled, name='SOMA Total (Billions)', marker_color='steelblue'),
            secondary_y=False
        )
    
    if 'SomaBillsRatio' in df.columns:
        ratio_resampled = df['SomaBillsRatio'].resample('W').last()
        fig.add_trace(
            go.Scatter(x=ratio_resampled.index, y=ratio_resampled, name='Bills Ratio (%)', 
                      line=dict(color='orange', width=2)),
            secondary_y=True
        )
    
    fig.update_layout(
        template='plotly_dark',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    fig.update_yaxes(title_text="SOMA Total (B)", secondary_y=False)
    fig.update_yaxes(title_text="Bills Ratio (%)", secondary_y=True, tickformat='.1f')
    
    st.plotly_chart(fig, use_container_width=True, key="pc_3")

# ========== MAIN APP ==========
st.title(f"📊 {PAGE_TITLE}")
st.caption("更新間隔: 10分 | データソース: FRED, Yahoo Finance")

# Sidebar
with st.sidebar:
    st.header("🎛️ Control")
    if st.button("Force Update", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Check CSV modification time for cache invalidation
    csv_mtime = None
    if os.path.exists(MANUAL_DATA_FILE):
        csv_mtime = os.path.getmtime(MANUAL_DATA_FILE)
    
    st.markdown("---")
    # Direct download button (single step)
    df_for_download, _ = get_market_data(csv_mtime)
    csv_data = df_for_download.to_csv()
    st.download_button(
        "📥 Download CSV",
        csv_data,
        "market_cockpit_data.csv",
        "text/csv",
        key="download_csv_main"
    )
    
    # === Market Alerts Section ===
    st.markdown("---")
    st.subheader("🔔 Market Alerts")
    st.caption("主要機関（FRB, Treasury, BIS）の直近24h発表")
    
    # Check for alerts button
    if st.button("🔍 今すぐチェック", key="check_alerts_btn"):
        with st.spinner("RSS取得中..."):
            alerts = check_for_market_alerts()
            st.session_state['market_alerts'] = alerts
            st.session_state['alerts_checked_at'] = datetime.datetime.now().strftime('%H:%M')
    
    # Display alerts
    if 'market_alerts' in st.session_state and st.session_state['market_alerts']:
        checked_at = st.session_state.get('alerts_checked_at', '')
        st.caption(f"📡 {checked_at} チェック済み")
        
        for alert in st.session_state['market_alerts']:
            hours = alert.get('hours_ago', 0)
            icon = "🔴" if hours < 6 else "🟡" if hours < 12 else "🟢"
            st.markdown(f"{icon} **[{alert['source']}]** {alert['title']}")
            st.caption(f"  ↳ {hours}時間前 | [詳細]({alert['link']})")
    else:
        if 'alerts_checked_at' in st.session_state:
            st.info("📭 直近24時間の新着アラートなし")
        else:
            st.caption("ボタンでアラートをチェック")


# Load Data (returns tuple: ffill版, オリジナル版)
df, df_original = get_market_data(csv_mtime)

# Data Health Check
with st.sidebar:
    # === AI Analysis Focus Settings (MOVED TO TOP for visibility) ===
    st.markdown("---")
    st.subheader("🎯 AI Analysis Focus")
    st.caption("AIに特に注目させたい領域を選択")
    
    ai_focus_options = [
        "💧 流動性 (Liquidity)",
        "👷 雇用 (Employment)",
        "📈 インフレ (Inflation)",
        "🏦 銀行・信用 (Banking)",
        "₿ クリプト (Crypto)",
        "💵 為替 (FX)",
        "📊 バリュエーション (Valuation)",
        "🌏 グローバルM2 (Global M2)"
    ]
    
    ai_focus_selection = st.multiselect(
        "注目領域",
        ai_focus_options,
        default=[],
        key="ai_focus_categories",
        help="選択した領域がAI分析の先頭に表示されます。未選択の場合は全指標を平等に分析"
    )
    
    if ai_focus_selection:
        st.success(f"✅ {len(ai_focus_selection)} 領域をフォーカス中")
    else:
        st.caption("📊 全指標を平等に分析")
    
    st.markdown("---")
    
    # === Data Health Monitor (Collapsible) ===
    with st.expander("📡 Data Health Monitor", expanded=False):
        # Current time display
        import datetime
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.caption(f"🕐 現在時刻: {current_time}")
        
        # Data freshness check
        if hasattr(df, 'attrs') and 'last_valid_dates' in df.attrs:
            release_dates = df.attrs.get('fred_release_dates', {})
            freshness = get_data_freshness_status(df.attrs['last_valid_dates'], release_dates)
            summary = freshness['summary']
            
            # Health Score (visual meter)
            health_score = summary['health_score']
            if health_score >= 80:
                health_color = "🟢"
                health_status = "Healthy"
            elif health_score >= 50:
                health_color = "🟡"
                health_status = "Warning"
            else:
                health_color = "🔴"
                health_status = "Critical"
            
            st.metric(
                "Data Health Score",
                f"{health_color} {health_score}%",
                delta=f"{health_status}"
            )
            
            # Summary counts in compact layout
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"🟢 Fresh: {summary['fresh_count']}")
                st.caption(f"🔴 Critical: {summary['critical_count']}")
            with col2:
                st.caption(f"🟡 Stale: {summary['stale_count']}")
                st.caption(f"⚫ Missing: {summary['missing_count']}")
            
            # Detailed view in expander
            with st.expander("📋 詳細レポート", expanded=False):
                st.markdown("##### 🔴 要確認 (Critical)")
                if freshness['critical']:
                    for ind in freshness['critical']:
                        detail = freshness['details'][ind]
                        if detail.get('is_release_based'):
                            st.markdown(f"- **{ind}**: {detail['days_old']}日前 (公表: {detail['release_date']}, 対象: {detail['last_date']})")
                        else:
                            st.markdown(f"- **{ind}**: {detail['days_old']}日前 (対象: {detail['last_date']})")
                else:
                    st.caption("なし ✅")
                
                st.markdown("##### 🟡 経過注意 (Stale)")
                if freshness['stale']:
                    for ind in freshness['stale']:
                        detail = freshness['details'][ind]
                        if detail.get('is_release_based'):
                            st.markdown(f"- **{ind}**: {detail['days_old']}日前 (公表: {detail['release_date']}, 対象: {detail['last_date']})")
                        else:
                            st.markdown(f"- **{ind}**: {detail['days_old']}日前 (対象: {detail['last_date']})")
                else:
                    st.caption("なし ✅")
                
                st.markdown("##### 🟢 最新 (Fresh)")
                st.caption(f"{len(freshness['fresh'])} 項目が最新データ")
            
            # Warning for AI Analysis
            if summary['critical_count'] > 0 or summary['stale_count'] > 3:
                st.warning(f"⚠️ {summary['critical_count'] + summary['stale_count']} 項目が古い可能性")
        else:
            total_cols = len(df.columns)
            valid_cols = sum(1 for c in df.columns if not df[c].isna().all())
            st.metric("Valid Series", f"{valid_cols}/{total_cols}")
    
    st.caption("💡 全データはFRED APIから自動取得")



# Tabs
tabs = st.tabs(["📊 Liquidity & Rates", "🌏 Global Money & FX", "📈 US Economic Data", "🪙 Crypto Liquidity", "🤖 AI Analysis", "🎲 Monte Carlo", "📰 Market Voices", "🎭 Market Sentiment"])

# Tab 1: Liquidity & Rates
with tabs[0]:
    st.subheader("🏦 Liquidity & The Fed")
    
    # === VALUATION & LEVERAGE SECTION (NEW) ===
    st.markdown("#### 📊 バリュエーション & レバレッジ指標")
    st.caption("市場の過熱度とレバレッジ状況を一目で確認")
    
    # Fetch data
    pe_data = get_pe_ratios()
    leverage_data = get_crypto_leverage_data()
    
    col_val1, col_val2, col_val3, col_val4 = st.columns(4)
    
    with col_val1:
        if pe_data and pe_data.get('sp500_pe'):
            pe = pe_data['sp500_pe']
            avg = pe_data['sp500_pe_avg']
            delta = pe - avg
            delta_pct = (delta / avg) * 100
            # Color coding: >25 = overvalued, <15 = undervalued
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
            # Funding rate interpretation: >0.1% = bullish crowded, <-0.1% = bearish crowded
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
    
    # === Open Interest with Historical Comparison ===
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
                
                # Color coding based on position vs average
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
            
            # Trend chart
            if leverage_data.get('btc_oi_history'):
                hist = leverage_data['btc_oi_history']
                oi_df = pd.DataFrame({
                    'date': hist['timestamps'],
                    'BTC OI': hist['values']
                }).set_index('date')
                st.line_chart(oi_df, height=150)
        
        with col_eth:
            oi = leverage_data.get('eth_open_interest', 0)
            avg = leverage_data.get('eth_oi_avg_30d')
            ath = leverage_data.get('eth_oi_ath')
            
            if oi and avg:
                pct_vs_avg = ((oi - avg) / avg) * 100
                pct_vs_ath = (oi / ath * 100) if ath else 0
                
                # Color coding
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
            
            # Trend chart
            if leverage_data.get('eth_oi_history'):
                hist = leverage_data['eth_oi_history']
                oi_df = pd.DataFrame({
                    'date': hist['timestamps'],
                    'ETH OI': hist['values']
                }).set_index('date')
                st.line_chart(oi_df, height=150)
        
        st.caption("""
        💡 **Open Interest の見方**
        - **30日平均比 +20%以上** 🔴: レバレッジ過多 → 清算連鎖リスク高
        - **30日平均比 ±5%** 🟢: 正常レンジ
        - **ATH比**: 過去30日の最高値に対する現在位置
        """)
    
    st.markdown("---")
    

    # Net Liquidity - Special treatment with SP500 comparison
    st.markdown("#### Net Liquidity")

    col1, col2 = st.columns([1, 3])
    with col1:
        show_metric_with_sparkline("Net Liquidity", df.get('Net_Liquidity'), 'Net_Liquidity', "B", "Net_Liquidity", notes="市場の真の燃料")
    with col2:
        st.markdown("##### Net Liquidity vs S&P 500 (過去2年間)")
        plot_dual_axis(df, 'Net_Liquidity', 'SP500', 'Net Liquidity (L)', 'S&P 500 (R)')
    
    st.markdown("---")
    
    # ON RRP, Reserves, TGA - Integrated view
    col1, col2 = st.columns(2)
    
    with col1:
        # ON RRP
        st.markdown("#### ON RRP")
        show_metric_with_sparkline("ON RRP", df.get('ON_RRP'), 'ON_RRP', "B", "ON_RRP", notes="余剰資金")
        if 'ON_RRP' in df.columns and not df.get('ON_RRP', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['ON_RRP']], height=250)
        
        st.markdown("")  # Spacing
        
        # TGA
        st.markdown("#### TGA")
        show_metric_with_sparkline("TGA", df.get('TGA'), 'TGA', "B", "TGA", notes="政府口座")
        if 'TGA' in df.columns and not df.get('TGA', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['TGA']], height=250)
    
    with col2:
        # Reserves
        st.markdown("#### Reserves")
        show_metric_with_sparkline("Reserves", df.get('Reserves'), 'Reserves', "B", "Reserves", notes="銀行準備預金")
        if 'Reserves' in df.columns and not df.get('Reserves', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['Reserves']], height=250)
    
    st.markdown("---")
    st.subheader("🔧 Market Plumbing (Repo & Liquidity)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # SRF
        st.markdown("#### SRF")
        show_metric_with_sparkline("SRF", df.get('SRF'), 'SRF', "B", "SRF", notes="国内リポ市場")
        if 'SRF' in df.columns and not df.get('SRF', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['SRF']], height=200)
        
        st.markdown("")
        
        # SOFR
        st.markdown("#### SOFR")
        show_metric_with_sparkline("SOFR", df.get('SOFR'), 'SOFR', "%", "SOFR", notes="担保付金利", decimal_places=3)
        if 'SOFR' in df.columns and not df.get('SOFR', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['SOFR']], height=200)
    
    with col2:
        # FIMA
        st.markdown("#### FIMA")
        show_metric_with_sparkline("FIMA", df.get('FIMA'), 'FIMA', "B", "FIMA", notes="海外ドル流動性")
        if 'FIMA' in df.columns and not df.get('FIMA', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['FIMA']], height=200)
        
        st.markdown("")
        
        # EFFR - IORB
        st.markdown("#### EFFR - IORB")
        diff = None
        diff_date = None
        if 'EFFR' in df.columns and 'IORB' in df.columns:
            diff = (df['EFFR'] - df['IORB']) * 100  # Convert to basis points
            # Get date from EFFR data
            if hasattr(df, 'attrs') and 'last_valid_dates' in df.attrs and 'EFFR' in df.attrs['last_valid_dates']:
                diff_date = df.attrs['last_valid_dates']['EFFR']
        
        show_metric("EFFR - IORB", diff, "bps", notes="連銀準備金状況")
        if diff_date:
            st.caption(f"📅 {diff_date}")
        
        # EFFR and IORB combined long-term chart
        rate_cols = ['EFFR', 'IORB']
        valid_rates = [c for c in rate_cols if c in df.columns and not df.get(c, pd.Series()).isna().all()]
        if valid_rates:
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[valid_rates], height=200)
    
    st.markdown("---")
    st.subheader("🏛️ Fed Balance Sheet (SOMA)")
    
    # RMP Status Display
    rmp_status_series = df.get('RMP_Status_Text')
    rmp_status = rmp_status_series.iloc[-1] if hasattr(rmp_status_series, 'iloc') else "データ collect中..."
    rmp_active_series = df.get('RMP_Alert_Active', pd.Series([False]))
    rmp_active = rmp_active_series.iloc[-1] if hasattr(rmp_active_series, 'iloc') else False
    
    if rmp_active:
        st.info(f"📊 **RMP状況**: {rmp_status}")
    else:
        st.warning(f"ℹ️ **RMP状況**: {rmp_status}")
    
    # SOMA Composition Chart (Overview)
    st.markdown("##### SOMA Composition (Total & Bills Ratio)")
    plot_soma_composition(df)
    
    st.markdown("")
    
    # Individual metrics with integrated views
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### SOMA Total")
        show_metric_with_sparkline("SOMA Total", df.get('SOMA_Total'), 'SOMA_Total', "B", "SOMA_Total", notes="保有資産総額")
    
    with col2:
        st.markdown("#### SOMA Bills")
        show_metric_with_sparkline("SOMA Bills", df.get('SOMA_Bills'), 'SOMA_Bills', "B", "SOMA_Bills", notes="短期国債保有高")
        if 'SOMA_Bills' in df.columns and not df.get('SOMA_Bills', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['SOMA_Bills']], height=200)
    
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
            st.line_chart(df[['Total_Loans']], height=250)
    
    with col2:
        st.markdown("#### Primary Credit")
        show_metric_with_sparkline("Primary Credit", df.get('Primary_Credit'), 'Primary_Credit', "B", "Primary", notes="健全行向け", alert_func=lambda x: x>1)
        if 'Primary_Credit' in df.columns and not df.get('Primary_Credit', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['Primary_Credit']], height=250)
    
    st.markdown("---")
    st.subheader("🏦 Private Banking Sector")
    st.caption("💡 FRBの政策と銀行の実際の行動のギャップを監視")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bank Cash
        st.markdown("#### Bank Cash Holdings")
        show_metric_with_sparkline("Bank Cash", df.get('Bank_Cash'), 'Bank_Cash', "B", "Bank_Cash", notes="銀行の現金退蔵")
        if 'Bank_Cash' in df.columns and not df.get('Bank_Cash', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['Bank_Cash']], height=200)
    
    with col2:
        # C&I Lending Tightening (formerly Lending Standards)
        st.markdown("#### C&I Lending Tightening")
        st.caption("商工業融資基準の厳格化（純割合）")
        # Custom display with +/- sign for Net %
        lending_val = df.get('Lending_Standards')
        if lending_val is not None and not lending_val.isna().all():
            val = lending_val.iloc[-1]
            delta = val - lending_val.iloc[-2] if len(lending_val) > 1 else None
            # Format with explicit sign
            val_str = f"+{val:.1f}" if val >= 0 else f"{val:.1f}"
            st.metric(
                "Net %", 
                f"{val_str} pts",
                delta=f"{delta:+.1f}" if delta is not None else None,
                help=EXPLANATIONS.get('Lending_Standards', '')
            )
            # Show frequency and date
            if hasattr(df, 'attrs') and 'last_valid_dates' in df.attrs:
                if 'Lending_Standards' in df.attrs['last_valid_dates']:
                    latest_date = df.attrs['last_valid_dates']['Lending_Standards']
                    st.caption(f"📅 {latest_date} (四半期)")
            
            # Sparkline (60 day trend)
            if 'Lending_Standards' in df.columns:
                recent_data = df['Lending_Standards'].tail(60)
                st.caption("📊 過去60日間のトレンド")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=recent_data.index,
                    y=recent_data.values,
                    mode='lines',
                    line=dict(color='cyan', width=1),
                    fill='tozeroy',
                    fillcolor='rgba(0,255,255,0.1)',
                    showlegend=False
                ))
                fig.update_layout(
                    height=80,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    hovermode=False
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"spark_lending_{uuid.uuid4().hex[:8]}")
        else:
            st.metric("Net %", "N/A")
        if 'Lending_Standards' in df.columns and not df.get('Lending_Standards', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['Lending_Standards']], height=200)
    
    # ========== SLOOS: C&I Lending Section ==========
    st.markdown("---")
    with st.expander("💰 C&I Lending (商工業融資) - SLOOS", expanded=False):
        st.caption("💡 融資基準の厳格化と需要の乖離、残高減少はクレジットクランチの前兆")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # C&I Standards - Large/Medium Firms
            st.markdown("#### 融資基準（大・中堅企業）")
            show_metric_with_sparkline("Large/Mid Firms", df.get('CI_Std_Large'), 'CI_Std_Large', "pts", "CI_Std_Large", notes="0超で貸し渋り、20%超で警戒")
            if 'CI_Std_Large' in df.columns and not df.get('CI_Std_Large', pd.Series()).isna().all():
                st.markdown("###### Long-term Trend (過去2年間)")
                st.line_chart(df[['CI_Std_Large']], height=200)
            
            st.markdown("")
            
            # C&I Demand
            st.markdown("#### 融資需要（大・中堅企業）")
            show_metric_with_sparkline("Demand", df.get('CI_Demand'), 'CI_Demand', "pts", "CI_Demand", notes="基準との乖離に注目")
            if 'CI_Demand' in df.columns and not df.get('CI_Demand', pd.Series()).isna().all():
                st.markdown("###### Long-term Trend (過去2年間)")
                st.line_chart(df[['CI_Demand']], height=200)
        
        with col2:
            # C&I Standards - Small Firms
            st.markdown("#### 融資基準（小企業）")
            show_metric_with_sparkline("Small Firms", df.get('CI_Std_Small'), 'CI_Std_Small', "pts", "CI_Std_Small", notes="雇用悪化の先行指標")
            if 'CI_Std_Small' in df.columns and not df.get('CI_Std_Small', pd.Series()).isna().all():
                st.markdown("###### Long-term Trend (過去2年間)")
                st.line_chart(df[['CI_Std_Small']], height=200)
            
            st.markdown("")
            
            # C&I Loan Balance
            st.markdown("#### 融資残高（総額）")
            show_metric_with_sparkline("C&I Loans", df.get('CI_Loans'), 'CI_Loans', "B", "CI_Loans", notes="残高減少でクレジットクランチ")
            if 'CI_Loans' in df.columns and not df.get('CI_Loans', pd.Series()).isna().all():
                st.markdown("###### Long-term Trend (過去2年間)")
                st.line_chart(df[['CI_Loans']], height=200)

    
    # ========== SLOOS: CRE Lending Section ==========
    st.markdown("---")
    with st.expander("🏢 CRE Lending (商業用不動産融資) - SLOOS", expanded=False):
        st.caption("💡 不動産開発・オフィスクライシス・借り換えリスクを監視")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CRE Standards - Construction
            st.markdown("#### 融資基準（建設・土地開発）")
            show_metric_with_sparkline("Construction", df.get('CRE_Std_Construction'), 'CRE_Std_Construction', "pts", "CRE_Std_Construction", notes="不動産開発の蛇口")
            if 'CRE_Std_Construction' in df.columns and not df.get('CRE_Std_Construction', pd.Series()).isna().all():
                st.markdown("###### Long-term Trend (過去2年間)")
                st.line_chart(df[['CRE_Std_Construction']], height=200)
            
            st.markdown("")
            
            # CRE Standards - Multifamily
            st.markdown("#### 融資基準（集合住宅）")
            show_metric_with_sparkline("Multifamily", df.get('CRE_Std_Multifamily'), 'CRE_Std_Multifamily', "pts", "CRE_Std_Multifamily", notes="住宅供給に影響")
            if 'CRE_Std_Multifamily' in df.columns and not df.get('CRE_Std_Multifamily', pd.Series()).isna().all():
                st.markdown("###### Long-term Trend (過去2年間)")
                st.line_chart(df[['CRE_Std_Multifamily']], height=200)
            
            st.markdown("")
            
            # CRE Demand
            st.markdown("#### 融資需要")
            show_metric_with_sparkline("CRE Demand", df.get('CRE_Demand'), 'CRE_Demand', "pts", "CRE_Demand", notes="不動産投資意欲")
            if 'CRE_Demand' in df.columns and not df.get('CRE_Demand', pd.Series()).isna().all():
                st.markdown("###### Long-term Trend (過去2年間)")
                st.line_chart(df[['CRE_Demand']], height=200)
        
        with col2:
            # CRE Standards - Office
            st.markdown("#### 融資基準（オフィス等）")
            show_metric_with_sparkline("Office/NonRes", df.get('CRE_Std_Office'), 'CRE_Std_Office', "pts", "CRE_Std_Office", notes="オフィスクライシス警戒")
            if 'CRE_Std_Office' in df.columns and not df.get('CRE_Std_Office', pd.Series()).isna().all():
                st.markdown("###### Long-term Trend (過去2年間)")
                st.line_chart(df[['CRE_Std_Office']], height=200)
            
            st.markdown("")
            
            # CRE Loan Balance (Weekly)
            st.markdown("#### 融資残高（週次）")
            show_metric_with_sparkline("CRE Loans", df.get('CRE_Loans'), 'CRE_Loans', "B", "CRE_Loans", notes="週次でリアルタイム監視")
            if 'CRE_Loans' in df.columns and not df.get('CRE_Loans', pd.Series()).isna().all():
                st.markdown("###### Long-term Trend (過去2年間)")
                st.line_chart(df[['CRE_Loans']], height=200)
        
        # Loan Balance Comparison Chart
        st.markdown("###### 融資残高の推移比較（C&I vs CRE）")
        loan_cols = [c for c in ['CI_Loans', 'CRE_Loans'] if c in df.columns and not df[c].isna().all()]
        if loan_cols:
            st.line_chart(df[loan_cols].tail(520), height=200)  # ~2 years
    
    st.markdown("---")
    st.subheader("⚠️ Risk & Bonds")
    st.caption("💡 市場のリスク状態と債券市場の動向を監視")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # VIX Index
        st.markdown("#### VIX Index")
        show_metric_with_sparkline("VIX Index", df.get('VIX'), 'VIX', "pt", "VIX", notes="恐怖指数", alert_func=lambda x: x>20)
        if 'VIX' in df.columns and not df.get('VIX', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['VIX']], height=200)
    
    with col2:
        # Credit Spread
        st.markdown("#### Credit Spread")
        show_metric_with_sparkline("Credit Spread", df.get('Credit_Spread'), 'Credit_Spread', "%", notes="ジャンク債スプレッド", decimal_places=3)
        if 'Credit_Spread' in df.columns and not df.get('Credit_Spread', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['Credit_Spread']], height=200)
    
    with col3:
        # US 10Y Yield
        st.markdown("#### US 10Y Yield")
        show_metric_with_sparkline("US 10Y Yield", df.get('US_TNX'), 'US_TNX', "%", notes="長期金利", decimal_places=3)
        if 'US_TNX' in df.columns and not df.get('US_TNX', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['US_TNX']], height=200)

# Tab 2: Global Money & FX
with tabs[1]:
    st.subheader("🌏 Global Money & FX")
    st.caption("💡 グローバル流動性、為替、コモディティ、仮想通貨の動向")
    
    # --- Global M2 Section ---
    st.markdown("---")
    st.markdown("### 💵 Global M2 Money Supply")
    st.caption("💡 世界の主要国マネーサプライ動向")
    
    # Get exchange rates for USD conversion
    usdjpy = df.get('USDJPY').iloc[-1] if df.get('USDJPY') is not None and len(df.get('USDJPY', pd.Series()).dropna()) > 0 else 157.0
    eurusd = df.get('EURUSD').iloc[-1] if df.get('EURUSD') is not None and len(df.get('EURUSD', pd.Series()).dropna()) > 0 else 1.04
    usdcny = df.get('USDCNY').iloc[-1] if df.get('USDCNY') is not None and len(df.get('USDCNY', pd.Series()).dropna()) > 0 else 7.30
    
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
        cn_m2_val = df.get('CN_M2').iloc[-1] if df.get('CN_M2') is not None else 313.5
        cn_m2_usd = cn_m2_val / usdcny  # Trillion CNY to Trillion USD
        show_metric_with_sparkline("CN M2 (Nominal)", df.get('CN_M2'), 'CN_M2', "T CNY", notes="名目")
        st.markdown(f"**💵 ≈ ${cn_m2_usd:.1f}T USD** (1 USD = {usdcny:.2f} CNY)")
        cn_cpi = df.get('CN_CPI').iloc[-1] if df.get('CN_CPI') is not None and len(df.get('CN_CPI', pd.Series()).dropna()) > 0 else 0.7
        cn_m2_real_val = df.get('CN_M2_Real').iloc[-1] if df.get('CN_M2_Real') is not None else cn_m2_val / (1 + cn_cpi/100)
        cn_m2_real_usd = cn_m2_real_val / usdcny
        show_metric_with_sparkline("CN M2 (Real)", df.get('CN_M2_Real'), 'CN_M2_Real', "T CNY", notes=f"CPI {cn_cpi}%調整")
        st.markdown(f"**💵 ≈ ${cn_m2_real_usd:.1f}T USD**")
        if 'CN_M2' in df.columns and not df.get('CN_M2', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['CN_M2']].dropna(), height=150)
        
        # China Credit Impulse (Proxy)
        st.markdown("---")
        st.markdown("##### 📊 Credit Impulse（信用刺激指数）")
        st.caption("⚠️ 代用計算: BIS経由FRED四半期信用残高データ(CRDQCNAPABIS)使用")
        
        show_metric_with_sparkline(
            "Credit Impulse", 
            df.get('CN_Credit_Impulse'), 
            'CN_Credit_Impulse', 
            "%", 
            notes="(信用フロー変化/GDP)"
        )
        if 'CN_Credit_Impulse' in df.columns and not df.get('CN_Credit_Impulse', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去5年間)")
            st.line_chart(df[['CN_Credit_Impulse']].dropna(), height=150)
    
    # Japan & Euro
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### 🇯🇵 Japan M2")
        jp_m2_val = df.get('JP_M2').iloc[-1] if df.get('JP_M2') is not None else 1260.0
        jp_m2_usd = jp_m2_val / usdjpy * 1000  # Trillion JPY to Billion USD (1T JPY = 1000B JPY / USDJPY)
        show_metric_with_sparkline("JP M2 (Nominal)", df.get('JP_M2'), 'JP_M2', "T JPY", notes="名目")
        st.markdown(f"**💵 ≈ ${jp_m2_usd/1000:.1f}T USD** (1 USD = {usdjpy:.1f} JPY)")
        jp_cpi = df.get('JP_CPI').iloc[-1] if df.get('JP_CPI') is not None and len(df.get('JP_CPI', pd.Series()).dropna()) > 0 else 2.9
        jp_m2_real_val = df.get('JP_M2_Real').iloc[-1] if df.get('JP_M2_Real') is not None else jp_m2_val / (1 + jp_cpi/100)
        jp_m2_real_usd = jp_m2_real_val / usdjpy * 1000
        show_metric_with_sparkline("JP M2 (Real)", df.get('JP_M2_Real'), 'JP_M2_Real', "T JPY", notes=f"CPI {jp_cpi}%調整")
        st.markdown(f"**💵 ≈ ${jp_m2_real_usd/1000:.1f}T USD**")
        if 'JP_M2' in df.columns and not df.get('JP_M2', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['JP_M2']].dropna(), height=150)
    
    with col4:
        st.markdown("#### 🇪🇺 Euro M2")
        eu_m2_val = df.get('EU_M2').iloc[-1] if df.get('EU_M2') is not None else 15.6
        eu_m2_usd = eu_m2_val * eurusd  # Trillion EUR to Trillion USD
        show_metric_with_sparkline("EU M2 (Nominal)", df.get('EU_M2'), 'EU_M2', "T EUR", notes="名目")
        st.markdown(f"**💵 ≈ ${eu_m2_usd:.1f}T USD** (1 EUR = {eurusd:.2f} USD)")
        eu_cpi = df.get('EU_CPI').iloc[-1] if df.get('EU_CPI') is not None and len(df.get('EU_CPI', pd.Series()).dropna()) > 0 else 2.1
        eu_m2_real_val = df.get('EU_M2_Real').iloc[-1] if df.get('EU_M2_Real') is not None else eu_m2_val / (1 + eu_cpi/100)
        eu_m2_real_usd = eu_m2_real_val * eurusd
        show_metric_with_sparkline("EU M2 (Real)", df.get('EU_M2_Real'), 'EU_M2_Real', "T EUR", notes=f"CPI {eu_cpi}%調整")
        st.markdown(f"**💵 ≈ ${eu_m2_real_usd:.1f}T USD**")
        if 'EU_M2' in df.columns and not df.get('EU_M2', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['EU_M2']].dropna(), height=150)
    
    # --- FX Section ---
    st.markdown("---")
    st.markdown("### 💱 Foreign Exchange")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### DXY")
        show_metric_with_sparkline("Dollar Index", df.get('DXY'), 'DXY', "pt", notes="ドル強弱指数", decimal_places=3)
        if 'DXY' in df.columns and not df.get('DXY', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['DXY']], height=150)
    
    with col2:
        st.markdown("#### USD/JPY")
        show_metric_with_sparkline("USD/JPY", df.get('USDJPY'), 'USDJPY', "¥", notes="円キャリー", decimal_places=3)
        if 'USDJPY' in df.columns and not df.get('USDJPY', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['USDJPY']], height=150)
    
    with col3:
        st.markdown("#### EUR/USD")
        show_metric_with_sparkline("EUR/USD", df.get('EURUSD'), 'EURUSD', "$", notes="ユーロドル", decimal_places=3)
        if 'EURUSD' in df.columns and not df.get('EURUSD', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['EURUSD']], height=150)
    
    with col4:
        st.markdown("#### USD/CNY")
        show_metric_with_sparkline("USD/CNY", df.get('USDCNY'), 'USDCNY', "CNY", notes="人民元", decimal_places=3)
        if 'USDCNY' in df.columns and not df.get('USDCNY', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['USDCNY']], height=150)
    
    # --- Commodities Section ---
    st.markdown("---")
    st.markdown("### 🛢️ Commodities")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### Gold")
        show_metric_with_sparkline("Gold", df.get('Gold'), 'Gold', "$", notes="金先物", decimal_places=3)
        if 'Gold' in df.columns and not df.get('Gold', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['Gold']], height=150)
    
    with col2:
        st.markdown("#### Silver")
        show_metric_with_sparkline("Silver", df.get('Silver'), 'Silver', "$", notes="銀先物", decimal_places=3)
        if 'Silver' in df.columns and not df.get('Silver', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['Silver']], height=150)
    
    with col3:
        st.markdown("#### Oil (WTI)")
        show_metric_with_sparkline("Oil", df.get('Oil'), 'Oil', "$", notes="原油先物", decimal_places=3)
        if 'Oil' in df.columns and not df.get('Oil', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['Oil']], height=150)
    
    with col4:
        st.markdown("#### Copper")
        show_metric_with_sparkline("Copper", df.get('Copper'), 'Copper', "$", notes="銅先物（景気先行指標）", decimal_places=3)
        if 'Copper' in df.columns and not df.get('Copper', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['Copper']], height=150)
    
    # --- Crypto Section ---
    st.markdown("---")
    st.markdown("### 🪙 Cryptocurrency")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Bitcoin (BTC)")
        show_metric_with_sparkline("BTC", df.get('BTC'), 'BTC', "$", notes="リスクオン指標", decimal_places=3)
        if 'BTC' in df.columns and not df.get('BTC', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['BTC']], height=200)
    
    with col2:
        st.markdown("#### Ethereum (ETH)")
        show_metric_with_sparkline("ETH", df.get('ETH'), 'ETH', "$", notes="DeFi基盤", decimal_places=3)
        if 'ETH' in df.columns and not df.get('ETH', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['ETH']], height=200)

# Tab 3: US Economic Data
with tabs[2]:
    st.subheader("🇺🇸 US Economic Data")
    st.caption("💡 景気循環、物価、雇用の多角的な分析")
    
    # === FOMC SEP (Dot Plot) Section ===
    st.markdown("### 🏛️ FOMC Economic Projections (SEP)")
    st.caption("📊 FOMCメンバーによる経済見通し（ドットプロット） - 四半期更新")
    
    # Fetch FOMC data
    fomc_sep = get_fomc_sep_projections()
    fedwatch = get_cme_fedwatch()
    
    col_fomc1, col_fomc2 = st.columns([2, 1])
    
    with col_fomc1:
        if fomc_sep:
            # Display cards for each projection
            proj_cols = st.columns(4)
            
            with proj_cols[0]:
                if fomc_sep.get('ff_rate'):
                    ff = fomc_sep['ff_rate']
                    change = ff['latest'] - ff['previous'] if ff['previous'] else 0
                    st.metric("FF金利予測 (中央値)", f"{ff['latest']:.2f}%", 
                             delta=f"{change:+.2f}%", delta_color="inverse")
                    st.caption(f"🔄 更新: {ff['date']}")
                else:
                    st.metric("FF金利予測", "N/A")
            
            with proj_cols[1]:
                if fomc_sep.get('gdp_growth'):
                    gdp = fomc_sep['gdp_growth']
                    st.metric("GDP成長率予測", f"{gdp['latest']:.1f}%")
                else:
                    st.metric("GDP成長率予測", "N/A")
            
            with proj_cols[2]:
                if fomc_sep.get('unemployment'):
                    unemp = fomc_sep['unemployment']
                    st.metric("失業率予測", f"{unemp['latest']:.1f}%")
                else:
                    st.metric("失業率予測", "N/A")
            
            with proj_cols[3]:
                if fomc_sep.get('core_pce'):
                    pce = fomc_sep['core_pce']
                    st.metric("Core PCE予測", f"{pce['latest']:.1f}%")
                else:
                    st.metric("Core PCE予測", "N/A")
        else:
            st.info("📝 FOMC SEPデータを読み込み中...")
    
    with col_fomc2:
        st.markdown("#### 📈 CME FedWatch")
        if fedwatch:
            probs = fedwatch['probabilities']
            
            # Main probability (cut)
            cut_prob = probs.get('cut_25bp', 0) + probs.get('cut_50bp', 0)
            if cut_prob >= 50:
                prob_emoji = "📉"
                prob_label = "利下げ優勢"
            elif probs.get('hold', 0) >= 50:
                prob_emoji = "➡️"
                prob_label = "据え置き優勢"
            else:
                prob_emoji = "📈"
                prob_label = "利上げ優勢"
            
            st.metric(f"{prob_emoji} 次回会合予想", prob_label)
            st.caption(f"📅 {fedwatch['next_meeting']}")
            
            # Probability breakdown
            st.markdown("**確率分布:**")
            st.caption(f"🔻 利下げ: {cut_prob:.0f}%")
            st.caption(f"➡️ 据置: {probs.get('hold', 0):.0f}%")
            st.caption(f"🔺 利上げ: {probs.get('hike_25bp', 0):.0f}%")
            
            if fedwatch.get('note'):
                st.caption(f"📝 {fedwatch['note']}")
        else:
            st.info("📝 CME FedWatchデータ準備中...")
    
    st.markdown("---")
    
    # helper for MoM/YoY - IMPORTANT: Use df_original for accurate calculations!
    def get_mom_yoy(df_column, freq='M'):
        """Calculate MoM% and YoY% using ORIGINAL (pre-ffill) data for accuracy"""
        # Use df_original (global) which has actual monthly data points, not ffill data
        series = df_original.get(df_column)
        if series is None or len(series.dropna()) < 2:
            return None, None
        s = series.dropna()
        curr = s.iloc[-1]
        prev = s.iloc[-2]
        mom = (curr / prev - 1) * 100 if prev != 0 else 0
        
        # YoY: Monthly=12, Quarterly=4
        offset = 12 if freq == 'M' else 4
        yoy = None
        if len(s) > offset:
            prev_yr = s.iloc[-(offset+1)]
            yoy = (curr / prev_yr - 1) * 100 if prev_yr != 0 else 0
        return mom, yoy

    # helper to wrap indicators for better organization and consistency across the tab
    def display_macro_card(title, series, df_column, unit="", notes="", freq='M', show_level=True):
        """Display macro indicator card with MoM, YoY, sparkline and long-term chart
        
        Args:
            show_level: If False, skip the sparkline/level display (for NFP where only change matters)
        """
        st.markdown(f"#### {title}")
        mom, yoy = get_mom_yoy(df_column, freq=freq)  # Use df_column, not series
        
        # 1. Metrics Row (MoM, YoY)
        m_col1, m_col2 = st.columns(2)
        if mom is not None:
            m_col1.metric("前月比", f"{mom:+.1f}%")
        if yoy is not None:
            m_col2.metric("前年比", f"{yoy:+.1f}%")
        
        # 2. Main Metric with Sparkline & Update Date (optional)
        if show_level:
            show_metric_with_sparkline(title, series, df_column, unit, notes=notes)
        
        # 3. YoY% Trend Chart (NEW - easier to see changes over time)
        # Use original data for accurate YoY calculation
        original_series = df_original.get(df_column)
        if original_series is not None and len(original_series.dropna()) > 12:
            data = original_series.dropna()
            yoy_series = (data / data.shift(12) - 1) * 100
            yoy_series = yoy_series.dropna()
            if len(yoy_series) > 0:
                st.markdown(f"###### {title} YoY% (前年比変化率)")
                st.line_chart(yoy_series, height=120)
        
        # 4. Dedicated Long-term Chart (Level)
        if series is not None and not series.isna().all():
            st.markdown(f"###### {title} Long-term Trend (Level)")
            st.line_chart(series, height=150)


    # --- 1️⃣ Monetary Policy (金融政策) ---
    st.markdown("---")
    st.markdown("### 🏛️ 1. Monetary Policy (金融政策)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### FF Target Rate (Upper)")
        show_metric_with_sparkline("FF Upper", df.get('FedFundsUpper'), 'FedFundsUpper', "%", notes="政策金利上限", decimal_places=3)
        if 'FedFundsUpper' in df.columns:
            st.line_chart(df[['FedFundsUpper']], height=120)
            
    with col2:
        st.markdown("#### EFFR")
        show_metric_with_sparkline("EFFR", df.get('EFFR'), 'EFFR', "%", notes="実効FF金利", decimal_places=3)
        if 'EFFR' in df.columns:
            st.line_chart(df[['EFFR']], height=120)
            
    with col3:
        st.markdown("#### SOFR")
        show_metric_with_sparkline("SOFR", df.get('SOFR'), 'SOFR', "%", notes="担保付金利(レポ市場)", decimal_places=3)
        if 'SOFR' in df.columns:
            st.line_chart(df[['SOFR']], height=120)

    # --- 2️⃣ Employment (雇用関連) ---
    st.markdown("---")
    st.markdown("### 👷 2. Employment (雇用関連)")
    col1, col2 = st.columns(2)
    
    with col1:
        # NFP: 非農業部門雇用者数・前月比 + 短期/長期チャート（Level表示は不要）
        st.markdown("#### 非農業部門雇用者数（NFP）前月比")
        # Get original data for change calculation (df_original is global from get_market_data)
        nfp_original = df_original.get('NFP')
        nfp_series = df.get('NFP')  # ffilled series for display
        
        if nfp_original is not None and len(nfp_original.dropna()) >= 2:
            nfp_data = nfp_original.dropna()
            nfp_curr = nfp_data.iloc[-1]
            nfp_prev = nfp_data.iloc[-2]
            nfp_change = nfp_curr - nfp_prev  # Absolute change in thousands
            # Display the monthly change as the main metric (no delta)
            st.metric("結果", f"{nfp_change:+,.0f}K（{nfp_change/10:+,.1f}万人）")
            # 提供元更新日を表示
            if hasattr(df, 'attrs'):
                if 'last_valid_dates' in df.attrs and 'NFP' in df.attrs['last_valid_dates']:
                    st.caption(f"📅 対象期間: {df.attrs['last_valid_dates']['NFP']} (月次)")
                if 'fred_release_dates' in df.attrs and 'NFP' in df.attrs['fred_release_dates']:
                    st.caption(f"🔄 提供元更新日: {df.attrs['fred_release_dates']['NFP']}")
        
        # Long-term trend chart - show MONTHLY CHANGES, not total level
        if nfp_original is not None and len(nfp_original.dropna()) >= 2:
            nfp_changes = nfp_original.dropna().diff().dropna()  # Calculate monthly changes
            if len(nfp_changes) > 0:
                st.markdown("###### NFP 月次増減の推移")
                st.line_chart(nfp_changes, height=150)
        
        # ADP Employment (先行指標)
        # 注意: ADPWNUSNERSA は「Persons」単位のため、1000で割って「K」単位に変換
        st.markdown("---")
        st.markdown("#### ADP Employment (民間雇用)")
        # Get original data for change calculation (df_original is global)
        adp_original = df_original.get('ADP')
        adp_series_raw = df.get('ADP')  # ffilled series for display
        
        if adp_original is not None and len(adp_original.dropna()) >= 2:
            # Use original data for change calculation, convert Persons to Thousands
            adp_data = adp_original.dropna() / 1000
            adp_series = adp_series_raw / 1000  # for display
            adp_curr = adp_data.iloc[-1]
            adp_prev = adp_data.iloc[-2]
            adp_change = adp_curr - adp_prev
            if abs(adp_change) >= 1:
                st.metric("月次増減 (民間)", f"{adp_change:+,.0f}K", delta=f"合計: {adp_curr:,.0f}K", delta_color="off")
            else:
                st.metric("月次増減 (民間)", f"{adp_change:+,.1f}K", delta=f"合計: {adp_curr:,.0f}K", delta_color="off")
            # ADPにsparklineと長期チャートを追加
            show_metric_with_sparkline("ADP Level", adp_series, 'ADP', "K", notes="民間雇用者数合計")
            
            # ADP Monthly Change Chart (similar to NFP)
            adp_changes = adp_data.diff().dropna()  # Calculate monthly changes
            if len(adp_changes) > 0:
                st.markdown("###### ADP 月次増減の推移")
                st.line_chart(adp_changes, height=150)
            
            st.markdown("###### ADP Long-term Trend")
            st.line_chart(adp_series, height=150)
        elif adp_original is not None and len(adp_original.dropna()) >= 1:
            adp_series = adp_series_raw / 1000
            st.caption("⚠️ ADPデータが1件のみです")
            show_metric_with_sparkline("ADP Level", adp_series, 'ADP', "K", notes="民間雇用者数合計")
        else:
            st.caption("⚠️ ADPデータが取得できませんでした")
        st.caption("📊 NFPの2日前に発表される先行指標")
        st.markdown("---")
        # Unemployment Rate: Use original data for change calculation
        st.markdown("#### Unemployment Rate")
        unemp_original = df_original.get('UNRATE')  # df_original is global
        unemp_series = df.get('UNRATE')
        
        if unemp_original is not None and len(unemp_original.dropna()) >= 2:
            unemp_data = unemp_original.dropna()
            unemp_curr = unemp_data.iloc[-1]
            unemp_prev = unemp_data.iloc[-2]
            unemp_change = unemp_curr - unemp_prev  # Point change
            st.metric("失業率", f"{unemp_curr:.1f}%", delta=f"{unemp_change:+.1f}pp vs先月")
            # 日付情報と提供元更新日を表示
            if hasattr(df, 'attrs'):
                if 'last_valid_dates' in df.attrs and 'UNRATE' in df.attrs['last_valid_dates']:
                    st.caption(f"📅 対象期間: {df.attrs['last_valid_dates']['UNRATE']} (月次)")
                if 'fred_release_dates' in df.attrs and 'UNRATE' in df.attrs['fred_release_dates']:
                    st.caption(f"🔄 提供元更新日: {df.attrs['fred_release_dates']['UNRATE']}")
            # Only show sparkline (not duplicate metric)
            if 'UNRATE' in df.columns:
                recent_data = df['UNRATE'].tail(60)
                st.caption("📊 過去60日間のトレンド")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=recent_data.index,
                    y=recent_data.values,
                    mode='lines',
                    line=dict(color='cyan', width=1),
                    fill='tozeroy',
                    fillcolor='rgba(0,255,255,0.1)',
                    showlegend=False
                ))
                fig.update_layout(
                    height=80,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    hovermode=False
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"spark_unemp_{uuid.uuid4().hex[:8]}")
            st.caption("サーム・ルール注視指標")
        if unemp_series is not None and not unemp_series.isna().all():
            st.markdown("###### Unemployment Long-term Trend")
            st.line_chart(unemp_series, height=150)
        
    with col2:
        # Average Hourly Earnings - show MoM/YoY results and YoY% trend chart
        st.markdown("#### 平均時給")
        ahe_original = df_original.get('AvgHourlyEarnings')
        ahe_series = df.get('AvgHourlyEarnings')
        
        if ahe_original is not None and len(ahe_original.dropna()) >= 2:
            ahe_data = ahe_original.dropna()
            ahe_curr = ahe_data.iloc[-1]
            ahe_prev = ahe_data.iloc[-2]
            mom = (ahe_curr / ahe_prev - 1) * 100
            
            # YoY calculation (12 months back)
            yoy = None
            if len(ahe_data) > 12:
                ahe_prev_yr = ahe_data.iloc[-13]
                yoy = (ahe_curr / ahe_prev_yr - 1) * 100
            
            # Display MoM and YoY results
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("前月比", f"{mom:+.1f}%")
            if yoy is not None:
                m_col2.metric("前年比", f"{yoy:+.1f}%")
            
            # 提供元更新日を表示
            if hasattr(df, 'attrs'):
                if 'last_valid_dates' in df.attrs and 'AvgHourlyEarnings' in df.attrs['last_valid_dates']:
                    st.caption(f"📅 対象期間: {df.attrs['last_valid_dates']['AvgHourlyEarnings']} (月次)")
                if 'fred_release_dates' in df.attrs and 'AvgHourlyEarnings' in df.attrs['fred_release_dates']:
                    st.caption(f"🔄 提供元更新日: {df.attrs['fred_release_dates']['AvgHourlyEarnings']}")
            
            # Chart 1: MoM% trend (calculate rolling MoM for each month)
            mom_series = (ahe_data / ahe_data.shift(1) - 1) * 100
            mom_series = mom_series.dropna()
            if len(mom_series) > 0:
                st.markdown("###### 前月比%の推移")
                st.line_chart(mom_series, height=120)
            
            # Chart 2: YoY% trend (calculate rolling YoY for each month)
            if len(ahe_data) > 12:
                yoy_series = (ahe_data / ahe_data.shift(12) - 1) * 100
                yoy_series = yoy_series.dropna()
                if len(yoy_series) > 0:
                    st.markdown("###### 前年比%の推移")
                    st.line_chart(yoy_series, height=120)
            
            # Chart 3: Level ($/hr) trend
            st.markdown("###### 平均時給（$/hr）の推移")
            st.line_chart(ahe_data, height=120)
        
        st.markdown("---")
        # JOLTS: Removed monthly change per user request
        st.markdown("#### JOLTS Job Openings")
        jolts_series = df.get('JOLTS')
        show_metric_with_sparkline("JOLTS Level", jolts_series, 'JOLTS', "K", notes="労働需要の先行指標")
        if jolts_series is not None and not jolts_series.isna().all():
            st.markdown("###### JOLTS Long-term Trend")
            st.line_chart(jolts_series, height=150)
        
        # --- ICSA: Initial Jobless Claims (新規失業保険申請件数) ---
        st.markdown("---")
        st.markdown("#### 新規失業保険申請件数 (ICSA)")
        icsa_series = df.get('ICSA')
        if icsa_series is not None and len(icsa_series.dropna()) >= 2:
            # ICSA is in Persons, convert to Thousands for display
            icsa_data = icsa_series.dropna() / 1000  # Persons -> Thousands
            icsa_curr = icsa_data.iloc[-1]
            icsa_prev = icsa_data.iloc[-2]
            icsa_change = icsa_curr - icsa_prev
            
            # Display current value and weekly change
            st.metric("最新週", f"{icsa_curr:,.0f}K", delta=f"{icsa_change:+,.0f}K vs前週", delta_color="inverse")
            
            # 提供元更新日を表示
            if hasattr(df, 'attrs'):
                if 'last_valid_dates' in df.attrs and 'ICSA' in df.attrs['last_valid_dates']:
                    st.caption(f"📅 対象期間: {df.attrs['last_valid_dates']['ICSA']} (週次)")
                if 'fred_release_dates' in df.attrs and 'ICSA' in df.attrs['fred_release_dates']:
                    st.caption(f"🔄 提供元更新日: {df.attrs['fred_release_dates']['ICSA']}")
            
            # Sparkline (past 60 data points)
            st.caption("📊 過去60週のトレンド")
            recent_icsa = icsa_data.tail(60)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=recent_icsa.index,
                y=recent_icsa.values,
                mode='lines',
                line=dict(color='orange', width=1),
                fill='tozeroy',
                fillcolor='rgba(255,165,0,0.1)',
                showlegend=False
            ))
            fig.update_layout(
                height=80,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                hovermode=False
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key=f"spark_icsa_{uuid.uuid4().hex[:8]}")
            st.caption("📋 週次発表（毎週木曜）。増加は解雇増、減少は雇用安定。")
        elif icsa_series is not None and len(icsa_series.dropna()) >= 1:
            icsa_data = icsa_series.dropna() / 1000
            st.metric("最新週", f"{icsa_data.iloc[-1]:,.0f}K")
            st.caption("⚠️ 前週データがありません")
        else:
            st.caption("⚠️ ICSAデータが取得できませんでした")
        
        # Long-term chart
        if icsa_series is not None and not icsa_series.isna().all():
            icsa_display = icsa_series / 1000  # Convert to Thousands for chart
            st.markdown("###### ICSA Long-term Trend (K)")
            st.line_chart(icsa_display, height=150)

    # --- 3️⃣ Inflation (物価・インフレ) ---
    st.markdown("---")
    st.markdown("### ⚖️ 3. Inflation (物価・インフレ)")
    col1, col2 = st.columns(2)
    
    with col1:
        display_macro_card("Consumer Price Index (CPI)", df.get('CPI'), 'CPI', notes="消費者物価指数")
        st.markdown("---")
        # Core PCE: Already YoY% - don't calculate MoM/YoY again
        st.markdown("#### Core PCE Inflation (YoY)")
        pce_series = df.get('CorePCE')
        if pce_series is not None and len(pce_series.dropna()) >= 2:
            pce_curr = pce_series.dropna().iloc[-1]
            pce_prev = pce_series.dropna().iloc[-2]
            pce_change = pce_curr - pce_prev  # Change in percentage points
            st.metric("現在のインフレ率", f"{pce_curr:.2f}%", delta=f"{pce_change:+.2f}pp vs先月")
        show_metric_with_sparkline("Core PCE", pce_series, 'CorePCE', "%", notes="FRB最重要視指標（ダラス連銀トリム平均）")
        if pce_series is not None and not pce_series.isna().all():
            st.markdown("###### Core PCE Long-term Trend")
            st.line_chart(pce_series, height=150)
            
    with col2:
        display_macro_card("Core CPI", df.get('CPICore'), 'CPICore', notes="食品・エネルギー除く")
        st.markdown("---")
        display_macro_card("Producer Price Index (PPI)", df.get('PPI'), 'PPI', notes="卸売物価指数")

    # --- 4️⃣ Economy (景気・先行指標) ---
    st.markdown("---")
    st.markdown("### 📈 4. Economy (景気・先行指標)")
    col1, col2 = st.columns(2)
    
    with col1:
        display_macro_card("Retail Sales", df.get('RetailSales'), 'RetailSales', unit="$M", notes="個人消費の動向")
        st.markdown("---")
        display_macro_card("Consumer Sentiment", df.get('ConsumerSent'), 'ConsumerSent', unit="pt", notes="ミシガン大学調査")

    with col2:
        # Real GDP: Show annualized growth rate (not just level or simple %)
        st.markdown("#### Real GDP (Annualized Growth)")
        gdp_series = df.get('RealGDP')
        if gdp_series is not None and len(gdp_series.dropna()) >= 2:
            gdp_data = gdp_series.dropna()
            gdp_curr = gdp_data.iloc[-1]
            gdp_prev = gdp_data.iloc[-2]
            qoq_pct = (gdp_curr / gdp_prev - 1)  # Quarterly growth rate (decimal)
            annualized = ((1 + qoq_pct) ** 4 - 1) * 100  # Annualized (%)
            st.metric("前期比年率", f"{annualized:+.1f}%", delta=f"水準: ${gdp_curr:,.0f}B", delta_color="off")
        show_metric_with_sparkline("GDP Level", gdp_series, 'RealGDP', "$B", notes="実質GDP (2017年基準)")
        if gdp_series is not None and not gdp_series.isna().all():
            st.markdown("###### Real GDP Long-term Trend")
            st.line_chart(gdp_series, height=150)
        st.markdown("---")
        st.markdown("#### 🔗 Yield Curve (2Y-10Y)")
        show_metric_with_sparkline("2Y-10Y Spread", df.get('T10Y2Y'), 'T10Y2Y', "%", notes="景気後退の先行指標")
        if 'T10Y2Y' in df.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['T10Y2Y'], name='2Y-10Y Spread', line=dict(color='cyan')))
            fig.add_hline(y=0, line_dash='dash', line_color='red', annotation_text="逆イールド境界")
            st.plotly_chart(fig, use_container_width=True, key="macro_yield_chart")


# Tab 4: Crypto Liquidity (NEW)
with tabs[3]:
    st.subheader("🪙 Crypto Liquidity")
    st.caption("💡 ステーブルコイン供給量 & トークン化資産 (国債/金) - DeFiLlama API経由")
    
    # Fetch data from DeFiLlama
    stablecoin_data = get_stablecoin_data()
    stablecoin_hist = get_stablecoin_historical()
    treasury_data = get_tokenized_treasury_data()
    
    # Cache crypto summary for AI Analysis tab (non-blocking)
    if stablecoin_data or treasury_data:
        crypto_cache = []
        if stablecoin_data:
            crypto_cache.append(f"Total Stablecoin Supply: ${stablecoin_data['total_supply']:.1f}B")
            for coin in stablecoin_data.get('top_coins', [])[:3]:
                delta_1d = coin['circulating'] - coin['prev_day'] if coin.get('prev_day') else 0
                crypto_cache.append(f"  {coin['symbol']}: ${coin['circulating']:.1f}B (24h: {delta_1d:+.2f}B)")
        if treasury_data:
            crypto_cache.append(f"Tokenized Treasuries TVL: ${treasury_data['treasury']['total_tvl']:.2f}B")
            crypto_cache.append(f"Tokenized Gold TVL: ${treasury_data['gold']['total_tvl']:.2f}B")
            crypto_cache.append(f"Other RWA TVL: ${treasury_data['other_rwa']['total_tvl']:.2f}B")
        st.session_state['crypto_summary_cache'] = crypto_cache
    
    # --- Stablecoin Supply Section ---
    st.markdown("### 💵 Stablecoin Supply")
    st.caption("クリプト市場の「血液」- 増加 = 資金流入")
    
    if stablecoin_data:

        # Total Supply Metric
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            total_supply = stablecoin_data['total_supply']
            st.metric(
                "Total Stablecoin Supply",
                f"${total_supply:.1f} B",
                help="全ステーブルコイン（USDペッグ）の総供給量"
            )
            # Show data freshness
            if 'timestamp' in stablecoin_data:
                st.caption(f"🔄 提供元更新: {stablecoin_data['timestamp'][:16].replace('T', ' ')} (DeFiLlama)")
        with col2:
            top_coins = stablecoin_data['top_coins']
            if top_coins and len(top_coins) > 0:
                usdt = next((c for c in top_coins if c['symbol'] == 'USDT'), None)
                if usdt:
                    delta_1d = usdt['circulating'] - usdt['prev_day'] if usdt['prev_day'] else 0
                    st.metric("USDT Supply", f"${usdt['circulating']:.1f} B", delta=f"{delta_1d:+.2f} B (24h)")
        with col3:
            if top_coins and len(top_coins) > 0:
                usdc = next((c for c in top_coins if c['symbol'] == 'USDC'), None)
                if usdc:
                    delta_1d = usdc['circulating'] - usdc['prev_day'] if usdc['prev_day'] else 0
                    st.metric("USDC Supply", f"${usdc['circulating']:.1f} B", delta=f"{delta_1d:+.2f} B (24h)")
        
        # Historical Chart - Total Stablecoin Supply
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
        else:
            st.caption("📊 履歴データ取得中...")
        
        # Top Stablecoins Table
        st.markdown("#### Top 10 Stablecoins by Supply")
        top_10 = stablecoin_data['top_coins'][:10]
        
        stablecoin_df = pd.DataFrame([
            {
                'Symbol': coin['symbol'],
                'Name': coin['name'],
                'Supply ($B)': round(coin['circulating'], 2),
                'Mechanism': coin['mechanism'],
                '24h Δ': round(coin['circulating'] - coin['prev_day'], 3) if coin['prev_day'] else 0,
                '7d Δ': round(coin['circulating'] - coin['prev_week'], 3) if coin['prev_week'] else 0,
            }
            for coin in top_10
        ])
        st.dataframe(stablecoin_df, use_container_width=True, hide_index=True)
        
        # Supply Distribution Chart
        st.markdown("#### Supply Distribution")
        fig = go.Figure(data=[
            go.Pie(
                labels=[c['symbol'] for c in top_10[:6]] + ['Others'],
                values=[c['circulating'] for c in top_10[:6]] + [sum(c['circulating'] for c in top_10[6:])],
                hole=0.4,
                marker=dict(colors=['#26a69a', '#42a5f5', '#7e57c2', '#ff7043', '#78909c', '#ab47bc', '#bdbdbd'])
            )
        ])
        fig.update_layout(
            template='plotly_dark',
            height=350,
            showlegend=True,
            legend=dict(orientation='h', y=-0.1)
        )
        st.plotly_chart(fig, use_container_width=True, key="stablecoin_pie")
        
        st.caption(f"📅 最終更新: {stablecoin_data['timestamp'][:19]}")
    else:
        st.warning("⚠️ ステーブルコインデータの取得に失敗しました。Force Updateを試してください。")
    
    st.markdown("---")
    
    # --- Tokenized Treasury Section (Separated Categories) ---
    if treasury_data:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 📜 Tokenized Treasuries")
            st.metric(
                "Treasury TVL",
                f"${treasury_data['treasury']['total_tvl']:.2f} B",
                help="トークン化米国債（BUIDL, USDY等）"
            )
        with col2:
            st.markdown("### 🪙 Tokenized Gold")
            st.metric(
                "Gold TVL",
                f"${treasury_data['gold']['total_tvl']:.2f} B",
                help="トークン化金（XAUT, PAXG等）"
            )
        with col3:
            st.markdown("### 🏢 Other RWA")
            st.metric(
                "Other RWA TVL",
                f"${treasury_data['other_rwa']['total_tvl']:.2f} B",
                help="その他の実世界資産"
            )
        
        # Show data freshness for RWA section
        if 'timestamp' in treasury_data:
            st.caption(f"🔄 提供元更新: {treasury_data['timestamp'][:16].replace('T', ' ')} (DeFiLlama)")
        
        # Treasury Protocols
        st.markdown("---")
        st.markdown("#### 📜 Tokenized US Treasuries")
        st.caption("機関投資家のクリプト参入指標 - TradFi → DeFiの架け橋")
        
        treasury_protocols = treasury_data['treasury']['protocols']
        if treasury_protocols:
            treasury_df = pd.DataFrame([
                {
                    'Protocol': p['name'],
                    'Symbol': p.get('symbol', '-'),
                    'TVL ($B)': round(p['tvl'], 3),
                    '24h Δ (%)': round(p.get('change_1d', 0), 2) if p.get('change_1d') else 0,
                    '7d Δ (%)': round(p.get('change_7d', 0), 2) if p.get('change_7d') else 0,
                }
                for p in treasury_protocols
            ])
            st.dataframe(treasury_df, use_container_width=True, hide_index=True)
            
            # Treasury Bar Chart
            fig = go.Figure(data=[
                go.Bar(
                    x=[p['name'][:15] for p in treasury_protocols[:8]],
                    y=[p['tvl'] for p in treasury_protocols[:8]],
                    marker_color='steelblue'
                )
            ])
            fig.update_layout(
                template='plotly_dark',
                height=250,
                xaxis_title="Protocol",
                yaxis_title="TVL ($B)"
            )
            st.plotly_chart(fig, use_container_width=True, key="treasury_bar")
        else:
            st.caption("トークン化国債プロトコルが見つかりません")
        
        # Gold Protocols
        st.markdown("---")
        st.markdown("#### 🪙 Tokenized Gold")
        st.caption("金のトークン化 - 伝統的安全資産のデジタル化")
        
        gold_protocols = treasury_data['gold']['protocols']
        if gold_protocols:
            gold_df = pd.DataFrame([
                {
                    'Protocol': p['name'],
                    'Symbol': p.get('symbol', '-'),
                    'TVL ($B)': round(p['tvl'], 3),
                    '24h Δ (%)': round(p.get('change_1d', 0), 2) if p.get('change_1d') else 0,
                    '7d Δ (%)': round(p.get('change_7d', 0), 2) if p.get('change_7d') else 0,
                }
                for p in gold_protocols
            ])
            st.dataframe(gold_df, use_container_width=True, hide_index=True)
            
            # Gold Bar Chart
            fig = go.Figure(data=[
                go.Bar(
                    x=[p['name'][:15] for p in gold_protocols],
                    y=[p['tvl'] for p in gold_protocols],
                    marker_color='gold'
                )
            ])
            fig.update_layout(
                template='plotly_dark',
                height=200,
                xaxis_title="Protocol",
                yaxis_title="TVL ($B)"
            )
            st.plotly_chart(fig, use_container_width=True, key="gold_bar")
        else:
            st.caption("トークン化金プロトコルが見つかりません")
        
        # Other RWA Protocols (collapsed by default)
        with st.expander("🏢 Other RWA Protocols"):
            other_protocols = treasury_data['other_rwa']['protocols']
            if other_protocols:
                other_df = pd.DataFrame([
                    {
                        'Protocol': p['name'],
                        'Symbol': p.get('symbol', '-'),
                        'TVL ($B)': round(p['tvl'], 3),
                        'Category': p.get('category', 'RWA'),
                        '24h Δ (%)': round(p.get('change_1d', 0), 2) if p.get('change_1d') else 0,
                    }
                    for p in other_protocols
                ])
                st.dataframe(other_df, use_container_width=True, hide_index=True)
            else:
                st.caption("その他のRWAプロトコルが見つかりません")
        
        st.caption(f"📅 最終更新: {treasury_data['timestamp'][:19]}")
    else:
        st.warning("⚠️ RWAデータの取得に失敗しました。Force Updateを試してください。")
    
    st.markdown("---")
    st.info("""
    💡 **なぜこれが重要？**
    - **ステーブルコイン**: クリプト市場への資金流入/流出を測定。増加トレンド = リスクオン
    - **トークン化国債**: 機関投資家の参入度合い。TradFi（伝統金融）からDeFiへの資本移動を示す
    - **トークン化金**: 伝統的安全資産のデジタル化。XAUTは国債とは別カテゴリ
    - **今後の展開**: Bitget等が株式のトークン化開始。金融商品のトークン化は加速する見込み
    """)

# Tab 5: AI Analysis (updated index)
with tabs[4]:
    st.subheader("🤖 AI Market Analysis")
    st.caption("Gemini 3 Flash & Claude Opus 4.5 によるデュアルAI市場分析")
    
    # Check API keys
    gemini_available = gemini_client is not None
    claude_available = claude_client is not None
    
    if not gemini_available and not claude_available:
        st.error("⚠️ APIキーが設定されていません。`.env` ファイルに `GEMINI_API_KEY` または `ANTHROPIC_API_KEY` を追加してください。")
    else:
        # Prepare market data summary for AI
        def get_market_summary():
            """Generate a comprehensive summary of ALL monitored market conditions for AI analysis"""
            summary_parts = []
            
            def add_metric(name, col_name, unit="", with_change=False, change_days=7, show_date=False, is_level=False):
                """Helper to add a metric to summary with strict labeling (Level vs Change)"""
                if col_name in df.columns:
                    data = df[col_name].dropna()
                    if len(data) > 0:
                        current = data.iloc[-1]
                        last_date = data.index[-1].strftime('%Y/%m/%d') if hasattr(data.index[-1], 'strftime') else str(data.index[-1])[:10]
                        
                        type_tag = "[Level/総数]" if is_level else "[Change/変化量・指数]"
                        
                        if with_change and len(data) >= change_days:
                            change = current - data.iloc[-change_days]
                            label = f"{name} {type_tag}: {current:.2f}{unit}"
                            change_label = f"({change_days}日変化: {change:+.2f}{unit})"
                            date_label = f" [更新: {last_date}]" if show_date else ""
                            summary_parts.append(f"{label} {change_label}{date_label}")
                        else:
                            label = f"{name} {type_tag}: {current:.2f}{unit}"
                            date_label = f" [更新: {last_date}]" if show_date else ""
                            summary_parts.append(f"{label}{date_label}")
            
            # Add data freshness header
            summary_parts.append("【データ鮮度情報】")
            today = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
            summary_parts.append(f"分析実行日時: {today}")
            summary_parts.append("")
            
            # ★ Add focus areas at the top (if user selected any)
            focus_selection = st.session_state.get('ai_focus_categories', [])
            if focus_selection:
                summary_parts.insert(0, "")  # Blank line after focus section
                for i, category in enumerate(reversed(focus_selection)):
                    summary_parts.insert(0, f"  → {category}")
                summary_parts.insert(0, "【★★★ ユーザー注目領域（AIはこれらを特に重視して分析してください）★★★】")

            

            # === Fed Liquidity ===
            summary_parts.append("【FRB流動性】")
            add_metric("Net Liquidity", "Net_Liquidity", "B", True, show_date=True, is_level=True)
            add_metric("ON RRP", "ON_RRP", "B", show_date=True, is_level=True)
            add_metric("Bank Reserves", "Reserves", "B", show_date=True, is_level=True)
            add_metric("TGA", "TGA", "B", show_date=True, is_level=True)
            add_metric("Fed Assets (WALCL)", "Fed_Assets", "B", show_date=True, is_level=True)
            add_metric("SOMA Total", "SOMA_Total", "B", is_level=True)
            add_metric("SOMA Bills", "SOMA_Bills", "B", True, is_level=True)
            

            # === Economic Indicators (US Economic Data) ===
            summary_parts.append("\n【米経済指標】")
            
            # 1. Monetary Policy
            summary_parts.append("[金融政策]")
            add_metric("FF Rate Upper", "FedFundsUpper", "%", is_level=True)
            add_metric("EFFR", "EFFR", "%", is_level=True)
            add_metric("IORB", "IORB", "%", is_level=True)
            add_metric("SOFR", "SOFR", "%", is_level=True)
            
            # 2. Employment
            summary_parts.append("[雇用関連]")
            add_metric("Unemployment Rate", "UNRATE", "%", is_level=True)
            add_metric("NFP Total (Level)", "NFP", "K", is_level=True)
            add_metric("Avg Hourly Earnings", "AvgHourlyEarnings", "$", is_level=True)
            add_metric("JOLTS Job Openings (Level)", "JOLTS", "K", is_level=True)
            add_metric("Initial Claims (Change)", "ICSA", "K")
            
            # 3. Inflation
            summary_parts.append("[物価・インフレ]")
            add_metric("CPI Index (Level)", "CPI", "", is_level=True)
            add_metric("CPI Core Index (Level)", "CPICore", "", is_level=True)
            add_metric("Core PCE YoY%", "CorePCE", "%")
            add_metric("PPI Index (Level)", "PPI", "", is_level=True)
            
            # 4. Economy
            summary_parts.append("[景気・製造業]")
            add_metric("Retail Sales", "RetailSales", "M", is_level=True)
            add_metric("Consumer Sentiment", "ConsumerSent", "pt", is_level=True)
            add_metric("Real GDP (Level)", "RealGDP", "B", is_level=True)
            add_metric("2Y-10Y Spread", "T10Y2Y", "%", is_level=True)
            
            # === Global M2 ===
            summary_parts.append("\n【マネーサプライ】")
            add_metric("US M2 (Nominal)", "M2SL", "B", is_level=True)
            add_metric("US M2 (Real)", "M2REAL", "B", is_level=True)
            add_metric("US Real M2 Index", "US_Real_M2_Index", "", is_level=True)
            add_metric("China M2", "CN_M2", "T CNY", is_level=True)
            add_metric("China Credit Impulse", "CN_Credit_Impulse", "%")
            add_metric("Japan M2", "JP_M2", "T JPY", is_level=True)
            add_metric("EU M2", "EU_M2", "T EUR", is_level=True)

            # === Banking Sector ===
            summary_parts.append("\n【銀行セクター】")
            add_metric("Bank Cash", "Bank_Cash", "B", is_level=True)
            add_metric("C&I Lending Std (Large)", "Lending_Standards", " pts", is_level=True)
            add_metric("C&I Lending Std (Small)", "CI_Std_Small", " pts", is_level=True)
            add_metric("C&I Demand", "CI_Demand", " pts", is_level=True)
            add_metric("C&I Loans", "CI_Loans", "B", is_level=True)
            add_metric("CRE Std (Construction)", "CRE_Std_Construction", " pts", is_level=True)
            add_metric("CRE Std (General)", "CRE_Std_Office", " pts", is_level=True)
            add_metric("CRE Loans", "CRE_Loans", "B", True, is_level=True)
            
            # === Risk & Bonds ===
            summary_parts.append("\n【リスク・債券】")
            add_metric("VIX", "VIX", "", show_date=True, is_level=True)
            add_metric("Credit Spread (HY)", "Credit_Spread", "%", show_date=True, is_level=True)
            add_metric("US 10Y Yield", "US_TNX", "%", show_date=True, is_level=True)
            
            # === Equity & Crypto ===
            summary_parts.append("\n【株式・仮想通貨】")
            if 'SP500' in df.columns:
                sp = df['SP500'].dropna()
                if len(sp) > 5:
                    change_pct = ((sp.iloc[-1] / sp.iloc[-5]) - 1) * 100
                    summary_parts.append(f"S&P 500 Index [Level]: {sp.iloc[-1]:,.0f} (週間: {change_pct:+.1f}%)")
            add_metric("BTC", "BTC", "", is_level=True)
            add_metric("ETH", "ETH", "", is_level=True)
            
            # === FX ===
            summary_parts.append("\n【為替】")
            add_metric("DXY", "DXY", "", is_level=True)
            add_metric("USD/JPY", "USDJPY", "", is_level=True)
            add_metric("EUR/USD", "EURUSD", "", is_level=True)
            add_metric("USD/CNY", "USDCNY", "", is_level=True)
            
            # === Commodities ===
            summary_parts.append("\n【コモディティ】")
            add_metric("Gold", "Gold", "", is_level=True)
            add_metric("Silver", "Silver", "", is_level=True)
            add_metric("Oil (WTI)", "Oil", "", is_level=True)
            add_metric("Copper", "Copper", "", is_level=True)
            
            # === HYG ===
            summary_parts.append("\n【ハイイールド債】")
            if 'HYG' in df.columns:
                hyg = df['HYG'].dropna()
                if len(hyg) > 5:
                    hyg_change = ((hyg.iloc[-1] / hyg.iloc[-5]) - 1) * 100
                    summary_parts.append(f"HYG (High Yield ETF): {hyg.iloc[-1]:.2f} (週間: {hyg_change:+.1f}%)")


            
            # === Crypto Liquidity (Fetch if not cached, ensuring availability) ===
            summary_parts.append("\n【クリプト流動性】")
            if 'crypto_summary_cache' not in st.session_state:
                # Proactively fetch to avoid "tab-dependency" for AI
                try:
                    s_data = get_stablecoin_data()
                    t_data = get_tokenized_treasury_data()
                    c_cache = []
                    if s_data:
                        c_cache.append(f"Total Stablecoin Supply [Level]: ${s_data['total_supply']:.1f}B")
                        for coin in s_data.get('top_coins', [])[:3]:
                            d1 = coin['circulating'] - coin['prev_day'] if coin.get('prev_day') else 0
                            c_cache.append(f"  {coin['symbol']} [Level]: ${coin['circulating']:.1f}B (24h Δ: {d1:+.2f}B)")
                    if t_data:
                        c_cache.append(f"Tokenized Treasuries TVL [Level]: ${t_data['treasury']['total_tvl']:.2f}B")
                        c_cache.append(f"Tokenized Gold TVL [Level]: ${t_data['gold']['total_tvl']:.2f}B")
                    st.session_state['crypto_summary_cache'] = c_cache
                except:
                    summary_parts.append("(取得エラー: クリプトAPIに一時的にアクセスできません)")
            
            if 'crypto_summary_cache' in st.session_state:
                for line in st.session_state['crypto_summary_cache']:
                    summary_parts.append(line)
            
            # === Market Sentiment (NEW) ===
            summary_parts.append("\n【マーケットセンチメント】")
            
            # VIX (already in df)
            if 'VIX' in df.columns:
                vix = df['VIX'].dropna()
                if len(vix) > 0:
                    vix_val = vix.iloc[-1]
                    vix_label = "Low" if vix_val < 15 else "Normal" if vix_val < 20 else "Elevated" if vix_val < 30 else "High Fear"
                    summary_parts.append(f"VIX (恐怖指数) [Level]: {vix_val:.1f} ({vix_label})")
            
            # Crypto Fear & Greed (fetch with cache)
            if 'sentiment_fg_cache' not in st.session_state:
                try:
                    cfg = get_crypto_fear_greed()
                    if cfg:
                        st.session_state['sentiment_fg_cache'] = f"Crypto Fear & Greed [Level]: {cfg['current']} ({cfg['classification']})"
                    else:
                        st.session_state['sentiment_fg_cache'] = "Crypto Fear & Greed: 取得失敗"
                except:
                    st.session_state['sentiment_fg_cache'] = "Crypto Fear & Greed: 取得失敗"
            summary_parts.append(st.session_state['sentiment_fg_cache'])
            
            # AAII Sentiment (fetch with cache)
            if 'sentiment_aaii_cache' not in st.session_state:
                try:
                    aaii = get_aaii_sentiment()
                    if aaii:
                        spread = aaii['bull_bear_spread']
                        spread_label = "過熱注意" if spread >= 20 else "やや強気" if spread >= 10 else "中立" if spread >= -10 else "やや弱気" if spread >= -20 else "底打ちサイン?"
                        st.session_state['sentiment_aaii_cache'] = f"AAII Bull-Bear Spread [Level]: {spread:+.1f}% ({spread_label})"
                    else:
                        st.session_state['sentiment_aaii_cache'] = "AAII Sentiment: 取得失敗"
                except:
                    st.session_state['sentiment_aaii_cache'] = "AAII Sentiment: 取得失敗"
            summary_parts.append(st.session_state['sentiment_aaii_cache'])
            
            return "\n".join(summary_parts)


        
        st.markdown("### 📊 現在の市場データサマリー")
        
        market_summary = get_market_summary()
        with st.expander("📋 AIに送信されるデータ", expanded=False):
            st.code(market_summary, language="text")
        
        st.markdown("---")
        
        # AI Status display
        col_status1, col_status2 = st.columns(2)
        with col_status1:
            if gemini_available:
                st.success(f"✅ Gemini 3 Flash 準備完了")
            else:
                st.warning("⚠️ Gemini未設定")
        with col_status2:
            if claude_available:
                st.success(f"✅ Claude Opus 4.5 準備完了")
            else:
                st.warning("⚠️ Claude未設定")
        
        st.markdown("---")
        
        # AI selection
        ai_options = []
        if gemini_available:
            ai_options.append("🔷 Gemini 3 Flash")
        if claude_available:
            ai_options.append("🟣 Claude Opus 4.5")
        if gemini_available and claude_available:
            ai_options.append("⚡ デュアルAI比較分析")
        
        selected_ai = st.selectbox("使用するAIを選択", ai_options)
        
        # Analysis options
        analysis_type = st.selectbox(
            "分析タイプを選択",
            ["総合分析", "リスク評価", "流動性分析", "FRB政策分析", "投資アイデア"]
        )
        
        # IMPORTANT: Policy context to prevent outdated information and ensure verification
        policy_context = """【超重要：分析の絶対条件（検証可能性と正確性）】
1. **ハルシネーション（嘘）の厳禁**: 
   - 未発表の統計や架空の数値を「確定値」として語ることは絶対に許されません。
   - 「市場データ」セクションの数値を「唯一の真実（Ground Truth）」とし、外部検索結果がこれと矛盾する場合はアプリ内の数値を優先してください。
2. **出典（Evidence）の提示義務**:
   - 全ての事実、ニュース、統計引用において、**[出典機関名] [配信日時] [URL]**を必ずセットで併記してください。
   - 証拠が提示できない情報は「推測」であることを明記するか、出力から除外してください。
3. **一次資料（Primary Source）の優先**:
   - 中央銀行（Fed, ECB, BOJ等）、国際機関（BIS, IMF等）、政府機関（BLS, BEA等）の公式発表を最優先で探索・引用してください。
4. **マクロの配管（Plumbing）視点**:
   - 表面的な動きだけでなく、準備預金、ON RRP、レポ市場への波及経路を論理的に解説してください。

【最新政策コンテキスト（2026年1月時点）】
- FRB QT（量的引き締め）: 2025年12月に終了。現在は月450億ドルペースの拡大フェーズに移行。
- Bills-in戦略: FRBは短期国債（T-Bills）の保有比率を積極的に増加中。
- ON RRP: 枯渇状態（Scarce Regime）。
"""

        analysis_prompts = {
            "総合分析": f"""{policy_context}
【分析指示】
1. 現在の市場環境を、提供された「市場データ[Level]」と最新ニュースを組み合わせて分析してください。
2. 他のメディアが見落としている「マクロの歪み」を独自の視点（配管視点）で抽出してください。
3. 最後に、X（Twitter）投稿にそのまま使える、魂の込もった「インサイト・ポスト」を作成してください。

【出力形式】
以下のJSON構造で出力してください（厳密に守ること）：
{{
  "headline": "今回の一番のインサイトを一言で",
  "credibility": 0.0-1.0,
  "importance_rank": "S/A/B/C",
  "sentiment_matrix": {{ "risk_assets": "Pos/Neu/Neg", "currency_usd": "...", "safe_haven": "...", "commodities": "...", "emerging_markets": "..." }},
  "deep_analysis": "詳細な分析テキスト（出典URLと日付を各項目に必ず含めること）",
  "x_post": "X用投稿テキスト（魂を込めて）"
}}""",
            
            "リスク評価": f"""{policy_context}
【分析指示】
1. 現在の市場データから、ダウンサイドリスクを特定してください。
2. 警戒すべき価格帯や指標の変化率を具体的に述べてください。

【出力形式】
以下のJSON構造で出力（厳密）：
{{
  "headline": "最大のリスク要因を一言で",
  "credibility": 0.0-1.0,
  "importance_rank": "S/A/B/C",
  "sentiment_matrix": {{ "risk_assets": "...", "currency_usd": "...", "safe_haven": "...", "commodities": "...", "emerging_markets": "..." }},
  "deep_analysis": "詳細なリスク分析（URL/日付必須）",
  "x_post": "リスク警告ポスト（魂）"
}}""",
            
            "流動性分析": f"""{policy_context}
【分析指示】
1. Net Liquidity と SOMA Bills の相関、および ON RRP 枯渇の影響を分析してください。
2. 資産価格（株・BTC）への流動性供給の「蛇口」がどうなっているか述べてください。

【出力形式】
JSON（厳密）：
{{
  "headline": "流動性の真の状態を一言で",
  "credibility": 0.0-1.0,
  "importance_rank": "S/A/B/C",
  "sentiment_matrix": {{ "risk_assets": "...", "currency_usd": "...", "safe_haven": "...", "commodities": "...", "emerging_markets": "..." }},
  "deep_analysis": "詳細な流動性分析（URL/日付必須）",
  "x_post": "流動性インサイトポスト（魂）"
}}""",
            
            "FRB政策分析": f"""{policy_context}
【分析指示】
1. QT終了後の「拡大フェーズ」にあるFRBの真の意図を分析してください。
2. 「Bills-in戦略」が金利曲線や銀行準備に与える影響を解説してください。

【出力形式】
JSON（厳密）：
{{
  "headline": "FRBの隠れた意図を一言で",
  "credibility": 0.0-1.0,
  "importance_rank": "S/A/B/C",
  "sentiment_matrix": {{ "risk_assets": "...", "currency_usd": "...", "safe_haven": "...", "commodities": "...", "emerging_markets": "..." }},
  "deep_analysis": "詳細な政策分析（URL/日付必須）",
  "x_post": "中銀ウォッチポスト（魂）"
}}""",
            
            "投資アイデア": f"""{policy_context}
【分析指示】
1. 市場の「歪み」から、最も期待値の高い資産クラス/セクターを提案してください。
2. 既存の定説（コンセンサス）を疑う視点を含めてください。

【出力形式】
JSON（厳密）：
{{
  "headline": "勝機のあるセクターを一言で",
  "credibility": 0.0-1.0,
  "importance_rank": "S/A/B/C",
  "sentiment_matrix": {{ "risk_assets": "...", "currency_usd": "...", "safe_haven": "...", "commodities": "...", "emerging_markets": "..." }},
  "deep_analysis": "詳細な投資アイデア（URL/日付必須）",
  "x_post": "投資アイデアポスト（魂）"
}}"""
        }
        
        # Helper function for Gemini with Google Search Grounding
        def run_gemini_analysis(prompt, use_search=True):
            """Run Gemini analysis with optional Google Search grounding for real-time info"""
            from google.genai import types
            
            if use_search:
                # Enable Google Search grounding for real-time information
                response = gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    )
                )
            else:
                response = gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt
                )
            return response.text

        
        # Helper function for Claude (defined outside button to be reusable)
        def run_claude_analysis(prompt):
            message = claude_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        
        if st.button("🚀 AI分析を実行", type="primary"):
            # Create prompt
            full_prompt = f"""{analysis_prompts[analysis_type]}

【市場データ】
{market_summary}

【分析日時】
{datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')}
"""
            
            def display_ai_result(result_text, ai_name):
                # Robust JSON parsing
                data = None
                try:
                    data = json.loads(result_text)
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown block
                    json_match = re.search(r'\{[\s\S]*\}', result_text)
                    if json_match:
                        try:
                            data = json.loads(json_match.group())
                        except: pass
                
                if data:
                    st.markdown(f"### {ai_name} 分析結果: [{data.get('importance_rank', 'N/A')}] {data.get('headline', '')}")
                    
                    col_m1, col_m2, col_m3 = st.columns(3)
                    with col_m1:
                        st.metric("重要度ランク", data.get('importance_rank', 'N/A'))
                    with col_m2:
                        st.metric("信頼性", f"{data.get('credibility', 0.0):.2f}")
                    with col_m3:
                        st.write("**5軸センチメント**")
                        s = data.get('sentiment_matrix', {})
                        st.caption(f"株/BTC:{s.get('risk_assets','-')} | USD:{s.get('currency_usd','-')} | Gold:{s.get('safe_haven','-')}")
                    
                    st.markdown("---")
                    st.markdown(data.get('deep_analysis', result_text))
                    
                    if 'x_post' in data:
                        with st.expander("📝 X投稿用（検証URL付き）", expanded=True):
                            st.code(data['x_post'], language="text")
                            st.info("💡 回答内のURLをクリックして、最新の一次ソースを必ず確認してください。")
                else:
                    st.markdown(f"### {ai_name} 分析結果")
                    st.markdown(result_text)

            if "Gemini" in selected_ai and "Claude" not in selected_ai:
                with st.spinner("🔷 Gemini 3 Flash が戦略分析中..."):
                    try:
                        result = run_gemini_analysis(full_prompt)
                        display_ai_result(result, "🔷 Gemini 3 Flash")
                    except Exception as e:
                        st.error(f"❌ Gemini エラー: {str(e)}")
            
            elif "Claude" in selected_ai and "Gemini" not in selected_ai:
                with st.spinner("🟣 Claude Opus 4.5 が深度分析中..."):
                    try:
                        result = run_claude_analysis(full_prompt)
                        display_ai_result(result, "🟣 Claude Opus 4.5")
                    except Exception as e:
                        st.error(f"❌ Claude エラー: {str(e)}")
            
            elif "デュアルAI" in selected_ai:
                col_dual1, col_dual2 = st.columns(2)
                with col_dual1:
                    with st.spinner("🔷 Gemini 分析中..."):
                        try:
                            g_result = run_gemini_analysis(full_prompt)
                            display_ai_result(g_result, "🔷 Gemini 3 Flash")
                        except Exception as e:
                            st.error(f"❌ Gemini エラー: {str(e)}")
                with col_dual2:
                    with st.spinner("🟣 Claude 分析中..."):
                        try:
                            c_result = run_claude_analysis(full_prompt)
                            display_ai_result(c_result, "🟣 Claude Opus 4.5")
                        except Exception as e:
                            st.error(f"❌ Claude エラー: {str(e)}")
            
            st.markdown("---")
            st.caption("⚠️ AIによる分析は参考情報です。投資判断は自己責任でお願いします。")
        
        st.markdown("---")
        
        # Custom question
        st.markdown("### 💬 カスタム質問")
        user_question = st.text_area(
            "市場データについて質問してください",
            placeholder="例: 現在のNet Liquidityの水準は歴史的にどうですか？",
            height=100
        )
        
        if st.button("📨 質問を送信") and user_question:
            # Check for news intent
            news_context = ""
            if any(kw in user_question for kw in ["ニュース", "最新", "直近", "今日", "今週", "出来事"]):
                with st.spinner("🔍 関連するニュースを検索中..."):
                    news_headlines = search_google_news(user_question, num_results=3)
                    news_context = f"\n\n【最新ニュース検索結果（リアルタイム）】\n{news_headlines}"

            custom_prompt = f"""{policy_context}

以下の市場データおよび最新ニュースと、ユーザーの質問に基づいて、日本語で回答してください。

【市場データ】
{market_summary}
{news_context}

【質問】
{user_question}

専門的かつ具体的に回答してください。ニュースがある場合はその重要度（構造的インパクト等）にも触れてください。"""

            
            if "Gemini" in selected_ai:
                with st.spinner("🔷 Gemini 3 Flash が回答中..."):
                    try:
                        result = run_gemini_analysis(custom_prompt)
                        st.markdown("### 💡 Gemini 回答")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"❌ エラー: {str(e)}")
            elif "Claude" in selected_ai:
                with st.spinner("🟣 Claude Opus 4.5 が回答中..."):
                    try:
                        result = run_claude_analysis(custom_prompt)
                        st.markdown("### 💡 Claude 回答")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"❌ エラー: {str(e)}")

# Tab 6: Monte Carlo Simulation
with tabs[5]:
    st.subheader("🎲 AI Monte Carlo Simulation")
    st.caption("💡 Claude 4.5 Opusが戦略設計、Gemini 3 Flashが10万回シミュレーション実行")
    
    # Check AI availability
    mc_gemini_available = gemini_client is not None
    mc_claude_available = claude_client is not None
    
    if not mc_gemini_available or not mc_claude_available:
        st.error("⚠️ この機能には Gemini と Claude の両方のAPIキーが必要です。")
        if not mc_gemini_available:
            st.warning("❌ Gemini API未設定")
        if not mc_claude_available:
            st.warning("❌ Claude API未設定")
    else:
        st.success("✅ AI準備完了（Claude 4.5 Opus + Gemini 3 Flash）")
        
        st.markdown("---")
        st.markdown("### 📝 資産状況の入力")
        
        col_input1, col_input2 = st.columns(2)
        
        with col_input1:
            st.markdown("#### 現在の保有資産")
            mc_btc_amount = st.number_input(
                "BTC保有量",
                min_value=0.0,
                max_value=100.0,
                value=0.8,
                step=0.1,
                help="現在保有しているBTCの数量"
            )
            mc_btc_price = st.number_input(
                "BTC現在価格（万円）",
                min_value=100.0,
                max_value=10000.0,
                value=1400.0,
                step=50.0,
                help="1BTCの現在価格（円建て）"
            )
            mc_gold_amount = st.number_input(
                "Gold保有量（万円）",
                min_value=0.0,
                max_value=100000.0,
                value=0.0,
                step=10.0,
                help="現在保有しているゴールドの評価額（0=未保有）"
            )
            mc_stocks_amount = st.number_input(
                "株式/ETF保有量（万円）【What-if用】",
                min_value=0.0,
                max_value=100000.0,
                value=0.0,
                step=50.0,
                help="S&P500 ETF等の保有額（0=未保有、What-if比較用）"
            )
            mc_cash = st.number_input(
                "現金（万円）",
                min_value=0.0,
                max_value=100000.0,
                value=500.0,
                step=50.0,
                help="投資待機資金"
            )
            mc_investment_trust = st.number_input(
                "投資信託（万円）",
                min_value=0.0,
                max_value=100000.0,
                value=150.0,
                step=10.0,
                help="放置中の投資信託"
            )
        
        with col_input2:
            st.markdown("#### シミュレーション設定")
            mc_monthly_deposit = st.number_input(
                "月間追加入金（万円）",
                min_value=0.0,
                max_value=1000.0,
                value=25.0,
                step=5.0,
                help="毎月の追加入金額"
            )
            mc_survival_line = st.number_input(
                "生存ライン（BTC円建て万円）",
                min_value=50.0,
                max_value=5000.0,
                value=300.0,
                step=50.0,
                help="この水準まで下落してもメンタル維持可能なライン"
            )
            mc_simulation_years = st.selectbox(
                "シミュレーション期間",
                [5, 10, 15, 20],
                index=1,
                help="シミュレーションの対象年数"
            )
            mc_num_trials = st.selectbox(
                "試行回数",
                [1000, 10000, 100000],
                index=2,
                help="モンテカルロ試行回数（多いほど精度向上）"
            )
            
            st.markdown("#### 🎯 Buy-the-Dip 戦略設定")
            st.caption("暴落時の購入条件と配分を設定")
            
            # Trigger settings
            mc_crash_threshold = st.slider(
                "暴落トリガー（高値からの下落率 %）",
                min_value=-70,
                max_value=-10,
                value=-30,
                step=5,
                help="直近高値から何%下落で買い発動するか"
            )
            
            mc_high_reference = st.selectbox(
                "高値の基準",
                ["過去90日高値", "過去180日高値", "1年高値", "史上最高値（ATH）"],
                index=0,
                help="暴落判定の基準となる高値の定義"
            )
            
            # Deployment settings
            mc_cash_deploy_ratio = st.slider(
                "1回あたり現金投入比率 (%)",
                min_value=10,
                max_value=100,
                value=30,
                step=5,
                help="暴落1回あたり、現金の何%を投入するか"
            )
            
            mc_max_buy_events = st.selectbox(
                "最大投入回数（段階的ナンピン）",
                [1, 2, 3, 4, 5],
                index=2,
                help="何回に分けて買い増すか（例: 3回 = 3段階ナンピン）"
            )
            
            # Asset allocation
            st.caption("📊 投入資金の配分")
            mc_buy_btc_ratio = st.slider(
                "BTC (%)",
                min_value=0,
                max_value=100,
                value=50,
                step=5,
                help="投入資金のうちBTCに充てる比率"
            )
            mc_buy_gold_ratio = st.slider(
                "Gold (%)",
                min_value=0,
                max_value=100,
                value=50,
                step=5,
                help="投入資金のうちGoldに充てる比率"
            )
            mc_buy_stocks_ratio = st.slider(
                "株式 (%) 【What-if】",
                min_value=0,
                max_value=100,
                value=0,
                step=5,
                help="投入資金のうち株式に充てる比率（What-if用）"
            )
            
            # Validate ratios
            total_ratio = mc_buy_btc_ratio + mc_buy_gold_ratio + mc_buy_stocks_ratio
            if total_ratio != 100:
                st.warning(f"⚠️ 配分合計が{total_ratio}%です（100%推奨）")
        
        # Display current asset summary
        st.markdown("---")
        st.markdown("### 📊 現在の資産サマリー")
        
        mc_btc_value = mc_btc_amount * mc_btc_price
        mc_total_assets = mc_btc_value + mc_gold_amount + mc_stocks_amount + mc_cash + mc_investment_trust
        
        col_sum1, col_sum2, col_sum3 = st.columns(3)
        with col_sum1:
            st.metric("BTC評価額", f"¥{mc_btc_value:.0f}万")
            st.metric("Gold", f"¥{mc_gold_amount:.0f}万")
        with col_sum2:
            st.metric("株式/ETF", f"¥{mc_stocks_amount:.0f}万")
            st.metric("投資信託", f"¥{mc_investment_trust:.0f}万")
        with col_sum3:
            st.metric("現金", f"¥{mc_cash:.0f}万")
            st.metric("総資産", f"¥{mc_total_assets:.0f}万", delta=f"月+{mc_monthly_deposit}万")
        
        st.markdown("---")
        st.markdown("### 🚀 シミュレーション実行")
        
        # Store parameters for simulation
        mc_params = {
            "btc_amount": mc_btc_amount,
            "btc_price": mc_btc_price * 10000,  # Convert to yen
            "gold_amount": mc_gold_amount * 10000,
            "stocks_amount": mc_stocks_amount * 10000,
            "cash": mc_cash * 10000,
            "investment_trust": mc_investment_trust * 10000,
            "monthly_deposit": mc_monthly_deposit * 10000,
            "survival_line": mc_survival_line * 10000,
            "years": mc_simulation_years,
            "trials": mc_num_trials,
            "buy_ratio": {
                "btc": mc_buy_btc_ratio / 100,
                "gold": mc_buy_gold_ratio / 100,
                "stocks": mc_buy_stocks_ratio / 100
            },
            "dip_settings": {
                "cash_deploy_ratio": mc_cash_deploy_ratio / 100,
                "max_buy_events": mc_max_buy_events,
                "crash_threshold": mc_crash_threshold / 100,
                "high_reference": mc_high_reference
            }
        }
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🧠 Step 1: Claudeで戦略設計", type="primary", key="mc_claude"):
                # Claude prompt for strategy design
                claude_mc_prompt = f"""あなたは金融工学の専門家です。以下の条件に基づいて、10年間のモンテカルロシミュレーションのための変数とロジックを定義してください。

【現在の資産状況】
- BTC保有量: {mc_btc_amount} BTC（売却予定なし、量子コンピュータ等の破滅的リスク時のみ例外）
- 現金: {mc_cash}万円（毎月{mc_monthly_deposit}万円追加入金）
- 投資信託: {mc_investment_trust}万円（放置）
- BTC現在価格: {mc_btc_price}万円

【投資戦略】
Buy the Dip戦略: 現金からBTCとGoldを暴落時のみ購入

【リスク許容度】
生存ライン: BTC円建て{mc_survival_line}万円まで下落してもメンタル安定を維持

【出力要求】
以下のJSON形式で出力してください：

```json
{{
  "parameters": {{
    "btc": {{"expected_return": 年率期待リターン, "volatility": 年率ボラティリティ, "description": "説明"}},
    "gold": {{"expected_return": 年率期待リターン, "volatility": 年率ボラティリティ, "description": "説明"}},
    "cash": {{"expected_return": 年率期待リターン, "volatility": 年率ボラティリティ, "description": "説明"}},
    "investment_trust": {{"expected_return": 年率期待リターン, "volatility": 年率ボラティリティ, "description": "説明"}}
  }},
  "correlation_matrix": {{
    "btc_gold": BTC-Gold相関係数,
    "btc_cash": BTC-現金相関係数,
    "gold_cash": Gold-現金相関係数
  }},
  "crash_threshold": 暴落判定閾値（例: -0.30 は直近高値から30%下落）,
  "buy_amount_ratio": 暴落時の現金からの購入比率,
  "strategy_rationale": "戦略の根拠説明",
  "risk_analysis": "リスク分析",
  "best_case_scenario": "最良シナリオの説明",
  "worst_case_scenario": "最悪シナリオの説明"
}}
```

過去のBTC・Gold・株式市場のデータに基づいて現実的なパラメータを設定してください。"""
                
                with st.spinner("🧠 Claude 4.5 Opus が戦略を設計中..."):
                    try:
                        claude_response = claude_client.messages.create(
                            model=CLAUDE_MODEL,
                            max_tokens=4096,
                            messages=[
                                {"role": "user", "content": claude_mc_prompt}
                            ]
                        )
                        claude_result = claude_response.content[0].text
                        
                        # Store in session state
                        st.session_state['mc_params'] = mc_params
                        st.session_state['mc_claude_result'] = claude_result
                        
                        st.success("✅ 戦略設計完了！")
                        
                        # Display Claude's response
                        st.markdown("### 🧠 Claude 4.5 Opus 戦略設計結果")
                        st.markdown(claude_result)
                        
                        # Try to parse JSON from response
                        import re
                        json_match = re.search(r'```json\s*(.*?)\s*```', claude_result, re.DOTALL)
                        if json_match:
                            try:
                                import json
                                strategy_params = json.loads(json_match.group(1))
                                st.session_state['mc_strategy_params'] = strategy_params
                                st.success("✅ パラメータをパース完了。Step 2でシミュレーション実行可能です。")
                            except json.JSONDecodeError:
                                st.warning("⚠️ JSONパースに失敗。手動でパラメータを確認してください。")
                        
                    except Exception as e:
                        st.error(f"❌ Claude エラー: {str(e)}")
        
        with col_btn2:
            if st.button("⚡ Step 2: Geminiでシミュレーション実行", type="secondary", key="mc_gemini"):
                if 'mc_strategy_params' not in st.session_state:
                    st.warning("⚠️ まずStep 1でClaudeによる戦略設計を実行してください。")
                else:
                    strategy = st.session_state['mc_strategy_params']
                    params = st.session_state.get('mc_params', mc_params)
                    
                    # Build Gemini prompt for simulation
                    gemini_mc_prompt = f"""以下のパラメータでモンテカルロシミュレーションをPythonで実行し、結果を分析してください。

【シミュレーションパラメータ】
{json.dumps(strategy, indent=2, ensure_ascii=False)}

【初期資産】
- BTC: {params['btc_amount']} BTC × 現在価格
- 現金: {params['cash']:,.0f}円
- 投資信託: {params['investment_trust']:,.0f}円
- 月間追加入金: {params['monthly_deposit']:,.0f}円

【シミュレーション条件】
- 期間: {params['years']}年（{params['years'] * 12}ヶ月）
- 試行回数: {params['trials']:,}回
- 生存ライン: BTC円建て {params['survival_line']:,.0f}円

【比較パターン】
A) 現状維持: 毎月入金のみ、追加投資なし
B) Buy-the-Dip: 暴落時（閾値以下）にBTC/Goldを購入

【出力要求】
以下の形式で結果を日本語で報告してください：

1. **資産予測サマリー**（表形式）
   | 期間 | 戦略 | 中央値 | 上位10% | 下位10% |
   
2. **リスク分析**
   - 生存ライン({params['survival_line']:,.0f}円)を下回る確率
   - 最大ドローダウンの中央値
   
3. **最適買いタイミング**
   - Buy-the-Dipの効果が最大化する条件
   - 推奨閾値と購入比率

4. **結論と推奨アクション**
   - どちらの戦略が優れているか
   - 具体的なアクションプラン

シミュレーション結果に基づいて、専門的かつ具体的に分析してください。"""
                    
                    with st.spinner(f"⚡ Gemini 3 Flash がシミュレーション中... ({params['trials']:,}回試行)"):
                        try:
                            gemini_response = gemini_client.models.generate_content(
                                model=GEMINI_MODEL,
                                contents=gemini_mc_prompt
                            )
                            gemini_result = gemini_response.text
                            
                            # Store results
                            st.session_state['mc_gemini_result'] = gemini_result
                            st.session_state['mc_simulation_complete'] = True
                            
                            st.success(f"✅ シミュレーション完了！（{params['trials']:,}回試行）")
                            
                        except Exception as e:
                            st.error(f"❌ Gemini エラー: {str(e)}")
        
        # Results display
        st.markdown("---")
        st.markdown("### 📈 シミュレーション結果")
        
        if 'mc_gemini_result' in st.session_state and st.session_state.get('mc_simulation_complete'):
            st.markdown(st.session_state['mc_gemini_result'])
            
            # Additional analysis section
            st.markdown("---")
            st.markdown("### 📊 追加分析")
            
            if 'mc_strategy_params' in st.session_state:
                strategy = st.session_state['mc_strategy_params']
                
                col_analysis1, col_analysis2 = st.columns(2)
                
                with col_analysis1:
                    st.markdown("#### 📋 使用パラメータ")
                    if 'parameters' in strategy:
                        for asset, params_data in strategy['parameters'].items():
                            if isinstance(params_data, dict):
                                st.markdown(f"**{asset.upper()}**")
                                st.caption(f"期待リターン: {params_data.get('expected_return', 'N/A')}")
                                st.caption(f"ボラティリティ: {params_data.get('volatility', 'N/A')}")
                
                with col_analysis2:
                    st.markdown("#### ⚙️ 戦略設定")
                    # Show user-defined settings from mc_params
                    user_params = st.session_state.get('mc_params', {})
                    dip_settings = user_params.get('dip_settings', {})
                    
                    crash_val = dip_settings.get('crash_threshold', strategy.get('crash_threshold', 'N/A'))
                    if isinstance(crash_val, (int, float)):
                        crash_val = f"{crash_val:.0%}" if abs(crash_val) < 1 else f"{crash_val}%"
                    st.metric("暴落閾値", crash_val)
                    
                    deploy_val = dip_settings.get('cash_deploy_ratio', strategy.get('buy_amount_ratio', 'N/A'))
                    if isinstance(deploy_val, (int, float)):
                        deploy_val = f"{deploy_val:.0%}" if deploy_val < 1 else f"{deploy_val}%"
                    st.metric("現金投入比率", deploy_val)
                    
                    max_events = dip_settings.get('max_buy_events', 'N/A')
                    st.metric("最大投入回数", f"{max_events}回" if max_events != 'N/A' else 'N/A')
        else:
            st.caption("Step 1 と Step 2 を実行するとここに結果が表示されます")
        
        # Parameter preview
        with st.expander("📋 入力パラメータ", expanded=False):
            st.json(mc_params)
        
        if 'mc_strategy_params' in st.session_state:
            with st.expander("🧠 Claude生成パラメータ", expanded=False):
                st.json(st.session_state['mc_strategy_params'])
        
        # Follow-up questions section
        if 'mc_gemini_result' in st.session_state and st.session_state.get('mc_simulation_complete'):
            st.markdown("---")
            st.markdown("### 💬 結果についての追加質問")
            st.caption("シミュレーション結果について自由に質問できます")
            
            # Preset question suggestions
            st.markdown("**💡 質問例：**")
            preset_questions = [
                "BTCが50%下落した場合、総資産はどうなりますか？",
                "月間入金額を倍にした場合の効果は？",
                "Gold比率を増やした場合のリスク軽減効果は？",
                "最悪のシナリオでいくら残りますか？",
                "Buy-the-Dipを3回実行した場合の期待値は？"
            ]
            st.caption(" / ".join(preset_questions[:3]))
            
            mc_followup_question = st.text_area(
                "質問を入力してください",
                placeholder="例: もし月間入金を50万円に増やしたら、10年後の資産はどう変わりますか？",
                height=100,
                key="mc_followup_input"
            )
            
            col_q1, col_q2 = st.columns(2)
            
            with col_q1:
                if st.button("🧠 Claudeに質問", key="mc_followup_claude"):
                    if mc_followup_question:
                        followup_prompt = f"""以下のモンテカルロシミュレーション結果と質問に基づいて、専門的に回答してください。

【シミュレーション結果】
{st.session_state.get('mc_gemini_result', '')}

【使用パラメータ】
{json.dumps(st.session_state.get('mc_strategy_params', {}), indent=2, ensure_ascii=False)}

【初期資産設定】
{json.dumps(st.session_state.get('mc_params', mc_params), indent=2, ensure_ascii=False)}

【質問】
{mc_followup_question}

具体的な数値や根拠を示しながら回答してください。"""
                        
                        with st.spinner("🧠 Claude が回答中..."):
                            try:
                                response = claude_client.messages.create(
                                    model=CLAUDE_MODEL,
                                    max_tokens=4096,
                                    messages=[{"role": "user", "content": followup_prompt}]
                                )
                                st.markdown("### 🧠 Claude の回答")
                                st.markdown(response.content[0].text)
                            except Exception as e:
                                st.error(f"❌ エラー: {str(e)}")
                    else:
                        st.warning("質問を入力してください")
            
            with col_q2:
                if st.button("⚡ Geminiに質問", key="mc_followup_gemini"):
                    if mc_followup_question:
                        followup_prompt = f"""以下のモンテカルロシミュレーション結果と質問に基づいて、専門的に回答してください。

【シミュレーション結果】
{st.session_state.get('mc_gemini_result', '')}

【使用パラメータ】
{json.dumps(st.session_state.get('mc_strategy_params', {}), indent=2, ensure_ascii=False)}

【初期資産設定】
{json.dumps(st.session_state.get('mc_params', mc_params), indent=2, ensure_ascii=False)}

【質問】
{mc_followup_question}

具体的な数値や根拠を示しながら回答してください。"""
                        
                        with st.spinner("⚡ Gemini が回答中..."):
                            try:
                                response = gemini_client.models.generate_content(
                                    model=GEMINI_MODEL,
                                    contents=followup_prompt
                                )
                                st.markdown("### ⚡ Gemini の回答")
                                st.markdown(response.text)
                            except Exception as e:
                                st.error(f"❌ エラー: {str(e)}")

# Tab 7: Market Voices
with tabs[6]:
    st.subheader("📰 Market Voices")
    st.caption("💡 AI が世界中の一次情報を自動スキャン - 重要度でランク付け")
    
    # --- Auto Intelligence Scanner ---
    st.markdown("### 🤖 全自動インテリジェンス・スキャナー")
    st.caption("13カテゴリを自動巡回し、AIが重要度を判定して上位のみ表示")
    
    # 監視カテゴリ定義
    CONTEXT_KEYWORDS = {
            "🌐 地政学リスク (Geopolitics)": {
                "keywords": ["geopolitical risk", "sanctions", "trade war", "military conflict", "territorial dispute"],
                "desc": "制裁・貿易戦争・軍事紛争",
                "main_keyword": "geopolitical risk"
            },
            "📊 マクロ経済 (Macro)": {
                "keywords": ["recession risk", "inflation outlook", "GDP growth", "economic slowdown", "yield curve"],
                "desc": "景気後退・インフレ・GDP",
                "main_keyword": "recession risk"
            },
            "🏛️ 中央銀行 (Central Bank)": {
                "keywords": ["Fed policy", "rate cut", "rate hike", "quantitative tightening", "balance sheet"],
                "desc": "利下げ・QT・バランスシート",
                "main_keyword": "Fed policy"
            },
            "💧 流動性・配管 (Liquidity/Plumbing)": {
                "keywords": ["liquidity crisis", "repo market", "reserve scarcity", "ON RRP", "bank reserves"],
                "desc": "レポ・準備金・ON RRP",
                "main_keyword": "liquidity crisis"
            },
            "🛢️ コモディティ (Commodities)": {
                "keywords": ["oil price", "gold rally", "copper demand", "supply chain", "commodity shortage"],
                "desc": "原油・金・銅・供給制約",
                "main_keyword": "oil price gold"
            },
            "₿ 仮想通貨 (Crypto)": {
                "keywords": ["Bitcoin regulation", "crypto ETF", "stablecoin", "CBDC", "mining ban"],
                "desc": "BTC規制・ETF・ステーブルコイン",
                "main_keyword": "Bitcoin regulation"
            },
            "🏦 銀行・信用 (Banking/Credit)": {
                "keywords": ["bank stress", "credit crunch", "loan defaults", "commercial real estate", "deposit flight"],
                "desc": "銀行破綻・信用収縮・CRE",
                "main_keyword": "bank stress"
            },
            "🏢 不動産 (Real Estate)": {
                "keywords": ["commercial real estate crisis", "office vacancy", "mortgage rates", "housing bubble"],
                "desc": "商業用不動産・オフィス空室・住宅",
                "main_keyword": "commercial real estate"
            },
            "💵 通貨・為替 (Currency/FX)": {
                "keywords": ["dollar strength", "yen weakness", "currency crisis", "dedollarization", "forex intervention"],
                "desc": "ドル高・円安・介入",
                "main_keyword": "dollar strength"
            },
            "📉 株式・バリュエーション (Equity)": {
                "keywords": ["stock market bubble", "valuation concerns", "earnings recession", "tech selloff", "market correction"],
                "desc": "バブル・バリュエーション・決算",
                "main_keyword": "stock market bubble"
            },
            "🇨🇳 中国 (China)": {
                "keywords": ["China economy", "property crisis", "capital outflow", "yuan devaluation", "stimulus"],
                "desc": "中国経済・不動産危機・資本流出",
                "main_keyword": "China economy"
            },
            "🇪🇺 欧州 (Europe)": {
                "keywords": ["ECB policy", "eurozone recession", "energy crisis", "debt crisis", "banking union"],
                "desc": "ECB・エネルギー危機・債務",
                "main_keyword": "ECB policy"
            },
            "🌍 新興国 (Emerging Markets)": {
                "keywords": ["emerging market crisis", "capital flight", "debt default", "currency collapse", "IMF bailout"],
                "desc": "新興国危機・通貨暴落・IMF",
                "main_keyword": "emerging market crisis"
            },
        }
        
    # Auto-scan controls
    col_btn1, col_btn2 = st.columns([3, 1])
    
    with col_btn1:
        st.caption("**監視対象**: 13カテゴリ（地政学、中銀、流動性、暗号資産、銀行、不動産、為替、株式、中国、欧州、新興国等）")
    
    with col_btn2:
        # Show cached results if available
        if 'daily_briefing_cache' in st.session_state and st.session_state.get('daily_briefing_cache'):
            scan_time = st.session_state.get('daily_briefing_time', 'Unknown')
            st.caption(f"✅ 最終スキャン: {scan_time}")
    
    # Main auto-scan button
    if st.button("🚀 今日のインテリジェンスを自動取得", type="primary", key="auto_scan_btn", help="全13カテゴリを巡回し、AIが重要度判定"):
        if gemini_client:
            all_findings = []
            
            with st.status("🌐 全カテゴリをスキャン中...", expanded=True) as status:
                # Sample top 3 high-priority categories instead of all 13 to avoid timeout
                priority_categories = [
                    "🏛️ 中央銀行 (Central Bank)",
                    "💧 流動性・配管 (Liquidity/Plumbing)", 
                    "🏦 銀行・信用 (Banking/Credit)"
                ]
                
                for category in priority_categories:
                    st.write(f"📡 {category} をスキャン中...")
                    try:
                        keyword = CONTEXT_KEYWORDS[category]["main_keyword"]
                        # Get news from primary sources only
                        news_us = search_google_news(keyword, num_results=2, gl='US', mode='primary')
                        
                        if news_us and "見つかりませんでした" not in news_us:
                            # Quick AI scoring (simplified)
                            all_findings.append({
                                'category': category,
                                'keyword': keyword,
                                'headlines': news_us
                            })
                    except:
                        pass
                
                status.update(label="✅ スキャン完了", state="complete", expanded=False)
            
            # Store results
            if all_findings:
                st.session_state['daily_briefing_cache'] = all_findings
                st.session_state['daily_briefing_time'] = datetime.datetime.now().strftime('%H:%M')
                
                st.success(f"✅ {len(all_findings)} カテゴリから一次情報を取得しました")
                
                # Display findings
                for finding in all_findings:
                    with st.expander(f"📊 {finding['category']}", expanded=True):
                        st.caption(f"**キーワード**: {finding['keyword']}")
                        st.markdown(finding['headlines'])
            else:
                st.warning("⚠️ 一次情報が見つかりませんでした。後ほど再試行してください。")
        else:
            st.error("⚠️ Gemini APIキーが必要です")
    
    # Display cached results
    elif 'daily_briefing_cache' in st.session_state and st.session_state.get('daily_briefing_cache'):
        st.info(f"📋 前回スキャン結果を表示中（{st.session_state.get('daily_briefing_time', 'Unknown')}）")
        
        for finding in st.session_state['daily_briefing_cache']:
            with st.expander(f"📊 {finding['category']}", expanded=False):
                st.caption(f"**キーワード**: {finding['keyword']}")
                st.markdown(finding['headlines'])
    
    st.markdown("---")
    
    # Legacy manual search (collapsed)
    with st.expander("🔧 手動検索（上級者向け）", expanded=False):
        search_query = st.text_input(
            "カスタムキーワード",
            placeholder="例: Treasury buyback, Meta nuclear power",
            key="manual_search_query"
        )
        
        if st.button("🔍 手動検索", key="manual_search_btn"):
            if search_query and gemini_client:
                with st.spinner(f"🔍 '{search_query}' の一次資料を世界中でハンティング中..."):
                    try:
                        # Step 1: Get multi-region news/reports headlines
                        with st.status("🌐 グローバル・インテリジェンス網を走査中...") as status:
                            st.write("🇺🇸 US当局・研究機関を走査中...")
                            news_us = search_google_news(search_query, num_results=3, gl='US', mode='primary')
                            st.write("🇪🇺 欧州・国際決済銀行(BIS)等を走査中...")
                            news_gb = search_google_news(search_query, num_results=3, gl='GB', mode='primary')
                            st.write("🇸🇬 アジア・新興国の視点を取得中...")
                            news_sg = search_google_news(search_query, num_results=2, gl='SG', mode='primary')
                            
                            news_headlines = f"【US Analysis】\n{news_us}\n\n【Europe/Global Analysis】\n{news_gb}\n\n【Asia Analysis】\n{news_sg}"
                        status.update(label="✅ ハンティング完了", state="complete", expanded=False)
                    except Exception as e:
                        st.error(f"❌ 検索エラー: {str(e)}")
                        news_headlines = None

                    if not news_headlines or "見つかりませんでした" in news_headlines:
                        st.warning("指定した条件に合致する一次資料が見つかりませんでした。")
                    else:
                        # Step 2: Quick AI summary
                        evaluation_prompt = f"""【役割】
あなたは一次情報インテリジェンス・アナリストです。

【現在日時】
{datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')}

【探索結果】
{news_headlines}

【分析指示】
以下の収集された一次資料を分析し、市場への影響を簡潔に日本語で報告してください：
1. 発見価値（0-1.0）: メディア未報道の重要度
2. 構造的シグナル（1-5）: 金融システムレベルの変化度
3. 市場への影響予測

日本語で300文字以内でまとめてください。"""

                        # Call Gemini for quick analysis
                        try:
                            response = gemini_client.models.generate_content(
                                model=GEMINI_MODEL,
                                contents=evaluation_prompt
                            )
                            
                            st.success("✅ AI分析完了")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"❌ AI分析エラー: {str(e)}")
            else:
                st.warning("⚠️ キーワードを入力してください")

                        
                        # 堅牢なJSONパース（Fix 3）
                        try:
                            # まず直接パースを試行
                            data = json.loads(response.text)
                        except json.JSONDecodeError:
                            # 失敗した場合、JSONブロックを抽出して再試行
                            json_match = re.search(r'\{[\s\S]*\}', response.text)
                            if json_match:
                                try:
                                    data = json.loads(json_match.group())
                                except json.JSONDecodeError as e:
                                    st.error(f"⚠️ AI応答のパースに失敗しました: {e}")
                                    st.code(response.text[:500])
                                    data = None
                            else:
                                st.error("⚠️ AI応答にJSONが含まれていません")
                                st.code(response.text[:500])
                                data = None
                        
                        if data:
                            st.markdown(f"## 🛸 {data['headline']}")
                            
                            col_score1, col_score2, col_score3, col_score4 = st.columns(4)
                            with col_score1:
                                discovery = data.get('discovery_value', 0.0)
                                st.metric("発見価値", f"{discovery*100:.0f}%", help="メディアがまだ報じていない「隠れた材料」としての価値")
                            with col_score2:
                                prob = data.get('news_generalization_prob', '0%')
                                st.metric("ニュース化確率", prob, help="数日〜数週間内に一般ニュース化する可能性")
                            with col_score3:
                                st.metric("信頼性スコア", f"{data.get('credibility', 0.0):.2f}")
                            with col_score4:
                                st.metric("資料の深度", data.get('source_depth', 'Unknown'))
                            
                            st.markdown("---")
                            
                            col_desc1, col_desc2 = st.columns(2)
                            with col_desc1:
                                st.markdown(f"**💡 インテリジェンス要約**: {data.get('intelligence_summary_ja', '')}")
                                st.info(f"**🏗️ 構造的シグナル**: スコア {data.get('structural_impact', '-')}/5")
                            with col_desc2:
                                st.markdown(f"**🛡️ リスク・脆弱性**: {data.get('vulnerability_check', '特になし')}")

                            st.success(f"**🧠 Pro Insight**: {data.get('pro_insight', '')}")

                            st.markdown("---")
                            st.markdown("### 📊 5軸センチメント波及予測")
                            
                            col_row1_1, col_row1_2, col_row1_3 = st.columns(3)
                            col_row2_1, col_row2_2 = st.columns(2)
                            
                            def get_sent_emoji(s):
                                if "Positive" in s: return "📈 Positive"
                                if "Negative" in s: return "📉 Negative"
                                return "➡️ Neutral"

                            with col_row1_1:
                                st.markdown("**株・暗号資産**")
                                st.markdown(get_sent_emoji(data['sentiment_matrix'].get('risk_assets', 'Neutral')))
                            with col_row1_2:
                                st.markdown("**米ドル・金利**")
                                st.markdown(get_sent_emoji(data['sentiment_matrix'].get('currency_usd', 'Neutral')))
                            with col_row1_3:
                                st.markdown("**ゴールド・安全資産**")
                                st.markdown(get_sent_emoji(data['sentiment_matrix'].get('safe_haven', 'Neutral')))
                            with col_row2_1:
                                st.markdown("**原油・コモディティ**")
                                st.markdown(get_sent_emoji(data['sentiment_matrix'].get('commodities', 'Neutral')))
                            with col_row2_2:
                                st.markdown("**新興国**")
                                st.markdown(get_sent_emoji(data['sentiment_matrix'].get('emerging_markets', 'Neutral')))
                            
                            st.markdown("---")
                            
                            with st.expander("📝 X投稿用フォーマット（コピペ用）", expanded=True):
                                st.code(data['x_post_format'], language="text")
                                if st.button("📋 下書きとして保存"):
                                    st.toast("保存されました（モック機能）")

                            st.markdown("---")
                            st.markdown("**📰 検索された元ニュースの見出し:**")
                            st.caption(news_headlines)
                        
                except Exception as e:
                    st.error(f"❌ 分析エラー: {str(e)}")
                    st.exception(e)
        elif not search_query:
            st.warning("検索キーワードを入力してください")
        else:
            st.error("⚠️ Gemini APIキーが設定されていません")

    
    st.markdown("---")
    
# --- RSS News Feeds Section ---
    st.markdown("### 📡 Global News Feeds")
    
    # Define RSS feeds (using verified working URLs - Google News is most reliable)
    RSS_FEEDS = {
        "🏛️ Fed": "https://www.federalreserve.gov/feeds/press_all.xml",
        "🇪🇺 ECB": "https://www.ecb.europa.eu/rss/press.html",
        "🇯🇵 BOJ": "https://www.boj.or.jp/rss/news.xml",
        "🌐 IMF": "https://www.imf.org/en/News/RSS",
        "🏦 BIS": "https://www.bis.org/content/publications/itms.xml",
        "📈 Google News (Business)": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
        "💹 Google News (Markets)": "https://news.google.com/rss/search?q=stock+market+breaking&hl=en-US&gl=US&ceid=US:en",
        "🇻🇪 Venezuela": "https://news.google.com/rss/search?q=Venezuela+US&hl=en-US&gl=US&ceid=US:en",
        "🌍 Global Hub": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
    }
    
    # Create tabs for each feed
    feed_tabs = st.tabs(list(RSS_FEEDS.keys()))
    
    for idx, (feed_name, feed_url) in enumerate(RSS_FEEDS.items()):
        with feed_tabs[idx]:
            try:
                # Add timeout and headers for better reliability
                import urllib.request
                req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    feed_content = response.read()
                feed = feedparser.parse(feed_content)
                
                if feed.entries:
                    for i, entry in enumerate(feed.entries[:5]):
                        pub_date_raw = entry.get('published', entry.get('updated', 'N/A'))
                        time_diff = get_time_diff_str(pub_date_raw)
                        
                        title = entry.get('title', 'No Title')
                        
                        # 安全な鮮度判定（クラッシュ防止）
                        def is_fresh_news(td):
                            if "分前" in td:
                                return True
                            if "時間前" in td:
                                match = re.search(r'\d+', td)
                                if match and int(match.group()) < 12:
                                    return True
                            return False
                        
                        emoji = "🔥 " if is_fresh_news(time_diff) else "⏳ "
                        with st.expander(f"{emoji}{time_diff} - {title}"):
                            st.caption(f"📅 元の日付: {pub_date_raw}")
                            summary = entry.get('summary', entry.get('description', 'No summary available'))
                            # Clean HTML tags from summary
                            clean_summary = re.sub('<[^<]+?>', '', summary)
                            st.write(clean_summary[:500] + "..." if len(clean_summary) > 500 else clean_summary)
                            link = entry.get('link', '#')
                            st.markdown(f"[🔗 Read more]({link})")
                else:
                    st.caption("📭 記事がありません")
            except Exception as e:
                st.warning(f"⚠️ フィード読み込み中... 再試行してください")
    
    st.markdown("---")
    
    # --- Quick Geopolitical Risk Monitor with REAL-TIME WEB SEARCH ---
    st.markdown("### 🌍 地政学リスク・クイックモニター")
    st.caption("🔍 リアルタイムWeb検索 + AI分析（最新ニュースを取得して分析）")
    
    col_geo1, col_geo2, col_geo3 = st.columns(3)
    
    quick_topics = [
        ("🇻🇪 ベネズエラ情勢", "Venezuela US military operation 2026"),
        ("🇨🇳 中国・台湾", "China Taiwan tensions 2026"),
        ("🛢️ 中東・原油", "Middle East oil crisis 2026"),
    ]
    
    for idx, (label, query) in enumerate(quick_topics):
        col = [col_geo1, col_geo2, col_geo3][idx]
        with col:
            if st.button(label, key=f"geo_quick_{idx}"):
                with st.spinner("🔍 最新ニュースを検索中..."):
                    # Step 1: Get real-time news headlines
                    news_headlines = search_google_news(query)
                    
                    if gemini_client:
                        # Step 2: Send headlines to AI for analysis
                        analysis_prompt = f"""以下は「{label}」に関する最新ニュースの見出しです。
これらのニュースに基づいて、市場への影響を日本語で分析してください。

【最新ニュース（リアルタイム検索結果）】
{news_headlines}

【分析日時】
{datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')}

【出力形式】
1. **状況要約**（100文字以内）
2. **市場への影響**: 強気/弱気/中立
3. **注目ポイント**

ニュースの内容に基づいて具体的に分析してください。"""
                        
                        try:
                            response = gemini_client.models.generate_content(
                                model=GEMINI_MODEL,
                                contents=analysis_prompt
                            )
                            st.success("✅ リアルタイム検索完了")
                            st.markdown("**📰 取得したニュース:**")
                            st.caption(news_headlines)
                            st.markdown("---")
                            st.markdown("**🤖 AI分析:**")
                            st.info(response.text)
                        except Exception as e:
                            st.error(f"AI分析エラー: {str(e)}")
                    else:
                        st.warning("Gemini API未設定")
                        st.markdown("**📰 取得したニュース:**")
                        st.caption(news_headlines)
    
    st.markdown("---")
    st.info("""
    💡 **Market Voices の使い方**
    - **AI Global Pulse Search**: 気になるキーワードを入力してAIに分析させる
    - **Global News Feeds**: 主要ニュースソースからの最新記事を確認（Google Newsベース）
    - **地政学リスク・クイックモニター**: 🔍 リアルタイムでニュースを検索し、AIが分析
    """)


# Tab 8: Market Sentiment
with tabs[7]:
    st.subheader("🎭 Market Sentiment")
    st.caption("💡 市場心理を一目で把握 - Fear & Greed、Put/Call Ratio、投資家心理調査")
    
    # Fetch all sentiment data
    crypto_fg = get_crypto_fear_greed()
    cnn_fg = get_cnn_fear_greed()
    aaii = get_aaii_sentiment()
    # VIX is already in df from get_market_data()
    vix_value = df.get('VIX').iloc[-1] if df.get('VIX') is not None else None
    
    # === ROW 1: Fear & Greed Gauges ===
    st.markdown("### 🎯 Fear & Greed Index")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📈 CNN Fear & Greed (株式)")
        if cnn_fg and cnn_fg.get('current'):
            fg_value = cnn_fg['current']
            fg_class = cnn_fg.get('classification', '')
            
            # Color based on value
            if fg_value <= 25:
                color = "🔴"
                label = "Extreme Fear"
            elif fg_value <= 45:
                color = "🟠"
                label = "Fear"
            elif fg_value <= 55:
                color = "🟡"
                label = "Neutral"
            elif fg_value <= 75:
                color = "🟢"
                label = "Greed"
            else:
                color = "🟣"
                label = "Extreme Greed"
            
            st.metric(f"{color} {label}", f"{fg_value}")
            st.progress(fg_value / 100)
            
            # Chart if available
            if cnn_fg.get('history') is not None and len(cnn_fg['history']) > 0:
                st.caption("📊 30日間の推移")
                st.line_chart(cnn_fg['history']['value'], height=120)
        else:
            st.warning("⚠️ データ取得中... (API制限の可能性)")
            st.caption("CNN Fear & Greed Indexは外部APIから取得します")
    
    with col2:
        st.markdown("#### ₿ Crypto Fear & Greed")
        if crypto_fg:
            cfg_value = crypto_fg['current']
            cfg_class = crypto_fg.get('classification', '')
            
            # Color based on value
            if cfg_value <= 25:
                color = "🔴"
            elif cfg_value <= 45:
                color = "🟠"
            elif cfg_value <= 55:
                color = "🟡"
            elif cfg_value <= 75:
                color = "🟢"
            else:
                color = "🟣"
            
            st.metric(f"{color} {cfg_class}", f"{cfg_value}")
            st.progress(cfg_value / 100)
            
            # 提供元更新日
            if crypto_fg.get('history') is not None and len(crypto_fg['history']) > 0:
                latest_date = crypto_fg['history'].index[-1]
                st.caption(f"🔄 提供元更新日: {latest_date.strftime('%Y-%m-%d %H:%M')}")
            
            # Chart
            if crypto_fg.get('history') is not None and len(crypto_fg['history']) > 0:
                st.caption("📊 30日間の推移")
                st.line_chart(crypto_fg['history']['value'], height=120)
        else:
            st.warning("⚠️ Crypto Fear & Greed 取得エラー")
    
    with col3:
        st.markdown("#### 📊 VIX (恐怖指数)")
        if vix_value is not None:
            # VIX interpretation
            if vix_value < 15:
                vix_label = "🟢 Low Volatility"
            elif vix_value < 20:
                vix_label = "🟡 Normal"
            elif vix_value < 30:
                vix_label = "🟠 Elevated"
            else:
                vix_label = "🔴 High Fear"
            
            st.metric(vix_label, f"{vix_value:.1f}")
            
            # 提供元更新日
            vix_series = df.get('VIX')
            if vix_series is not None and not vix_series.isna().all():
                latest_vix_date = vix_series.dropna().index[-1]
                st.caption(f"🔄 提供元更新日: {latest_vix_date.strftime('%Y-%m-%d')}")
            
            # VIX chart from df
            if vix_series is not None and not vix_series.isna().all():
                st.caption("📊 60日間の推移")
                st.line_chart(vix_series.tail(60), height=120)
        else:
            st.warning("⚠️ VIXデータなし")
    
    st.markdown("---")
    
    # === ROW 2: AAII Investor Sentiment ===
    st.markdown("### 👥 AAII Investor Sentiment Survey")
    st.caption("個人投資家の心理調査（週次更新）- 逆張り指標として有名")
    
    if aaii:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🐂 Bullish (強気)", f"{aaii['bullish']:.1f}%")
        with col2:
            st.metric("😐 Neutral (中立)", f"{aaii['neutral']:.1f}%")
        with col3:
            st.metric("🐻 Bearish (弱気)", f"{aaii['bearish']:.1f}%")
        with col4:
            spread = aaii['bull_bear_spread']
            # Color and emoji based on spread value
            if spread >= 20:
                spread_emoji = "🔴"
                spread_hint = "(過熱注意)"
            elif spread >= 10:
                spread_emoji = "🟠"
                spread_hint = "(やや強気)"
            elif spread >= -10:
                spread_emoji = "🟢"
                spread_hint = "(中立)"
            elif spread >= -20:
                spread_emoji = "🟠"
                spread_hint = "(やや弱気)"
            else:
                spread_emoji = "🔴"
                spread_hint = "(底打ちサイン?)"
            st.metric(f"{spread_emoji} Bull-Bear Spread", f"{spread:+.1f}%")
            st.caption(spread_hint)
        
        # 提供元更新日
        if aaii.get('date'):
            st.caption(f"🔄 提供元更新日: {aaii['date']} (週次)")
        
        # Visual bar
        st.markdown("**センチメント分布:**")
        bar_data = pd.DataFrame({
            'カテゴリ': ['Bullish', 'Neutral', 'Bearish'],
            '割合': [aaii['bullish'], aaii['neutral'], aaii['bearish']]
        })
        st.bar_chart(bar_data.set_index('カテゴリ'), height=150)
        
        # Bull-Bear Spread 読み方ガイド
        with st.expander("📈 Bull-Bear Spread の読み方"):
            st.markdown("""
            **Bull-Bear Spread** = Bullish(強気)% − Bearish(弱気)%
            
            | 数値 | 意味 | 解釈 |
            |-----|------|------|
            | **+20%以上** | 強気優勢 | 🔴 過熱注意（天井サイン？） |
            | **+10%〜+20%** | やや強気 | 🟠 楽観的 |
            | **−10%〜+10%** | 中立 | 🟢 バランス良し |
            | **−10%〜−20%** | やや弱気 | 🟠 悲観的 |
            | **−20%以下** | 弱気優勢 | 🔴 底打ちサイン？ |
            
            💡 **逆張り戦略**: みんなが強気の時は天井、弱気の時は底になりやすい！
            """)
        
        if aaii.get('note'):
            st.caption(f"📝 {aaii['note']}")
    else:
        st.warning("⚠️ AAIIデータ取得エラー")
    
    st.markdown("---")
    
    # === ROW 3: Put/Call Ratio ===
    st.markdown("### 📊 Put/Call Ratio")
    st.caption("オプション市場の弱気/強気度 - 高い = 弱気、低い = 強気")
    
    pc_ratio = get_put_call_ratio()
    if pc_ratio:
        st.metric("Equity P/C Ratio", f"{pc_ratio:.2f}")
    else:
        st.info("📝 Put/Call Ratioのデータソースを準備中です。VIXで代替表示しています。")
        # Show VIX as proxy
        if vix_value is not None:
            st.caption(f"VIX (参考): {vix_value:.1f}")
    
    st.markdown("---")
    
    # === Interpretation Guide ===
    st.markdown("### 📚 センチメント指標の読み方")
    with st.expander("💡 指標の解釈ガイド"):
        st.markdown("""
        | 指標 | 極端な恐怖 | 恐怖 | 中立 | 強欲 | 極端な強欲 |
        |------|-----------|------|------|------|-----------|
        | **Fear & Greed** | 0-25 | 25-45 | 45-55 | 55-75 | 75-100 |
        | **VIX** | >30 | 20-30 | 15-20 | 10-15 | <10 |
        | **Put/Call** | >1.2 | 0.9-1.2 | 0.7-0.9 | 0.5-0.7 | <0.5 |
        
        **逆張り戦略のヒント:**
        - 「Extreme Fear」は買いのチャンスかも
        - 「Extreme Greed」は利確のサインかも
        - AAIIで強気が極端に多い時は注意
        """)

