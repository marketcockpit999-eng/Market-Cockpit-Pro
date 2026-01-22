# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Configuration
================================================================================
⚠️  INDICATOR DEFINITIONS HAVE MOVED TO utils/indicators.py
    This file now imports from indicators.py for backward compatibility.
    
    To add a new indicator, edit utils/indicators.py ONLY.
================================================================================
"""

# =============================================================================
# IMPORT INDICATOR DEFINITIONS FROM SINGLE SOURCE OF TRUTH
# =============================================================================
from .indicators import (
    INDICATORS,
    FRED_INDICATORS,
    YAHOO_INDICATORS,
    DATA_FREQUENCY,
    DATA_FRESHNESS_RULES,
    VALIDATION_RANGES,
    FRED_UNITS,
    get_fred_indicators,
    get_yahoo_indicators,
    get_data_frequency,
    get_freshness_rules,
    get_validation_ranges,
    get_fred_units,
    get_indicators_for_page,
    get_indicators_for_ai,
    get_indicators_by_category,
    get_indicator_info,
    get_all_indicator_names,
)

# =============================================================================
# API KEYS & SETTINGS (NOT moved to indicators.py)
# =============================================================================
FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"
PAGE_TITLE = "Market Cockpit Pro"
MANUAL_DATA_FILE = "manual_h41_data.csv"

# AI Model Names
GEMINI_MODEL = "gemini-2.5-pro"
CLAUDE_MODEL = "claude-opus-4-5-20251101"

# =============================================================================
# MANUAL GLOBAL M2 DATA (REMOVED)
# Non-US M2 data removed due to unreliable FRED data sources
# =============================================================================
MANUAL_GLOBAL_M2 = {}  # Empty - no longer used

# =============================================================================
# EXPLANATIONS (UI tooltip text)
# =============================================================================
EXPLANATIONS = {
    "Net_Liquidity": "Net Liquidity\nMarket's true fuel. Calculated as (Fed Assets - TGA - RRP).",
    "Reserves": "Bank Reserves\nMoney that private banks hold at the Fed.",
    "TGA": "TGA (Treasury General Account)\nGovernment's bank account at the Fed.",
    "ON_RRP": "ON RRP\nWhere MMFs park excess cash at the Fed.",
    "VIX": "VIX Index\nFear gauge. Above 20 signals elevated market anxiety.",
    "Bank_Cash": "Bank Cash Holdings\nCash assets held by all US banks.",
    "Lending_Standards": "C&I Lending Tightening\nNet % of banks tightening. + is tight, - is loose.",
    "SRF": "Standing Repo Facility\nDomestic repo market liquidity backstop.",
    "FIMA": "FIMA Repo Facility\nForeign central bank dollar lending.",
    "SOFR": "SOFR\nSecured overnight financing rate (Treasury-collateralized).",
    "Primary": "Primary Credit\nEmergency lending to healthy banks.",
    "Window": "Total Loans\nTotal FRB lending to financial institutions.",
    "SOMA_Total": "SOMA Total Assets\nFed holdings of Treasuries and MBS.",
    "SOMA_Bills": "SOMA Bills (T-Bills)\nFed's short-term Treasury holdings.",
    "SomaBillsRatio": "SOMA Bills Ratio\nShare of T-Bills in Fed's total assets.",
    "M2SL": "M2 Money Supply\nTotal money circulating in the economy.",
    "CI_Std_Large": "C&I Standards (Large/Mid)\nAbove 0 = tightening. 40%+ = strong recession signal.",
    "CI_Std_Small": "C&I Standards (Small)\nLeading indicator for SME funding & employment.",
    "CI_Demand": "C&I Loan Demand\nMeasures corporate capex appetite.",
    "CI_Loans": "C&I Loan Balance\nTotal commercial & industrial loans.",
    "CRE_Std_Construction": "CRE Standards (Construction)\nReal estate development gateway.",
    "CRE_Std_Office": "CRE Standards (Office)\nRefinancing difficulty indicator.",
    "CRE_Std_Multifamily": "CRE Standards (Multifamily)\nResidential real estate liquidity.",
    "CRE_Demand": "CRE Loan Demand\nReal estate investment appetite.",
    "CRE_Loans": "CRE Loan Balance (Weekly)\nFastest available CRE lending data.",
    # Financial Stress
    "NFCI": "NFCI\nChicago Fed Financial Conditions. + is tight, - is loose.",
    "MOVE": "MOVE Index\nBond fear index. Often reacts before VIX.",
    "Small_Bank_Deposits": "Small Bank Deposits\nSharp decline = bank run warning.",
    "CC_Delinquency": "Credit Card Delinquency\nLeading indicator of consumer stress.",
    "CP_Spread": "CP-FF Spread\nCorporate short-term funding stress.",
    "Breakeven_10Y": "10Y Breakeven\nMarket inflation expectations.",
}

# =============================================================================
# RSS & NEWS
# =============================================================================
MONITORED_AGENCIES = {
    "FRB": {"domain": "federalreserve.gov", "rss": "https://www.federalreserve.gov/feeds/press_all.xml", "label": "🏦 Federal Reserve"},
    "Treasury": {"domain": "treasury.gov", "rss": "https://home.treasury.gov/news/press-releases/rss.xml", "label": "💵 Treasury"},
}

RSS_FEEDS = {
    "🏛️ Fed": "https://www.federalreserve.gov/feeds/press_all.xml",
    "🇪🇺 ECB": "https://www.ecb.europa.eu/rss/press.html",
    "🇯🇵 BOJ": "https://www.boj.or.jp/rss/news.xml",
    "📈 Markets": "https://news.google.com/rss/search?q=stock+market+breaking&hl=en-US&gl=US&ceid=US:en",
}

CONTEXT_KEYWORDS = {
    "🌐 地政学リスク (Geopolitics)": {"main_keyword": "geopolitical risk", "desc": "制裁・貿易戦争・軍事紛争"},
    "📊 マクロ経済 (Macro)": {"main_keyword": "recession risk", "desc": "景気後退・インフレ・GDP"},
    "🏛️ 中央銀行 (Central Bank)": {"main_keyword": "Fed policy", "desc": "利下げ・QT・バランスシート"},
    "💧 流動性・配管 (Liquidity/Plumbing)": {"main_keyword": "liquidity crisis", "desc": "レポ・準備金・ON RRP"},
    "🛢️ コモディティ (Commodities)": {"main_keyword": "oil price gold", "desc": "原油・金・銅・供給制約"},
    "₿ 仮想通貨 (Crypto)": {"main_keyword": "Bitcoin regulation", "desc": "BTC規制・ETF・ステーブルコイン"},
    "🏦 銀行・信用 (Banking/Credit)": {"main_keyword": "bank stress", "desc": "銀行破綻・信用収縮・CRE"},
    "🏢 不動産 (Real Estate)": {"main_keyword": "commercial real estate", "desc": "商業用不動産・オフィス空室"},
    "💵 通貨・為替 (Currency/FX)": {"main_keyword": "dollar strength", "desc": "ドル高・円安・介入"},
    "🇨🇳 中国 (China)": {"main_keyword": "China economy", "desc": "中国経済・不動産危機・資本流出"},
    "🇪🇺 欧州 (Europe)": {"main_keyword": "ECB policy", "desc": "ECB・エネルギー危機・債務"},
    "🌍 新興国 (Emerging Markets)": {"main_keyword": "emerging market crisis", "desc": "新興国危機・通貨暴落・IMF"},
}
