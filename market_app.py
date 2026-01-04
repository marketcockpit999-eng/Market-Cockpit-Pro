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
                      'Credit_Spread', 'US_TNX', 'T10Y2Y', 'ON_RRP']
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
        'indicators': ['M2SL', 'M2REAL', 'CPI', 'Unemployment', 'UNRATE', 'CorePCE', 
                      'ConsumerSent', 'CN_M2', 'JP_M2', 'EU_M2',
                      'CN_CPI', 'JP_CPI', 'EU_CPI']
    },
    # Quarterly data
    'quarterly': {
        'fresh': 100,    # 🟢 ≤100 days old
        'stale': 120,    # 🟡 101-120 days old
        'critical': 150, # 🔴 >120 days old
        'indicators': ['Lending_Standards', 'CI_Std_Large', 'CI_Std_Small', 'CI_Demand',
                      'CRE_Std_Construction', 'CRE_Std_Office', 'CRE_Std_Multifamily', 'CRE_Demand']
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
    # Monthly
    'M2SL': '月次', 'M2REAL': '月次', 'CPI': '月次', 'Unemployment': '月次', 'UNRATE': '月次',
    'CorePCE': '月次', 'ConsumerSent': '月次', 'CN_M2': '月次', 'JP_M2': '月次', 'EU_M2': '月次',
    'CN_CPI': '月次', 'JP_CPI': '月次', 'EU_CPI': '月次', 'US_Real_M2_Index': '月次',
    # Quarterly
    'Lending_Standards': '四半期',
    'CI_Std_Large': '四半期', 'CI_Std_Small': '四半期', 'CI_Demand': '四半期',
    'CRE_Std_Construction': '四半期', 'CRE_Std_Office': '四半期', 'CRE_Std_Multifamily': '四半期', 'CRE_Demand': '四半期',
    # Monthly (SLOOS Loan Balances)
    'CI_Loans': '月次',
    # Weekly (SLOOS Loan Balances)
    'CRE_Loans': '週次',
}

def get_data_freshness_status(last_valid_dates: dict) -> dict:
    """
    Check data freshness for all indicators.
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
            last_date = datetime.strptime(date_str, '%Y-%m-%d').date()
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
                'days_old': days_old,
                'status': status,
                'category': category,
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

# ========== DATA FUNCTIONS ==========
@st.cache_data(ttl=600, show_spinner=False)
def get_market_data(_csv_mtime=None):
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
    mil_to_bil = ['Fed_Assets', 'TGA', 'Reserves', 'SOMA_Total', 'Bank_Cash', 'SRF', 'FIMA', 'Primary_Credit', 'Total_Loans', 'SOMA_Bills', 'M2SL', 'M2REAL', 'ICSA', 'CI_Loans', 'CRE_Loans']
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
    
    # Forward fill missing data (for display continuity)
    df = df.ffill()
    
    # Store metadata as a DataFrame attribute (accessible in display functions)
    df.attrs['last_valid_dates'] = last_valid_dates
    
    # Note: All data (including SOMA_Bills via WHTLSBL) is now fetched from FRED API
    # Manual data override has been removed
    
    return df

def show_metric(label, series, unit="", explanation_key="", notes="", alert_func=None):
    """メトリック表示ヘルパー"""
    if series is None or (hasattr(series, 'isna') and series.isna().all()):
        val = None
        delta = None
        latest_date = None
    else:
        val = series.iloc[-1] if hasattr(series, 'iloc') else series
        if hasattr(series, 'iloc') and len(series) > 1:
            delta = val - series.iloc[-2]
        else:
            delta = None
        
        # Get actual last valid data date from DataFrame metadata
        latest_date = None
        if hasattr(series, 'name') and hasattr(df, 'attrs') and 'last_valid_dates' in df.attrs:
            col_name = series.name
            if col_name in df.attrs['last_valid_dates']:
                latest_date = df.attrs['last_valid_dates'][col_name]  # Already a string
    
    help_text = EXPLANATIONS.get(explanation_key, "")
    
    if alert_func and val is not None and alert_func(val):
        st.metric(label, f"{val:.1f} {unit}" if val is not None else "N/A", 
                 delta=f"{delta:+.1f}" if delta is not None else None,
                 help=help_text, delta_color="inverse")
    else:
        st.metric(label, f"{val:.1f} {unit}" if val is not None else "N/A",
                 delta=f"{delta:+.1f}" if delta is not None else None,
                 help=help_text)
    
    # Display data source update date with frequency
    if latest_date:
        freq_label = DATA_FREQUENCY.get(explanation_key, '')
        if freq_label:
            st.caption(f"📅 {latest_date} ({freq_label})")
        else:
            st.caption(f"📅 {latest_date}")
    
    if notes:
        st.caption(notes)

def show_metric_with_sparkline(label, series, df_column, unit="", explanation_key="", notes="", alert_func=None):
    """メトリック + スパークライン（ミニトレンドチャート）を表示"""
    if series is None or (hasattr(series, 'isna') and series.isna().all()):
        val = None
        delta = None
        latest_date = None
    else:
        val = series.iloc[-1] if hasattr(series, 'iloc') else series
        if hasattr(series, 'iloc') and len(series) > 1:
            delta = val - series.iloc[-2]
        else:
            delta = None
        
        # Get actual last valid data date from DataFrame metadata
        latest_date = None
        if hasattr(df, 'attrs') and 'last_valid_dates' in df.attrs:
            if df_column in df.attrs['last_valid_dates']:
                latest_date = df.attrs['last_valid_dates'][df_column]  # Already a string
    
    help_text = EXPLANATIONS.get(explanation_key, "")
    
    # メトリック表示
    if alert_func and val is not None and alert_func(val):
        st.metric(label, f"{val:.1f} {unit}" if val is not None else "N/A", 
                 delta=f"{delta:+.1f}" if delta is not None else None,
                 help=help_text, delta_color="inverse")
    else:
        st.metric(label, f"{val:.1f} {unit}" if val is not None else "N/A",
                 delta=f"{delta:+.1f}" if delta is not None else None,
                 help=help_text)
    
    # Display data source update date with frequency
    if latest_date:
        freq_label = DATA_FREQUENCY.get(df_column, '')
        if freq_label:
            st.caption(f"📅 {latest_date} ({freq_label})")
        else:
            st.caption(f"📅 {latest_date}")
    
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
            height=80,
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
    df_for_download = get_market_data(csv_mtime)
    csv_data = df_for_download.to_csv()
    st.download_button(
        "📥 Download CSV",
        csv_data,
        "market_cockpit_data.csv",
        "text/csv",
        key="download_csv_main"
    )

# Load Data
df = get_market_data(csv_mtime)

# Data Health Check
with st.sidebar:
    st.markdown("---")
    st.subheader("📡 Data Health Monitor")
    
    # Current time display
    import datetime
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.caption(f"🕐 現在時刻: {current_time}")
    st.caption("")  # Spacing
    
    # Data freshness check
    if hasattr(df, 'attrs') and 'last_valid_dates' in df.attrs:
        freshness = get_data_freshness_status(df.attrs['last_valid_dates'])
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
        
        # Summary counts
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🟢 Fresh", summary['fresh_count'])
            st.metric("🔴 Critical", summary['critical_count'])
        with col2:
            st.metric("🟡 Stale", summary['stale_count'])
            st.metric("⚫ Missing", summary['missing_count'])
        
        # Detailed view in expander
        with st.expander("📋 詳細レポート", expanded=False):
            st.markdown("##### 🔴 要確認 (Critical)")
            if freshness['critical']:
                for ind in freshness['critical']:
                    detail = freshness['details'][ind]
                    st.markdown(f"- **{ind}**: {detail['days_old']}日前 ({detail['last_date']})")
            else:
                st.caption("なし ✅")
            
            st.markdown("##### 🟡 更新遅れ (Stale)")
            if freshness['stale']:
                for ind in freshness['stale']:
                    detail = freshness['details'][ind]
                    st.markdown(f"- **{ind}**: {detail['days_old']}日前 ({detail['last_date']})")
            else:
                st.caption("なし ✅")
            
            st.markdown("##### 🟢 最新 (Fresh)")
            st.caption(f"{len(freshness['fresh'])} 項目が最新データ")
        
        # Warning for AI Analysis
        if summary['critical_count'] > 0 or summary['stale_count'] > 3:
            st.warning(f"⚠️ {summary['critical_count'] + summary['stale_count']} 項目のデータが古い可能性があります。AI分析の精度に影響する場合があります。")
    else:
        total_cols = len(df.columns)
        valid_cols = sum(1 for c in df.columns if not df[c].isna().all())
        st.metric("Valid Series", f"{valid_cols}/{total_cols}")
    
    st.markdown("---")
    st.info("💡 すべてのデータはFRED APIから自動取得されます（SOMA Bills: WHTLSBL, Total Loans: WLCFLL, Primary Credit: WLCFLPCL）")

# Tabs
tabs = st.tabs(["📊 Liquidity & Rates", "🌏 Global Money & FX", "📈 US Economic Data", "🤖 AI Analysis", "🎲 Monte Carlo", "📰 Market Voices"])

# Tab 1: Liquidity & Rates
with tabs[0]:
    st.subheader("🏦 Liquidity & The Fed")
    
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
        show_metric_with_sparkline("SOFR", df.get('SOFR'), 'SOFR', "%", "SOFR", notes="担保付金利")
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
    st.subheader("💰 C&I Lending (商工業融資) - SLOOS")
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
    st.subheader("🏢 CRE Lending (商業用不動産融資) - SLOOS")
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
        show_metric_with_sparkline("Credit Spread", df.get('Credit_Spread'), 'Credit_Spread', "%", notes="ジャンク債スプレッド")
        if 'Credit_Spread' in df.columns and not df.get('Credit_Spread', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['Credit_Spread']], height=200)
    
    with col3:
        # US 10Y Yield
        st.markdown("#### US 10Y Yield")
        show_metric_with_sparkline("US 10Y Yield", df.get('US_TNX'), 'US_TNX', "%", notes="長期金利")
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
        show_metric_with_sparkline("Dollar Index", df.get('DXY'), 'DXY', "pt", notes="ドル強弱指数")
        if 'DXY' in df.columns and not df.get('DXY', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['DXY']], height=150)
    
    with col2:
        st.markdown("#### USD/JPY")
        show_metric_with_sparkline("USD/JPY", df.get('USDJPY'), 'USDJPY', "¥", notes="円キャリー")
        if 'USDJPY' in df.columns and not df.get('USDJPY', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['USDJPY']], height=150)
    
    with col3:
        st.markdown("#### EUR/USD")
        show_metric_with_sparkline("EUR/USD", df.get('EURUSD'), 'EURUSD', "$", notes="ユーロドル")
        if 'EURUSD' in df.columns and not df.get('EURUSD', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['EURUSD']], height=150)
    
    with col4:
        st.markdown("#### USD/CNY")
        show_metric_with_sparkline("USD/CNY", df.get('USDCNY'), 'USDCNY', "CNY", notes="人民元")
        if 'USDCNY' in df.columns and not df.get('USDCNY', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['USDCNY']], height=150)
    
    # --- Commodities Section ---
    st.markdown("---")
    st.markdown("### 🛢️ Commodities")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("#### Gold")
        show_metric_with_sparkline("Gold", df.get('Gold'), 'Gold', "$", notes="金先物")
        if 'Gold' in df.columns and not df.get('Gold', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['Gold']], height=150)
    
    with col2:
        st.markdown("#### Silver")
        show_metric_with_sparkline("Silver", df.get('Silver'), 'Silver', "$", notes="銀先物")
        if 'Silver' in df.columns and not df.get('Silver', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['Silver']], height=150)
    
    with col3:
        st.markdown("#### Oil (WTI)")
        show_metric_with_sparkline("Oil", df.get('Oil'), 'Oil', "$", notes="原油先物")
        if 'Oil' in df.columns and not df.get('Oil', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['Oil']], height=150)
    
    with col4:
        st.markdown("#### Copper")
        show_metric_with_sparkline("Copper", df.get('Copper'), 'Copper', "$", notes="銅先物（景気先行指標）")
        if 'Copper' in df.columns and not df.get('Copper', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['Copper']], height=150)
    
    # --- Crypto Section ---
    st.markdown("---")
    st.markdown("### 🪙 Cryptocurrency")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Bitcoin (BTC)")
        show_metric_with_sparkline("BTC", df.get('BTC'), 'BTC', "$", notes="リスクオン指標")
        if 'BTC' in df.columns and not df.get('BTC', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['BTC']], height=200)
    
    with col2:
        st.markdown("#### Ethereum (ETH)")
        show_metric_with_sparkline("ETH", df.get('ETH'), 'ETH', "$", notes="DeFi基盤")
        if 'ETH' in df.columns and not df.get('ETH', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['ETH']], height=200)

# Tab 3: US Economic Data
with tabs[2]:
    st.subheader("📈 US Economic Data")
    st.caption("💡 景気循環と労働市場の先行指標")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📉 Yield Curve (2Y-10Y Spread)")
        st.caption("マイナス = 景気後退シグナル")
        show_metric_with_sparkline("2Y-10Y Spread", df.get('T10Y2Y'), 'T10Y2Y', "%", notes="逆イールド警戒")
        if 'T10Y2Y' in df.columns and not df.get('T10Y2Y', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['T10Y2Y'], name='2Y-10Y Spread', line=dict(color='cyan')))
            fig.add_hline(y=0, line_dash='dash', line_color='red', annotation_text="逆イールド警戒ライン")
            fig.update_layout(template='plotly_dark', height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="pc_4")
    
    with col2:
        st.markdown("#### 📊 Initial Jobless Claims")
        st.caption("週次更新・労働市場の健全性")
        show_metric_with_sparkline("Jobless Claims", df.get('ICSA'), 'ICSA', "K", notes="新規失業保険申請")
        if 'ICSA' in df.columns and not df.get('ICSA', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend (過去2年間)")
            st.line_chart(df[['ICSA']], height=300)
    
    # Second row of economic indicators
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 👷 Unemployment Rate")
        st.caption("サーム・ルール監視（月次）")
        show_metric_with_sparkline("Unemployment", df.get('UNRATE'), 'UNRATE', "%", notes="失業率")
        if 'UNRATE' in df.columns and not df.get('UNRATE', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['UNRATE'], name='Unemployment', line=dict(color='orange')))
            # Sahm Rule: recession warning if 3-month avg rises 0.5pp above 12-month low
            fig.add_hline(y=4.0, line_dash='dash', line_color='yellow', annotation_text="警戒ライン")
            fig.update_layout(template='plotly_dark', height=250, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="pc_unrate")
    
    with col2:
        st.markdown("#### 💰 Core PCE Inflation")
        st.caption("FRBインフレ目標指標（月次）")
        show_metric_with_sparkline("Core PCE YoY", df.get('CorePCE'), 'CorePCE', "%", notes="FRB目標2%")
        if 'CorePCE' in df.columns and not df.get('CorePCE', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['CorePCE'], name='Core PCE', line=dict(color='orange')))
            fig.add_hline(y=2.0, line_dash='dash', line_color='green', annotation_text="FRB目標2%")
            fig.update_layout(template='plotly_dark', height=250, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="pc_corepce")
    
    with col3:
        st.markdown("#### 📈 Consumer Sentiment")
        st.caption("消費者信頼感（月次）")
        show_metric_with_sparkline("Sentiment", df.get('ConsumerSent'), 'ConsumerSent', "pt", notes="ミシガン大学")
        if 'ConsumerSent' in df.columns and not df.get('ConsumerSent', pd.Series()).isna().all():
            st.markdown("###### Long-term Trend")
            st.line_chart(df[['ConsumerSent']], height=250)

# Tab 4: AI Analysis
with tabs[3]:
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
            
            def add_metric(name, col_name, unit="", with_change=False, change_days=7):
                """Helper to add a metric to summary"""
                if col_name in df.columns:
                    data = df[col_name].dropna()
                    if len(data) > 0:
                        current = data.iloc[-1]
                        if with_change and len(data) >= change_days:
                            change = current - data.iloc[-change_days]
                            summary_parts.append(f"{name}: {current:.1f}{unit} ({change_days}日変化: {change:+.1f}{unit})")
                        else:
                            summary_parts.append(f"{name}: {current:.1f}{unit}")
            
            # === Fed Liquidity ===
            summary_parts.append("【FRB流動性】")
            add_metric("Net Liquidity", "Net_Liquidity", "B", True)
            add_metric("ON RRP", "ON_RRP", "B")
            add_metric("Bank Reserves", "Reserves", "B")
            add_metric("TGA", "TGA", "B")
            add_metric("Fed Assets (WALCL)", "Fed_Assets", "B")
            add_metric("SOMA Total", "SOMA_Total", "B")
            add_metric("SOMA Bills", "SOMA_Bills", "B", True)
            
            # === Rates & Plumbing ===
            summary_parts.append("\n【金利・市場配管】")
            add_metric("EFFR", "EFFR", "%")
            add_metric("IORB", "IORB", "%")
            add_metric("SOFR", "SOFR", "%")
            add_metric("SRF", "SRF", "B")
            add_metric("FIMA", "FIMA", "B")
            add_metric("Primary Credit", "Primary_Credit", "B")
            add_metric("Total Loans", "Total_Loans", "B")
            
            # === Banking Sector ===
            summary_parts.append("\n【銀行セクター】")
            add_metric("Bank Cash", "Bank_Cash", "B")
            add_metric("C&I Lending Std (Large)", "Lending_Standards", " pts")
            add_metric("C&I Lending Std (Small)", "CI_Std_Small", " pts")
            add_metric("C&I Demand", "CI_Demand", " pts")
            add_metric("C&I Loans", "CI_Loans", "B")
            add_metric("CRE Std (Construction)", "CRE_Std_Construction", " pts")
            add_metric("CRE Std (General)", "CRE_Std_Office", " pts")
            add_metric("CRE Loans", "CRE_Loans", "B", True)
            
            # === Risk & Bonds ===
            summary_parts.append("\n【リスク・債券】")
            add_metric("VIX", "VIX", "")
            add_metric("Credit Spread (HY)", "Credit_Spread", "%")
            add_metric("US 10Y Yield", "US_TNX", "%")
            add_metric("2Y-10Y Spread", "T10Y2Y", "%")
            
            # === Equity & Crypto ===
            summary_parts.append("\n【株式・仮想通貨】")
            if 'SP500' in df.columns:
                sp = df['SP500'].dropna()
                if len(sp) > 5:
                    change_pct = ((sp.iloc[-1] / sp.iloc[-5]) - 1) * 100
                    summary_parts.append(f"S&P 500: {sp.iloc[-1]:,.0f} (週間: {change_pct:+.1f}%)")
            add_metric("BTC", "BTC", "")
            add_metric("ETH", "ETH", "")
            
            # === FX ===
            summary_parts.append("\n【為替】")
            add_metric("DXY", "DXY", "")
            add_metric("USD/JPY", "USDJPY", "")
            add_metric("EUR/USD", "EURUSD", "")
            add_metric("USD/CNY", "USDCNY", "")
            
            # === Commodities ===
            summary_parts.append("\n【コモディティ】")
            add_metric("Gold", "Gold", "")
            add_metric("Silver", "Silver", "")
            add_metric("Oil (WTI)", "Oil", "")
            add_metric("Copper", "Copper", "")
            
            # === Economic Indicators ===
            summary_parts.append("\n【経済指標】")
            add_metric("Unemployment Rate", "UNRATE", "%")
            add_metric("Core PCE", "CorePCE", "%")
            add_metric("Consumer Sentiment", "ConsumerSent", "")
            add_metric("Initial Claims", "ICSA", "K")
            add_metric("M2 (Nominal)", "M2SL", "B")
            add_metric("M2 (Real)", "M2REAL", "B")
            
            # === Global M2 ===
            summary_parts.append("\n【グローバルM2】")
            add_metric("US Real M2 Index", "US_Real_M2_Index", "")
            add_metric("China M2", "CN_M2", "T CNY")
            add_metric("China Credit Impulse", "CN_Credit_Impulse", "%")
            add_metric("Japan M2", "JP_M2", "T JPY")
            add_metric("EU M2", "EU_M2", "T EUR")
            
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
        
        analysis_prompts = {
            "総合分析": """以下の市場データを分析し、日本語で以下の点について解説してください：
1. 現在の市場環境の概要
2. 注目すべきポイント
3. 今後の見通し（短期・中期）

簡潔かつ専門的な分析をお願いします。""",
            
            "リスク評価": """以下の市場データからリスク要因を特定し、日本語で分析してください：
1. 現在の主要リスク要因（高・中・低で評価）
2. 警戒すべきシグナル
3. リスク軽減のための注目ポイント""",
            
            "流動性分析": """以下の市場データから流動性状況を分析し、日本語で解説してください：
1. 現在の流動性レベル評価
2. Net Liquidity, ON RRP, TGA, Reservesの相互関係
3. 流動性の今後の見通し
4. 株式市場への影響""",
            
            "FRB政策分析": """以下の市場データからFRB政策の影響を分析し、日本語で解説してください：
1. 現在のFRB政策スタンス
2. RMP（Reserve Management Purchases）の進捗状況
3. 今後予想される政策変更
4. 市場への影響""",
            
            "投資アイデア": """以下の市場データを踏まえ、投資アイデアを日本語で提案してください：
1. 現在の市場環境の評価
2. 有望なセクター/資産クラス
3. リスク/リワード分析
4. 注意すべきポイント

※これは参考情報であり、投資助言ではありません。"""
        }
        
        # Helper function for Gemini (defined outside button to be reusable)
        def run_gemini_analysis(prompt):
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
            
            if "Gemini" in selected_ai and "Claude" not in selected_ai:
                # Gemini only
                with st.spinner("🔷 Gemini 3 Flash が分析中..."):
                    try:
                        result = run_gemini_analysis(full_prompt)
                        st.markdown("### 🔷 Gemini 3 Flash 分析結果")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"❌ Gemini エラー: {str(e)}")
            
            elif "Claude" in selected_ai and "Gemini" not in selected_ai:
                # Claude only
                with st.spinner("🟣 Claude Opus 4.5 が分析中..."):
                    try:
                        result = run_claude_analysis(full_prompt)
                        st.markdown("### 🟣 Claude Opus 4.5 分析結果")
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"❌ Claude エラー: {str(e)}")
            
            elif "デュアル" in selected_ai:
                # Dual AI comparison
                col_gemini, col_claude = st.columns(2)
                
                with col_gemini:
                    st.markdown("### 🔷 Gemini 3 Flash")
                    with st.spinner("分析中..."):
                        try:
                            gemini_result = run_gemini_analysis(full_prompt)
                            st.markdown(gemini_result)
                        except Exception as e:
                            st.error(f"❌ エラー: {str(e)}")
                
                with col_claude:
                    st.markdown("### 🟣 Claude Opus 4.5")
                    with st.spinner("分析中..."):
                        try:
                            claude_result = run_claude_analysis(full_prompt)
                            st.markdown(claude_result)
                        except Exception as e:
                            st.error(f"❌ エラー: {str(e)}")
            
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
            custom_prompt = f"""以下の市場データと質問に基づいて、日本語で回答してください。

【市場データ】
{market_summary}

【質問】
{user_question}

専門的かつ具体的に回答してください。"""
            
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

# Tab 5: Monte Carlo Simulation
with tabs[4]:
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

# Tab 6: Market Voices
with tabs[5]:
    st.subheader("📰 Market Voices")
    st.caption("💡 FRBニュースとマーケットに影響する発言")
    
    st.markdown("### 🏛️ Federal Reserve News")
    try:
        feed = feedparser.parse("https://www.federalreserve.gov/feeds/press_all.xml")
        for i, entry in enumerate(feed.entries[:5]):
            with st.expander(f"{entry.published[:10]} - {entry.title}"):
                st.write(entry.summary)
                st.markdown(f"[Read more]({entry.link})")
    except:
        st.error("ニュースフィードの取得に失敗しました")


