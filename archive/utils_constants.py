
# ========== SETTINGS ==========
FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"
PAGE_TITLE = "Market Cockpit Pro"
MANUAL_DATA_FILE = "manual_h41_data.csv"

# ========== DATA FRESHNESS MONITORING ==========
# Update frequency categories (in days)
# CANONICAL SOURCE: All 66 monitored indicators
DATA_FRESHNESS_RULES = {
    # Daily data (market days) - 22 items
    'daily': {
        'fresh': 3,      # 🟢 ≤3 days old
        'stale': 7,      # 🟡 4-7 days old
        'critical': 14,  # 🔴 >7 days old
        'indicators': ['EFFR', 'IORB', 'SOFR', 'SP500', 'VIX', 'HYG', 'DXY', 'USDJPY', 
                      'EURUSD', 'USDCNY', 'Gold', 'Silver', 'Oil', 'Copper', 'BTC', 'ETH',
                      'Credit_Spread', 'US_TNX', 'T10Y2Y', 'ON_RRP', 'FedFundsUpper', 'FedFundsLower']
    },
    # Weekly data (Fed H.4.1 etc) - 14 items
    'weekly': {
        'fresh': 10,     # 🟢 ≤10 days old
        'stale': 14,     # 🟡 11-14 days old
        'critical': 21,  # 🔴 >14 days old
        'indicators': ['Reserves', 'TGA', 'Fed_Assets', 'SOMA_Total', 'SOMA_Bills', 
                      'SRF', 'FIMA', 'Primary_Credit', 'Total_Loans', 'Bank_Cash', 'ICSA',
                      'Net_Liquidity', 'SomaBillsRatio', 'CRE_Loans']
    },
    # Monthly data - 21 items
    'monthly': {
        'fresh': 45,     # 🟢 ≤45 days old
        'stale': 60,     # 🟡 46-60 days old
        'critical': 90,  # 🔴 >60 days old
        'indicators': ['M2SL', 'M2REAL', 'CPI', 'CPICore', 'PPI', 'Unemployment', 'UNRATE', 'CorePCE', 
                      'ConsumerSent', 'CN_M2', 'JP_M2', 'EU_M2', 'NFP', 'ADP', 'AvgHourlyEarnings', 'JOLTS',
                      'RetailSales', 'CN_CPI', 'JP_CPI', 'EU_CPI', 'US_Real_M2_Index', 'CI_Loans']
    },
    # Quarterly data - 9 items
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
# FRED UNITS: Official unit documentation for each series
# This prevents unit confusion errors (like the ADP Persons vs Thousands issue)
FRED_UNITS = {
    # Liquidity (FRB H.4.1) - Millions, converted to Billions by /1000
    'Reserves': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'TGA': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'Fed_Assets': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'SOMA_Total': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'SOMA_Bills': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'Bank_Cash': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    
    # Plumbing facilities (Millions -> Billions)
    'SRF': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'FIMA': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'Primary_Credit': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},
    'Total_Loans': {'unit': 'Millions', 'convert_to': 'Billions', 'divisor': 1000},

    # Already in Billions (Do NOT divide for Net Liquidity calculation)
    'ON_RRP': {'unit': 'Billions', 'convert_to': None, 'divisor': 1},

    # Money Supply (Billions -> Trillions as in market_app.py)
    'M2SL': {'unit': 'Billions', 'convert_to': 'Trillions', 'divisor': 1000},
    'M2REAL': {'unit': 'Billions', 'convert_to': 'Trillions', 'divisor': 1000},
    
    # Lending (Billions -> Trillions as in market_app.py)
    'CI_Loans': {'unit': 'Billions', 'convert_to': 'Trillions', 'divisor': 1000},
    'CRE_Loans': {'unit': 'Billions', 'convert_to': 'Trillions', 'divisor': 1000},

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

    # Employment
    'NFP': {'unit': 'Thousands of Persons', 'convert_to': None, 'divisor': 1},
    'ADP': {'unit': 'Persons', 'convert_to': 'Thousands', 'divisor': 1000},
    'JOLTS': {'unit': 'Thousands', 'convert_to': None, 'divisor': 1},
    'ICSA': {'unit': 'Persons', 'convert_to': 'Thousands', 'divisor': 1000},
    'AvgHourlyEarnings': {'unit': 'Dollars per Hour', 'convert_to': None, 'divisor': 1}
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
