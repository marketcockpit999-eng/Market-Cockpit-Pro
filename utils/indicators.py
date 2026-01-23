# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Unified Indicator Registry
================================================================================
SINGLE SOURCE OF TRUTH for all market indicators.

Adding a new indicator? Just add ONE entry to INDICATORS dict below.
All other parts of the app will automatically pick it up.

Example:
    'NEW_INDICATOR': {
        'source': 'FRED',           # FRED, YAHOO, or MANUAL
        'id': 'FRED_SERIES_ID',     # Ticker/Series ID
        'unit': '%',                # Display unit
        'frequency': 'monthly',     # daily, weekly, monthly, quarterly
        'freshness': 'monthly',     # For data freshness monitoring
        'category': 'economy',      # For grouping
        'ui_page': '03_us_economic', # Which page displays this
        'ai_include': True,         # Include in AI summary?
        'ai_section': '米経済指標', # AI summary section
        'notes': 'Description',     # Human-readable notes
        'validation': (0, 100),     # Optional: (min, max) for validation
        'divisor': 1000,            # Optional: unit conversion divisor
    },
================================================================================
"""

# =============================================================================
# UNIFIED INDICATOR REGISTRY
# =============================================================================
INDICATORS = {
    # =========================================================================
    # FED LIQUIDITY & RATES (Page 01)
    # =========================================================================
    'ON_RRP': {
        'source': 'FRED',
        'id': 'RRPONTSYD',
        'unit': 'B',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fed_liquidity',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'FRB流動性',
        'notes': 'Overnight Reverse Repo (余剰資金の滞留)',
        'validation': (0, 3000),
        'divisor': 1000,  # Millions → Billions
    },
    'Reserves': {
        'source': 'FRED',
        'id': 'WRESBAL',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'fed_liquidity',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'FRB流動性',
        'notes': '銀行準備預金',
        'validation': (0, 5000),
        'divisor': 1000,
    },
    'TGA': {
        'source': 'FRED',
        'id': 'WTREGEN',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'fed_liquidity',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'FRB流動性',
        'notes': '財務省一般口座',
        'validation': (0, 2000),
        'divisor': 1000,
    },
    'Fed_Assets': {
        'source': 'FRED',
        'id': 'WALCL',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'fed_liquidity',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'FRB流動性',
        'notes': 'FRB総資産',
        'validation': (4000, 12000),
        'divisor': 1000,
    },
    'SOMA_Total': {
        'source': 'FRED',
        'id': 'WALCL',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'fed_liquidity',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'FRB流動性',
        'notes': 'SOMA総資産',
        'validation': (4000, 12000),
        'divisor': 1000,
    },
    'SOMA_Treasury': {
        'source': 'FRED',
        'id': 'TREAST',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'fed_liquidity',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'FRB流動性',
        'notes': 'SOMA国債保有総額（Treasury Securities Held Outright）',
        'divisor': 1000,
    },
    'SOMA_Bills': {
        'source': 'FRED',
        'id': 'WSHOBL',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'fed_liquidity',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'FRB流動性',
        'notes': 'SOMA短期国債保有（RMP監視の核心指標）',
        'divisor': 1000,
    },

    'SRF': {
        'source': 'FRED',
        'id': 'WORAL',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'fed_plumbing',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'FRB流動性',
        'notes': 'Standing Repo Facility',
        'divisor': 1000,
    },
    'FIMA': {
        'source': 'FRED',
        'id': 'H41RESPPALGTRFNWW',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'fed_plumbing',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'FRB流動性',
        'notes': 'FIMA Repo Facility',
        'divisor': 1000,
    },
    'Primary_Credit': {
        'source': 'FRED',
        'id': 'WLCFLPCL',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'fed_plumbing',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'FRB流動性',
        'notes': '割引窓口プライマリークレジット',
        'divisor': 1000,
    },
    'Total_Loans': {
        'source': 'FRED',
        'id': 'WLCFLL',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'fed_plumbing',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'FRB流動性',
        'notes': 'FRB貸出総額',
        'divisor': 1000,
    },
    
    # === Rates ===
    'EFFR': {
        'source': 'FRED',
        'id': 'EFFR',
        'unit': '%',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'rates',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '金利',
        'notes': '実効FF金利',
        'validation': (0, 15),
    },
    'IORB': {
        'source': 'FRED',
        'id': 'IORB',
        'unit': '%',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'rates',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '金利',
        'notes': '準備預金付利',
        'validation': (0, 15),
    },
    'SOFR': {
        'source': 'FRED',
        'id': 'SOFR',
        'unit': '%',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'rates',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '金利',
        'notes': 'SOFR',
        'validation': (0, 15),
    },
    'FedFundsUpper': {
        'source': 'FRED',
        'id': 'DFEDTARU',
        'unit': '%',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'rates',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '金利',
        'notes': 'FF金利上限',
        'validation': (0, 15),
    },
    'FedFundsLower': {
        'source': 'FRED',
        'id': 'DFEDTARL',  # Updated 2026-01-21: Old DFEDTAR was DISCONTINUED in 2008
        'unit': '%',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'rates',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '金利',
        'notes': 'FF金利下限',
        'validation': (0, 15),
    },
    'US_TNX': {
        'source': 'FRED',
        'id': 'DGS10',
        'unit': '%',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'rates',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '金利',
        'notes': '米10年国債利回り',
        'validation': (0, 20),
    },
    'T10Y2Y': {
        'source': 'FRED',
        'id': 'T10Y2Y',
        'unit': '%',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'rates',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '金利',
        'notes': '10年-2年スプレッド（逆イールド）',
        'validation': (-5, 5),
    },
    'Credit_Spread': {
        'source': 'FRED',
        'id': 'BAMLH0A0HYM2',
        'unit': '%',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'rates',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '金利',
        'notes': 'ハイイールドスプレッド',
        'validation': (0, 30),
    },
    
    # =========================================================================
    # GLOBAL MONEY SUPPLY (Page 02)
    # =========================================================================
    'M2SL': {
        'source': 'FRED',
        'id': 'M2SL',
        'unit': 'T',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'money_supply',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '通貨供給',
        'notes': '米M2',
        'divisor': 1000,  # Billions → Trillions
    },
    'M2REAL': {
        'source': 'FRED',
        'id': 'M2REAL',
        'unit': 'T',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'money_supply',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '通貨供給',
        'notes': '米実質M2',
        'divisor': 1000,
    },
    # NOTE: Non-US M2 (CN, JP, EU) removed due to unreliable FRED data sources
    # Only US M2 (M2SL, M2REAL) is maintained for reliable data
    
    # =========================================================================
    # US ECONOMIC INDICATORS (Page 03)
    # =========================================================================
    'CPI': {
        'source': 'FRED',
        'id': 'CPIAUCSL',
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'inflation',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '消費者物価指数',
        'validation': (200, 400),
    },
    'CPICore': {
        'source': 'FRED',
        'id': 'CPILFESL',
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'inflation',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'コアCPI',
        'validation': (200, 400),
    },
    'PPI': {
        'source': 'FRED',
        'id': 'PPIACO',
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'inflation',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '生産者物価指数',
        'validation': (100, 350),
    },
    'CorePCE': {
        'source': 'FRED',
        'id': 'PCETRIM12M159SFRBDAL',
        'unit': '%',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'inflation',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'コアPCE（Fedの最重視指標）',
        'validation': (-5, 15),
    },
    # NOTE: 'Unemployment' removed - duplicate of UNRATE below
    'UNRATE': {
        'source': 'FRED',
        'id': 'UNRATE',
        'unit': '%',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'employment',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '失業率（別名）',
        'validation': (0, 25),
    },
    'NFP': {
        'source': 'FRED',
        'id': 'PAYEMS',
        'unit': 'K',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'employment',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '非農業部門雇用者数',
        'validation': (100000, 200000),
    },
    'ADP': {
        'source': 'FRED',
        'id': 'ADPWNUSNERSA',
        'unit': 'K',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'employment',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'ADP雇用統計',
        'validation': (100000, 200000),
        'divisor': 1000,  # Persons → Thousands
    },
    'AvgHourlyEarnings': {
        'source': 'FRED',
        'id': 'CES0500000003',
        'unit': '$/hr',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'employment',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '平均時給',
        'validation': (20, 60),
    },
    'JOLTS': {
        'source': 'FRED',
        'id': 'JTSJOL',
        'unit': 'K',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'employment',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'JOLTS求人数',
        'validation': (3000, 15000),
    },
    'ICSA': {
        'source': 'FRED',
        'id': 'ICSA',
        'unit': 'K',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'employment',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '新規失業保険申請件数',
        'validation': (100, 1000),
        'divisor': 1000,  # Persons → Thousands
    },
    'RetailSales': {
        'source': 'FRED',
        'id': 'RSAFS',
        'unit': 'B',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'consumption',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '小売売上高',
    },
    'ConsumerSent': {
        'source': 'FRED',
        'id': 'UMCSENT',
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'sentiment',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'ミシガン消費者信頼感',
    },
    'Michigan_Inflation_Exp': {
        'source': 'FRED',
        'id': 'MICH',
        'unit': '%',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'inflation',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'ミシガン大1年先期待インフレ率（消費者の予想）',
        'validation': (0, 15),
    },
    'RealGDP': {
        'source': 'FRED',
        'id': 'GDPC1',
        'unit': 'B',
        'frequency': 'quarterly',
        'freshness': 'quarterly',
        'category': 'gdp',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '実質GDP',
    },
    
    # === Regional Fed Manufacturing Indices (2026-01-23 追加) ===
    # These are ISM PMI alternatives - Free regional Fed surveys from FRED
    'Empire_State_Mfg': {
        'source': 'FRED',
        'id': 'GACDISA066MSFRBNY',  # NY Fed Empire State Manufacturing Survey: General Business Conditions
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'manufacturing',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'NY連銀製造業景況指数（0超=拡大）',
        'validation': (-80, 80),
    },
    'Philly_Fed_Mfg': {
        'source': 'FRED',
        'id': 'GACDFSA066MSFRBPHI',  # Philly Fed Manufacturing Survey: General Business Conditions
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'manufacturing',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'フィラデルフィア連銀製造業景況指数（0超=拡大）',
        'validation': (-80, 80),
    },
    'Dallas_Fed_Mfg': {
        'source': 'FRED',
        'id': 'BACTSAMFRBDAL',  # Dallas Fed Manufacturing Survey: Business Activity
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'manufacturing',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'ダラス連銀製造業指数（0超=拡大）',
        'validation': (-80, 80),
    },
    'Richmond_Fed_Mfg': {
        'source': 'WEB',  # Not on FRED - scrape from Richmond Fed website
        'id': 'https://www.richmondfed.org/region_communities/regional_data_analysis/surveys/manufacturing',
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'manufacturing',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'リッチモンド連銀製造業景況指数（0超=拡大）- Webスクレイピング',
        'validation': (-80, 80),
    },
    
    # === Leading & Housing Indicators (2026-01-22 追加) ===
    # NOTE: ISM_PMI removed - FRED discontinued NAPM series in 2016
    'Housing_Starts': {
        'source': 'FRED',
        'id': 'HOUST',
        'unit': 'K',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'housing',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '住宅着工件数（年率換算・千戸）',
    },
    'Building_Permits': {
        'source': 'FRED',
        'id': 'PERMIT',
        'unit': 'K',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'housing',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '建築許可件数（年率換算・千戸）',
    },
    'Leading_Index': {
        'source': 'FRED',
        'id': 'CFNAIMA3',  # Updated 2026-01-22: USSLIND discontinued in 2020, replaced with Chicago Fed CFNAI
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'economy',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'シカゴ連銀景気指数（3ヶ月移動平均）経済活動の先行指標、0超=拡大/0未満=減速',
        'validation': (-4, 4),
    },
    
    # =========================================================================
    # BANKING SECTOR (Page 09) - SLOOS & H.8
    # =========================================================================
    'Bank_Cash': {
        'source': 'FRED',
        'id': 'CASACBW027SBOG',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'banking_h8',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': '銀行の現金保有',
        'divisor': 1000,
    },
    'CI_Loans': {
        'source': 'FRED',
        'id': 'BUSLOANS',
        'unit': 'B',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'banking_loans',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': 'C&I融資残高',
        'divisor': 1000,
    },
    'CRE_Loans': {
        'source': 'FRED',
        'id': 'CREACBW027SBOG',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'banking_loans',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': 'CRE融資残高',
        'divisor': 1000,
    },
    # NOTE: 'Lending_Standards' removed - duplicate of CI_Std_Large below
    'CI_Std_Large': {
        'source': 'FRED',
        'id': 'DRTSCILM',
        'unit': 'pts',
        'frequency': 'quarterly',
        'freshness': 'quarterly',
        'category': 'banking_sloos',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': 'C&I基準（大企業）',
    },
    'CI_Std_Small': {
        'source': 'FRED',
        'id': 'DRTSCIS',
        'unit': 'pts',
        'frequency': 'quarterly',
        'freshness': 'quarterly',
        'category': 'banking_sloos',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': 'C&I基準（小企業）',
    },
    'CI_Demand': {
        'source': 'FRED',
        'id': 'DRSDCILM',  # Demand for C&I Loans (Large/Mid Firms)
        'unit': 'pts',
        'frequency': 'quarterly',
        'freshness': 'quarterly',
        'category': 'banking_sloos',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': 'C&I融資需要',
    },
    'CRE_Std_Construction': {
        'source': 'FRED',
        'id': 'SUBLPDRCSC',
        'unit': 'pts',
        'frequency': 'quarterly',
        'freshness': 'quarterly',
        'category': 'banking_sloos',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': 'CRE基準（建設）',
    },
    'CRE_Std_Office': {
        'source': 'FRED',
        'id': 'SUBLPDRCSN',  # Nonfarm Nonresidential (Office/Retail)
        'unit': 'pts',
        'frequency': 'quarterly',
        'freshness': 'quarterly',
        'category': 'banking_sloos',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': 'CRE基準（オフィス）',
    },
    'CRE_Std_Multifamily': {
        'source': 'FRED',
        'id': 'SUBLPDRCSM',  # Multifamily (集合住宅)
        'unit': 'pts',
        'frequency': 'quarterly',
        'freshness': 'quarterly',
        'category': 'banking_sloos',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': 'CRE基準（集合住宅）',
    },
    'CRE_Demand': {
        'source': 'FRED',
        'id': 'SUBLPDRCDN',  # Demand for CRE Loans (Nonfarm Nonresidential)
        'unit': 'pts',
        'frequency': 'quarterly',
        'freshness': 'quarterly',
        'category': 'banking_sloos',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': 'CRE融資需要',
    },
    
    # === H.8 Additional (2026-01-15) ===
    'Credit_Card_Loans': {
        'source': 'FRED',
        'id': 'CCLACBW027SBOG',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'banking_h8',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': 'クレカ残高',
    },
    'Consumer_Loans': {
        'source': 'FRED',
        'id': 'CLSACBW027NBOG',
        'unit': 'B',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'banking_h8',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': '消費者ローン残高',
    },
    'Bank_Securities': {
        'source': 'FRED',
        'id': 'TASACBW027SBOG',  # Updated 2026-01-21: Old H8B1002NCBCAG was annual, this is weekly
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'banking_h8',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': '銀行保有有価証券（国債＋政府機関債）',
    },
    'Bank_Deposits': {
        'source': 'FRED',
        'id': 'DPSACBW027SBOG',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'banking_h8',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '銀行セクター',
        'notes': '銀行預金総額',
    },
    
    # === Financial Stress (2026-01-16 Gemini推奨) ===
    'Small_Bank_Deposits': {
        'source': 'FRED',
        'id': 'DPSSCBW027SBOG',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'financial_stress',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '金融ストレス',
        'notes': '地銀預金（取り付け警報）',
    },
    'CC_Delinquency': {
        'source': 'FRED',
        'id': 'DRCCLACBS',
        'unit': '%',
        'frequency': 'quarterly',
        'freshness': 'quarterly',
        'category': 'financial_stress',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '金融ストレス',
        'notes': 'クレカ延滞率',
    },
    'CP_Spread': {
        'source': 'FRED',
        'id': 'CPFF',
        'unit': '%',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'financial_stress',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '金融ストレス',
        'notes': 'CP-FFスプレッド（企業資金ストレス）',
    },
    'NFCI': {
        'source': 'FRED',
        'id': 'NFCI',
        'unit': '',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'financial_stress',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '金融ストレス',
        'notes': 'シカゴ連銀金融環境指数',
    },
    'Breakeven_10Y': {
        'source': 'FRED',
        'id': 'T10YIE',
        'unit': '%',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'inflation_expectations',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '金融ストレス',
        'notes': '10年期待インフレ率',
    },
    
    # =========================================================================
    # MARKET INDICATORS (Yahoo Finance)
    # =========================================================================
    'SP500': {
        'source': 'YAHOO',
        'id': '^GSPC',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'equity',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'S&P 500',
        'validation': (2000, 8000),
    },
    'VIX': {
        'source': 'YAHOO',
        'id': '^VIX',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'volatility',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'VIX恐怖指数',
        'validation': (5, 100),
    },
    'MOVE': {
        'source': 'YAHOO',
        'id': '^MOVE',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'volatility',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '金融ストレス',
        'notes': 'MOVE債券恐怖指数',
    },
    'HYG': {
        'source': 'YAHOO',
        'id': 'HYG',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'credit',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '社債',
        'notes': 'ハイイールド債ETF（投機的社債）',
    },
    'LQD': {
        'source': 'YAHOO',
        'id': 'LQD',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'credit',
        'ui_page': '11_analysis_lab',
        'ai_include': True,
        'ai_section': '社債',
        'notes': '投資適格社債ETF（IG社債）',
    },
    'NIKKEI': {
        'source': 'YAHOO',
        'id': '^N225',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'equity',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': '日経225',
    },
    
    # === FX ===
    'DXY': {
        'source': 'YAHOO',
        'id': 'DX-Y.NYB',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ドルインデックス',
        'validation': (70, 130),
    },
    'USDJPY': {
        'source': 'YAHOO',
        'id': 'JPY=X',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ドル円',
        'validation': (80, 200),
    },
    'EURUSD': {
        'source': 'YAHOO',
        'id': 'EURUSD=X',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ユーロドル',
    },
    'USDCNY': {
        'source': 'YAHOO',
        'id': 'CNY=X',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ドル人民元',
    },
    'GBPUSD': {
        'source': 'YAHOO',
        'id': 'GBPUSD=X',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ポンドドル (Fiat Health Monitor)',
    },
    'USDCHF': {
        'source': 'YAHOO',
        'id': 'CHF=X',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ドルスイスフラン (Fiat Health Monitor)',
    },
    'AUDUSD': {
        'source': 'YAHOO',
        'id': 'AUDUSD=X',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': '豪ドル (Fiat Health Monitor)',
    },
    
    # === Commodities ===
    'Gold': {
        'source': 'YAHOO',
        'id': 'GC=F',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'commodities',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': '金先物',
        'validation': (1000, 4000),
    },
    'Silver': {
        'source': 'YAHOO',
        'id': 'SI=F',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'commodities',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': '銀先物',
    },
    'Oil': {
        'source': 'YAHOO',
        'id': 'CL=F',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'commodities',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'WTI原油先物',
    },
    'Copper': {
        'source': 'YAHOO',
        'id': 'HG=F',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'commodities',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': '銅先物（景気先行指標）',
    },
    
    # === Crypto ===
    'BTC': {
        'source': 'YAHOO',
        'id': 'BTC-USD',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'crypto',
        'ui_page': '04_crypto',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'ビットコイン',
        'validation': (10000, 500000),
    },
    'ETH': {
        'source': 'YAHOO',
        'id': 'ETH-USD',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'crypto',
        'ui_page': '04_crypto',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'イーサリアム',
    },
    
    # =========================================================================
    # NEW ADVANCED INDICATORS (2026-01-16)
    # =========================================================================
    'M2_Velocity': {
        'source': 'FRED',
        'id': 'M2V',
        'unit': '',
        'frequency': 'quarterly',
        'freshness': 'quarterly',
        'category': 'economy',
        'ui_page': '10_market_lab',  # New Lab Page
        'ai_include': True,
        'ai_section': 'マクロ分析',
        'notes': 'M2通貨回転率（インフレ・景気過熱）',
    },
    'Financial_Stress': {
        'source': 'FRED',
        'id': 'STLFSI4',
        'unit': '',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'financial_stress',
        'ui_page': '10_market_lab',
        'ai_include': True,
        'ai_section': '金融ストレス',
        'notes': 'セントルイス連銀金融ストレス指数',
    },
    'ECB_Assets': {
        'source': 'FRED',
        'id': 'ECBASSETSW',
        'unit': 'M',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'central_bank',
        'ui_page': '02_global_money', # Or hidden mainly for calc
        'ai_include': True,
        'ai_section': '中央銀行',
        'notes': 'ECB総資産 (Million EUR)',
        'divisor': 1000000, # Initial unit is Million? FRED says "Millions of Euros". Convert to Trillions? Or Billions?
        # Usually we want Billions for consistency with Fed Assets. 1,000,000 Million = 1 Trillion.
        # Fed Assets is in Billions.
        # Let's keep it Raw and normalize in data_fetcher if needed, or set divisor here.
        # FRED: ECBASSETSW is "Millions of Euros".
        # To get Billions of Euros: Divide by 1,000.
        # To get Trillions: Divide by 1,000,000.
        # Current Fed Assets is Billions. Let's aim for Billions.
        'divisor': 1000, 
    },
    'Global_Liquidity_Proxy': {
        'source': 'CALCULATED',
        'id': 'GLP_USD',
        'unit': 'B USD',
        'frequency': 'weekly', # Driven by Fed/ECB weekly
        'freshness': 'weekly',
        'category': 'liquidity',
        'ui_page': '10_market_lab',
        'ai_include': True,
        'ai_section': '流動性',
        'notes': 'グローバル流動性プロキシ (Fed+ECB-TGA-RRP)',
    },
}


# =============================================================================
# AUTO-GENERATED HELPER FUNCTIONS
# These maintain backward compatibility with existing code
# =============================================================================

def get_fred_indicators():
    """Return dict of FRED indicators {name: series_id}"""
    return {k: v['id'] for k, v in INDICATORS.items() if v['source'] == 'FRED'}

def get_yahoo_indicators():
    """Return dict of Yahoo indicators {name: ticker}"""
    return {k: v['id'] for k, v in INDICATORS.items() if v['source'] == 'YAHOO'}

def get_data_frequency():
    """Return dict of indicator frequencies {name: frequency_key}
    
    Returns English frequency keys (daily, weekly, etc.)
    Translation should be done at display time using t(f'freq_{key}')
    """
    return {k: v['frequency'] for k, v in INDICATORS.items()}

def get_freshness_rules():
    """Return dict of freshness rules for DATA_FRESHNESS_RULES format"""
    rules = {
        'daily': {'fresh': 3, 'stale': 7, 'critical': 14, 'indicators': []},
        'weekly': {'fresh': 10, 'stale': 14, 'critical': 21, 'indicators': []},
        'monthly': {'fresh': 45, 'stale': 60, 'critical': 90, 'indicators': []},
        'quarterly': {'fresh': 100, 'stale': 120, 'critical': 150, 'indicators': []},
    }
    for k, v in INDICATORS.items():
        freshness = v.get('freshness', v['frequency'])
        if freshness in rules:
            rules[freshness]['indicators'].append(k)
    return rules

def get_validation_ranges():
    """Return dict of validation ranges {name: (min, max)}"""
    return {k: v['validation'] for k, v in INDICATORS.items() if 'validation' in v}

def get_fred_units():
    """Return dict of FRED units {name: {unit, convert_to, divisor}}"""
    units = {}
    for k, v in INDICATORS.items():
        if v['source'] == 'FRED' and 'divisor' in v:
            units[k] = {
                'unit': 'Original',
                'convert_to': v.get('unit', ''),
                'divisor': v['divisor']
            }
    return units

def get_indicators_for_page(page_name):
    """Return indicators for a specific UI page"""
    return {k: v for k, v in INDICATORS.items() if v.get('ui_page') == page_name}

def get_indicators_for_ai():
    """Return indicators to include in AI summary"""
    return {k: v for k, v in INDICATORS.items() if v.get('ai_include')}

def get_indicators_by_category(category):
    """Return indicators for a specific category"""
    return {k: v for k, v in INDICATORS.items() if v.get('category') == category}

def get_indicator_info(name):
    """Get full info for a single indicator"""
    return INDICATORS.get(name)

def get_all_indicator_names():
    """Get list of all indicator names"""
    return list(INDICATORS.keys())


# =============================================================================
# BACKWARD COMPATIBILITY EXPORTS
# =============================================================================
FRED_INDICATORS = get_fred_indicators()
YAHOO_INDICATORS = get_yahoo_indicators()
DATA_FREQUENCY = get_data_frequency()
DATA_FRESHNESS_RULES = get_freshness_rules()
VALIDATION_RANGES = get_validation_ranges()
FRED_UNITS = get_fred_units()


if __name__ == '__main__':
    # Quick self-test
    print(f"Total indicators: {len(INDICATORS)}")
    print(f"FRED indicators: {len(FRED_INDICATORS)}")
    print(f"Yahoo indicators: {len(YAHOO_INDICATORS)}")
    print(f"\nFreshness rules:")
    for period, rules in DATA_FRESHNESS_RULES.items():
        print(f"  {period}: {len(rules['indicators'])} indicators")
