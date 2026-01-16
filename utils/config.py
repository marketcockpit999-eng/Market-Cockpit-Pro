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
GEMINI_MODEL = "gemini-3-flash-preview"
CLAUDE_MODEL = "claude-opus-4-5-20251101"

# =============================================================================
# MANUAL GLOBAL M2 DATA
# FREDで取得できない国のM2データ（手動更新）
# =============================================================================
MANUAL_GLOBAL_M2 = {
    'CN_M2': {
        'value': 336.9,      # 単位: Trillion CNY
        'date': '2025-11',   # 対象月
        'source': 'PBoC',    # 人民銀行
        'cpi': 0.2,          # CPIインフレ率(%)
    },
    'JP_M2': {
        'value': 1260,       # 単位: Trillion JPY
        'date': '2025-11',
        'source': 'BOJ',
        'cpi': 2.9,
    },
    'EU_M2': {
        'value': 15.6,       # 単位: Trillion EUR
        'date': '2025-11',
        'source': 'ECB',
        'cpi': 2.1,
    },
}

# =============================================================================
# EXPLANATIONS (UI tooltip text)
# =============================================================================
EXPLANATIONS = {
    "Net_Liquidity": "【ネットリクイディティ】\n市場に出回る「真の資金量」。(FRB総資産 - TGA - RRP) で計算されます。",
    "Reserves": "【銀行準備預金】\n民間銀行がFRBに預けているお金。",
    "TGA": "【TGA (財務省一般口座)】\n政府の銀行口座。",
    "ON_RRP": "【ON RRP】\nMMFなどがFRBにお金を預ける場所。",
    "VIX": "【VIX指数】\n恐怖指数。20以上で市場の不安が高まっている状態です。",
    "Bank_Cash": "【銀行の現金保有】\n全米の銀行が保有する現金資産の推移。",
    "Lending_Standards": "【C&I Lending Tightening】\n銀行の融資態度を示す純割合。",
    "SRF": "【Standing Repo Facility】\n国内リポ市場の流動性。",
    "FIMA": "【FIMA Repo Facility】\n海外の中央銀行向け融資。",
    "SOFR": "【SOFR】\n国債を担保にした資金調達コスト。",
    "Primary": "【Primary Credit】\n健全な銀行向けの緊急融資。",
    "Window": "【Total Loans】\nFRBによる金融機関への貸出総額。",
    "SOMA_Total": "【SOMA総資産】\nFRBが保有する国債やMBSの総額。",
    "SOMA_Bills": "【SOMA Bills (短期国債)】\nFRBが保有する短期国債。",
    "SomaBillsRatio": "【SOMA Bills比率】\nFRBの総資産に占める短期国債の割合。",
    "M2SL": "【通貨供給量 M2】\n世の中に流通しているマネーの総量。",
    "CI_Std_Large": "【C&I融資基準（大・中堅企業）】\n0を超えると貸し渋り。",
    "CI_Std_Small": "【C&I融資基準（小企業）】\n中小企業の資金繰りの先行指標。",
    "CI_Demand": "【C&I融資需要】\n企業の設備投資意欲を測定。",
    "CI_Loans": "【C&I融資残高】\n商工業向け融資の総額。",
    "CRE_Std_Construction": "【CRE融資基準（建設・土地開発）】\n不動産開発の蛇口。",
    "CRE_Std_Office": "【CRE融資基準（オフィス等）】\n既存物件の借り換え難易度。",
    "CRE_Std_Multifamily": "【CRE融資基準（集合住宅）】\n居住用不動産市場の流動性。",
    "CRE_Demand": "【CRE融資需要】\n不動産投資意欲。",
    "CRE_Loans": "【CRE融資残高（週次）】\n週次で追える最速のデータ。",
    # Financial Stress
    "NFCI": "【NFCI】\nシカゴ連銀金融環境指数。+で引締、-で緩和。",
    "MOVE": "【MOVE Index】\n債券恐怖指数。VIXより先に反応することが多い。",
    "Small_Bank_Deposits": "【地銀預金】\n急減は取り付け騒ぎの前兆。",
    "CC_Delinquency": "【クレカ延滞率】\n消費者ストレスの先行指標。",
    "CP_Spread": "【CP-FFスプレッド】\n企業短期資金調達ストレス。",
    "Breakeven_10Y": "【10年期待インフレ】\n市場のインフレ期待。",
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
