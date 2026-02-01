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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'notes': '米実質M2（1982-84年基準ドル、Billions）',
        'divisor': 1000,  # Billions → Trillions
        'display_pattern': 'standard',
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
        'display_pattern': 'mom_yoy',
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
        'display_pattern': 'mom_yoy',
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
        'display_pattern': 'mom_yoy',
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
        'display_pattern': 'mom_yoy',
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
        'display_pattern': 'manual_calc',
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
        'display_pattern': 'manual_calc',
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
        'display_pattern': 'manual_calc',
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
        'display_pattern': 'manual_calc',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'manual_calc',
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
        'display_pattern': 'mom_yoy',
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
        'display_pattern': 'mom_yoy',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'manual_calc',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
    },
    'Richmond_Fed_Mfg': {
        'source': 'WEB',  # Not on FRED - scrape from Richmond Fed website
        'id': 'https://www.richmondfed.org/region_communities/regional_data_analysis/business_surveys/manufacturing',
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'manufacturing',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'リッチモンド連銀製造業景況指数（0超=拡大）- Webスクレイピング',
        'validation': (-80, 80),
        'display_pattern': 'web_scrape',
    },
    
    # === Manufacturing Hard Data (2026-02-01 追加) ===
    # Direct output & orders measurement (vs survey-based indices above)
    'INDPRO': {
        'source': 'FRED',
        'id': 'INDPRO',
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'manufacturing',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '工業生産指数（2017=100、製造業実績の直接測定）',
        'validation': (80, 140),
        'display_pattern': 'standard',
    },
    'NEWORDER': {
        'source': 'FRED',
        'id': 'NEWORDER',
        'unit': 'B',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'manufacturing',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': '製造業新規受注（設備投資の先行指標、年率換算）',
        'divisor': 1000,  # Millions → Billions
        'display_pattern': 'standard',
    },

    # === Regional Fed Services/Nonmanufacturing Indices (2026-01-23 追加) ===
    # Non-manufacturing sector surveys from regional Federal Reserve Banks
    'Philly_Fed_Services': {
        'source': 'FRED',
        'id': 'GABNDIF066MSFRBPHI',  # Philly Fed Nonmanufacturing: General Activity (Firm Perceptions)
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'services',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'フィラデルフィア連銀非製造業景況指数（0超=拡大）季節調整済',
        'validation': (-80, 80),
        'display_pattern': 'standard',
    },
    'Dallas_Fed_Services': {
        'source': 'FRED',
        'id': 'TSSOSBACTSAMFRBDAL',  # Texas Service Sector Outlook Survey: General Business Activity
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'services',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'ダラス連銀サービス業指数（0超=拡大）季節調整済',
        'validation': (-80, 80),
        'display_pattern': 'standard',
    },
    'NY_Fed_Services': {
        'source': 'FRED',
        'id': 'BACDINA066MNFRBNY',  # NY Fed Business Leaders Survey: Current Business Activity
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'services',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'NY連銀サービス業景況指数（0超=拡大）※季節調整なし(NSA)',
        'validation': (-80, 80),
        'display_pattern': 'standard',
    },
    'Richmond_Fed_Services': {
        'source': 'WEB',  # Not on FRED - scrape from Richmond Fed website
        'id': 'https://www.richmondfed.org/region_communities/regional_data_analysis/business_surveys/non-manufacturing',
        'unit': 'idx',
        'frequency': 'monthly',
        'freshness': 'monthly',
        'category': 'services',
        'ui_page': '03_us_economic',
        'ai_include': True,
        'ai_section': '米経済指標',
        'notes': 'リッチモンド連銀サービス業景況指数（0超=拡大）- Webスクレイピング',
        'validation': (-80, 80),
        'display_pattern': 'web_scrape',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        # divisor削除: FREDはBillionsで返すため変換不要
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
    },
    'NFCI': {
        'source': 'FRED',
        'id': 'NFCI',
        'unit': 'idx',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'financial_stress',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '金融ストレス',
        'notes': 'シカゴ連銀金融環境指数',
        'display_pattern': 'standard',
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
        'display_pattern': 'standard',
    },
    
    # =========================================================================
    # MARKET INDICATORS (Yahoo Finance)
    # =========================================================================
    'SP500': {
        'source': 'YAHOO',
        'id': '^GSPC',
        'unit': 'pts',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'equity',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'S&P 500',
        'validation': (2000, 8000),
        'display_pattern': 'standard',
    },
    'VIX': {
        'source': 'YAHOO',
        'id': '^VIX',
        'unit': 'pts',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'volatility',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'VIX恐怖指数',
        'validation': (5, 100),
        'display_pattern': 'standard',
    },
    'MOVE': {
        'source': 'YAHOO',
        'id': '^MOVE',
        'unit': 'pts',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'volatility',
        'ui_page': '09_banking',
        'ai_include': True,
        'ai_section': '金融ストレス',
        'notes': 'MOVE債券恐怖指数',
        'display_pattern': 'standard',
    },
    'HYG': {
        'source': 'YAHOO',
        'id': 'HYG',
        'unit': '$',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'credit',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '社債',
        'notes': 'ハイイールド債ETF（投機的社債）',
        'display_pattern': 'standard',
    },
    'LQD': {
        'source': 'YAHOO',
        'id': 'LQD',
        'unit': '$',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'credit',
        'ui_page': '01_liquidity',  # Changed from 11_analysis_lab to match actual display location
        'ai_include': True,
        'ai_section': '社債',
        'notes': '投資適格社債ETF（IG社債）',
        'display_pattern': 'standard',
    },
    'NIKKEI': {
        'source': 'YAHOO',
        'id': '^N225',
        'unit': 'pts',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'equity',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': '日経225',
        'display_pattern': 'standard',
    },
    
    # === FX ===
    'DXY': {
        'source': 'YAHOO',
        'id': 'DX-Y.NYB',
        'unit': 'pts',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ドルインデックス',
        'validation': (70, 130),
        'display_pattern': 'standard',
    },
    'USDJPY': {
        'source': 'YAHOO',
        'id': 'JPY=X',
        'unit': '¥',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ドル円',
        'validation': (80, 200),
        'display_pattern': 'standard',
    },
    'EURUSD': {
        'source': 'YAHOO',
        'id': 'EURUSD=X',
        'unit': '$',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ユーロドル',
        'display_pattern': 'standard',
    },
    'USDCNY': {
        'source': 'YAHOO',
        'id': 'CNY=X',
        'unit': '¥',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ドル人民元',
        'display_pattern': 'standard',
    },
    'GBPUSD': {
        'source': 'YAHOO',
        'id': 'GBPUSD=X',
        'unit': '$',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ポンドドル (Fiat Health Monitor)',
        'display_pattern': 'standard',
    },
    'USDCHF': {
        'source': 'YAHOO',
        'id': 'CHF=X',
        'unit': 'Fr',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'ドルスイスフラン (Fiat Health Monitor)',
        'display_pattern': 'standard',
    },
    'AUDUSD': {
        'source': 'YAHOO',
        'id': 'AUDUSD=X',
        'unit': '$',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'fx',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': '豪ドル (Fiat Health Monitor)',
        'display_pattern': 'standard',
    },
    
    # === Commodities ===
    'Gold': {
        'source': 'YAHOO',
        'id': 'GC=F',
        'unit': '$',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'commodities',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': '金先物',
        'validation': (1000, 4000),
        'display_pattern': 'standard',
    },
    'Silver': {
        'source': 'YAHOO',
        'id': 'SI=F',
        'unit': '$',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'commodities',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': '銀先物',
        'display_pattern': 'standard',
    },
    'Oil': {
        'source': 'YAHOO',
        'id': 'CL=F',
        'unit': '$',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'commodities',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': 'WTI原油先物',
        'display_pattern': 'standard',
    },
    'Copper': {
        'source': 'YAHOO',
        'id': 'HG=F',
        'unit': '$',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'commodities',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '株式・為替・商品',
        'notes': '銅先物（景気先行指標）',
        'display_pattern': 'standard',
    },
    
    # === Crypto ===
    'BTC': {
        'source': 'YAHOO',
        'id': 'BTC-USD',
        'unit': '$',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'crypto',
        'ui_page': '04_crypto',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'ビットコイン',
        'validation': (10000, 500000),
        'display_pattern': 'standard',
    },
    'ETH': {
        'source': 'YAHOO',
        'id': 'ETH-USD',
        'unit': '$',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'crypto',
        'ui_page': '04_crypto',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'イーサリアム',
        'display_pattern': 'standard',
    },
    
    # =========================================================================
    # NEW ADVANCED INDICATORS (2026-01-16)
    # =========================================================================
    'M2_Velocity': {
        'source': 'FRED',
        'id': 'M2V',
        'unit': 'ratio',
        'frequency': 'quarterly',
        'freshness': 'quarterly',
        'category': 'economy',
        'ui_page': '10_market_lab',  # New Lab Page
        'ai_include': True,
        'ai_section': 'マクロ分析',
        'notes': 'M2通貨回転率（インフレ・景気過熱）',
        'display_pattern': 'standard',
    },
    'Financial_Stress': {
        'source': 'FRED',
        'id': 'STLFSI4',
        'unit': 'idx',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'financial_stress',
        'ui_page': '10_market_lab',
        'ai_include': True,
        'ai_section': '金融ストレス',
        'notes': 'セントルイス連銀金融ストレス指数',
        'display_pattern': 'standard',
    },
    'ECB_Assets': {
        'source': 'FRED',
        'id': 'ECBASSETSW',
        'unit': 'B EUR',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'central_bank',
        'ui_page': '02_global_money',
        'ai_include': True,
        'ai_section': '中央銀行',
        'notes': 'ECB総資産（10億ユーロ）',
        'divisor': 1000,  # Millions → Billions変換
        'display_pattern': 'standard',
    },
    'Net_Liquidity': {
        'source': 'CALCULATED',
        'id': 'NET_LIQ',
        'unit': 'B',
        'frequency': 'weekly',
        'freshness': 'weekly',
        'category': 'liquidity',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '流動性',
        'notes': 'ネット流動性 (Fed Assets - TGA - RRP)',
        'display_pattern': 'calculated',
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
        'display_pattern': 'calculated',
    },
    
    # =========================================================================
    # API-BASED INDICATORS (Not stored in main df)
    # These are fetched via separate API calls, not part of get_market_data()
    # =========================================================================
    
    # === Valuation Metrics (Page 01) ===
    'SP500_PE': {
        'source': 'EXTERNAL',
        'id': 'multpl.com/s-p-500-pe-ratio',
        'unit': 'x',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'valuation',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'バリュエーション',
        'notes': 'S&P 500 P/E比率',
        'df_stored': False,
        'fetch_function': 'get_pe_ratios',
        'fetch_key': 'sp500_pe',
        'api_check': True,
        'display_pattern': 'api',
    },
    'NASDAQ_PE': {
        'source': 'EXTERNAL',
        'id': 'yfinance/QQQ',
        'unit': 'x',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'valuation',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': 'バリュエーション',
        'notes': 'NASDAQ P/E比率（QQQ ETF）',
        'df_stored': False,
        'fetch_function': 'get_pe_ratios',
        'fetch_key': 'nasdaq_pe',
        'api_check': True,
        'display_pattern': 'api',
    },
    
    # === Crypto Leverage (Page 01/04) - Hyperliquid DEX ===
    'BTC_Funding_Rate': {
        'source': 'HYPERLIQUID',
        'id': 'BTC-PERP',
        'unit': '%',
        'frequency': 'realtime',
        'freshness': 'daily',
        'category': 'crypto_leverage',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'BTC Funding Rate（Hyperliquid DEX）',
        'df_stored': False,
        'fetch_function': 'get_crypto_leverage_data',
        'fetch_key': 'btc_funding_rate',
        'api_check': True,
        'display_pattern': 'api',
    },
    'BTC_Open_Interest': {
        'source': 'HYPERLIQUID',
        'id': 'BTC-PERP',
        'unit': 'BTC',
        'frequency': 'realtime',
        'freshness': 'daily',
        'category': 'crypto_leverage',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'BTC Open Interest（Hyperliquid DEX）',
        'df_stored': False,
        'fetch_function': 'get_crypto_leverage_data',
        'fetch_key': 'btc_open_interest',
        'api_check': True,
        'display_pattern': 'api',
    },
    'BTC_Long_Short_Ratio': {
        'source': 'EXTERNAL',
        'id': 'coingecko/derivatives',
        'unit': '',
        'frequency': 'realtime',
        'freshness': 'daily',
        'category': 'crypto_leverage',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'BTC Long/Short比率（CoinGecko）',
        'df_stored': False,
        'fetch_function': 'get_crypto_leverage_data',
        'fetch_key': 'btc_long_short_ratio',
        'api_check': True,
        'display_pattern': 'api',
    },
    'ETH_Funding_Rate': {
        'source': 'HYPERLIQUID',
        'id': 'ETH-PERP',
        'unit': '%',
        'frequency': 'realtime',
        'freshness': 'daily',
        'category': 'crypto_leverage',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'ETH Funding Rate（Hyperliquid DEX）',
        'df_stored': False,
        'fetch_function': 'get_crypto_leverage_data',
        'fetch_key': 'eth_funding_rate',
        'api_check': True,
        'display_pattern': 'api',
    },
    'ETH_Open_Interest': {
        'source': 'HYPERLIQUID',
        'id': 'ETH-PERP',
        'unit': 'ETH',
        'frequency': 'realtime',
        'freshness': 'daily',
        'category': 'crypto_leverage',
        'ui_page': '01_liquidity',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'ETH Open Interest（Hyperliquid DEX）',
        'df_stored': False,
        'fetch_function': 'get_crypto_leverage_data',
        'fetch_key': 'eth_open_interest',
        'api_check': True,
        'display_pattern': 'api',
    },
    
    # === DeFiLlama Data (Page 04) ===
    'Stablecoin_Total': {
        'source': 'DEFILLAMA',
        'id': 'stablecoins/all',
        'unit': 'B',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'crypto_stablecoin',
        'ui_page': '04_crypto',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'ステーブルコイン総発行量',
        'df_stored': False,
        'fetch_function': 'get_stablecoin_data',
        'fetch_key': 'total_supply',
        'api_check': True,
        'display_pattern': 'api',
    },
    'Treasury_TVL': {
        'source': 'DEFILLAMA',
        'id': 'protocols/rwa-treasury',
        'unit': 'B',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'crypto_rwa',
        'ui_page': '04_crypto',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'トークン化米国債TVL（RWA）',
        'df_stored': False,
        'fetch_function': 'get_tokenized_treasury_data',
        'fetch_key': 'treasury.total_tvl',
        'api_check': True,
        'display_pattern': 'api',
    },
    'Gold_TVL': {
        'source': 'DEFILLAMA',
        'id': 'protocols/rwa-gold',
        'unit': 'B',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'crypto_rwa',
        'ui_page': '04_crypto',
        'ai_include': True,
        'ai_section': '仮想通貨',
        'notes': 'トークン化金TVL（RWA）',
        'df_stored': False,
        'fetch_function': 'get_tokenized_treasury_data',
        'fetch_key': 'gold.total_tvl',
        'api_check': True,
        'display_pattern': 'api',
    },
    
    # === Sentiment Indicators (Page 08) ===
    'Crypto_Fear_Greed': {
        'source': 'SENTIMENT',
        'id': 'alternative.me/fng',
        'unit': '',
        'frequency': 'daily',
        'freshness': 'daily',
        'category': 'sentiment',
        'ui_page': '08_sentiment',
        'ai_include': True,
        'ai_section': 'センチメント',
        'notes': 'Crypto Fear & Greed Index',
        'df_stored': False,
        'fetch_function': 'get_crypto_fear_greed',
        'fetch_key': 'current',
        'api_check': True,
        'validation': (0, 100),
        'display_pattern': 'api',
    },
    # NOTE: CNN_Fear_Greed removed 2026-01-30 - API unreliable/blocked
    # 'CNN_Fear_Greed': {...}
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


def get_api_indicators():
    """Return indicators that are fetched via separate API calls (not stored in main df)
    
    These have 'df_stored': False and include:
    - EXTERNAL: multpl.com, yfinance PE, CoinGecko
    - HYPERLIQUID: Hyperliquid DEX
    - DEFILLAMA: DeFiLlama API
    - SENTIMENT: Fear & Greed indices
    """
    return {k: v for k, v in INDICATORS.items() if v.get('df_stored') == False}


def get_df_indicators():
    """Return indicators stored in main DataFrame (FRED, YAHOO, WEB, CALCULATED)
    
    These are fetched by get_market_data() and stored in the main df.
    Default is df_stored=True (not explicitly set).
    """
    return {k: v for k, v in INDICATORS.items() if v.get('df_stored', True) == True}


def get_indicators_for_health_check():
    """Return all indicators that should be health-checked
    
    Returns dict with two categories:
    - 'df_indicators': Checked via data freshness (last_valid_date)
    - 'api_indicators': Checked via API response validation
    """
    df_indicators = {k: v for k, v in INDICATORS.items() 
                     if v.get('df_stored', True) == True}
    api_indicators = {k: v for k, v in INDICATORS.items() 
                      if v.get('api_check') == True}
    return {
        'df_indicators': df_indicators,
        'api_indicators': api_indicators,
        'total_count': len(df_indicators) + len(api_indicators)
    }


def get_indicators_by_source(source: str):
    """Return indicators for a specific source type
    
    Valid sources: FRED, YAHOO, WEB, CALCULATED, EXTERNAL, HYPERLIQUID, DEFILLAMA, SENTIMENT
    """
    return {k: v for k, v in INDICATORS.items() if v.get('source') == source}


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
    
    # New source types
    print(f"\nBy source type:")
    for source in ['FRED', 'YAHOO', 'WEB', 'CALCULATED', 'EXTERNAL', 'HYPERLIQUID', 'DEFILLAMA', 'SENTIMENT']:
        count = len(get_indicators_by_source(source))
        if count > 0:
            print(f"  {source}: {count}")
    
    # Health check summary
    hc = get_indicators_for_health_check()
    print(f"\nHealth check coverage:")
    print(f"  DataFrame indicators: {len(hc['df_indicators'])}")
    print(f"  API indicators: {len(hc['api_indicators'])}")
    print(f"  Total: {hc['total_count']}")
    
    print(f"\nFreshness rules:")
    for period, rules in DATA_FRESHNESS_RULES.items():
        print(f"  {period}: {len(rules['indicators'])} indicators")
