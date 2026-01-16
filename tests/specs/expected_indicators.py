# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Master Specification
===========================================
このファイルは「意図した変更」と「意図しない変更」を区別するための
マスター定義です。変更履歴を必ず記録してください。

変更履歴:
---------
2026-01-15: 初版作成 - 67指標定義
2026-01-15: v1.1 - REQUIRED_DATAFRAME_COLUMNSをconstants.pyと整合
"""

# ========== 不変の定義（絶対に変わらない）==========

# Net Liquidityの計算式（これは変更禁止）
NET_LIQUIDITY_FORMULA = "Fed_Assets - TGA - ON_RRP - SRF - FIMA"

# Bills Ratioの計算式
BILLS_RATIO_FORMULA = "(SOMA_Bills / SOMA_Total) * 100"


# ========== 可変の定義（変更時はコメント必須）==========

# 期待される指標数
# 変更時は日付と理由をコメントで記載すること
EXPECTED_INDICATOR_COUNT = 67  # 2026-01-15: 初版

# ページファイル（存在確認用）
EXPECTED_PAGE_FILES = [
    "01_liquidity.py",
    "02_global_money.py",
    "03_us_economic.py",
    "04_crypto.py",
    "05_ai_analysis.py",
    "06_monte_carlo.py",
    "07_market_voices.py",
    "08_sentiment.py",
]

# utilsモジュール（インポート確認用）
EXPECTED_UTILS_MODULES = [
    ("utils.constants", ["FRED_INDICATORS", "YAHOO_INDICATORS", "DATA_FRESHNESS_RULES"]),
    ("utils.config", ["EXPLANATIONS", "MANUAL_GLOBAL_M2"]),
    ("utils.data", ["get_market_data"]),
    ("utils.charts", ["show_metric"]),
]

# FRED指標キー（constants.pyのFRED_INDICATORSに存在すべきキー）
EXPECTED_FRED_KEYS = [
    # Plumbing
    "ON_RRP", "Reserves", "TGA", "Fed_Assets", "SOMA_Total", "SOMA_Bills",
    "EFFR", "IORB", "SRF", "FIMA", "SOFR",
    # Banking
    "Bank_Cash", "Lending_Standards", "Primary_Credit", "Total_Loans",
    # SLOOS - C&I
    "CI_Std_Large", "CI_Std_Small", "CI_Demand", "CI_Loans",
    # SLOOS - CRE
    "CRE_Std_Construction", "CRE_Std_Office", "CRE_Std_Multifamily", "CRE_Demand", "CRE_Loans",
    # Rates & Bonds
    "Credit_Spread", "US_TNX", "T10Y2Y",
    # Macro
    "Unemployment", "UNRATE", "CPI", "CPICore", "PPI", "CorePCE",
    "M2SL", "M2REAL",
    # Employment
    "NFP", "ADP", "AvgHourlyEarnings", "JOLTS", "ICSA",
    # Fed Policy
    "FedFundsUpper", "FedFundsLower",
    # Global M2
    "CN_M2", "JP_M2", "EU_M2",
    # Global CPI
    "CN_CPI", "JP_CPI", "EU_CPI",
    # Economy
    "RetailSales", "RealGDP", "ConsumerSent",
]

# Yahoo指標キー
EXPECTED_YAHOO_KEYS = [
    "SP500", "VIX", "HYG",
    "DXY", "USDJPY", "EURUSD", "USDCNY",
    "Gold", "Silver", "Oil", "Copper",
    "BTC", "ETH",
]

# ページごとの期待される指標
EXPECTED_INDICATORS_BY_PAGE = {
    "01_liquidity": {
        "name": "Liquidity & Rates",
        "metrics": [
            # バリュエーション & レバレッジ
            "S&P 500 P/E", "NASDAQ P/E (QQQ)", "BTC Funding Rate", "BTC L/S Ratio",
            "BTC Open Interest", "ETH Open Interest",
            # Net Liquidity
            "Net Liquidity",
            # Plumbing
            "ON RRP", "TGA", "Reserves", "SRF", "FIMA", "SOFR", "EFFR - IORB",
            # SOMA
            "SOMA Total", "SOMA Bills", "Bills Ratio",
            # Emergency Loans
            "Total Loans", "Primary Credit",
            # Banking
            "Bank Cash", "C&I Lending Tightening",
            # SLOOS C&I
            "CI_Std_Large", "CI_Std_Small", "CI_Demand", "CI_Loans",
            # SLOOS CRE
            "CRE_Std_Construction", "CRE_Std_Office", "CRE_Std_Multifamily", "CRE_Demand", "CRE_Loans",
            # Risk
            "VIX", "Credit Spread", "US 10Y Yield"
        ],
        "charts": [
            "Net Liquidity vs S&P 500",
            "SOMA Composition"
        ]
    },
    "02_global_money": {
        "name": "Global Money & FX",
        "metrics": [
            # Global M2
            "US M2", "China M2", "Japan M2", "Eurozone M2",
            # FX
            "DXY", "USD/JPY", "EUR/USD", "USD/CNY",
            # Commodities
            "Gold", "Silver", "Oil", "Copper",
            # Crypto
            "BTC", "ETH"
        ],
        "charts": []
    },
    "03_us_economic": {
        "name": "US Economic Data",
        "metrics": [
            # Employment
            "NFP", "ADP", "Unemployment", "Avg Hourly Earnings", "JOLTS", "ICSA",
            # Inflation
            "CPI", "Core CPI", "PPI", "Core PCE",
            # Consumer
            "Retail Sales", "Consumer Sentiment",
            # GDP
            "Real GDP",
            # Yield Curve
            "10Y-2Y Spread"
        ],
        "charts": [
            "Yield Curve"
        ]
    },
    "04_crypto": {
        "name": "Crypto Liquidity",
        "metrics": [
            # Stablecoin
            "USDT", "USDC", "DAI",
            # BTC Reserves
            "Treasury Holdings", "Gold Holdings"
        ],
        "charts": [
            "Stablecoin Supply"
        ]
    },
    "08_sentiment": {
        "name": "Market Sentiment",
        "metrics": [
            # Fear & Greed
            "CNN Fear & Greed", "Crypto Fear & Greed", "VIX",
            # AAII
            "AAII Bullish", "AAII Neutral", "AAII Bearish", "Bull-Bear Spread"
        ],
        "charts": []
    }
}

# データフレーム必須列（オフラインテスト用 - Net Liquidity計算に必要な列）
REQUIRED_DATAFRAME_COLUMNS = [
    # Net Liquidity計算に必須
    "Net_Liquidity", "Fed_Assets", "TGA", "ON_RRP", "SRF", "FIMA",
    # Plumbing
    "Reserves", "EFFR", "IORB", "SOFR",
    # SOMA
    "SOMA_Total", "SOMA_Bills", "SomaBillsRatio",
    # Markets (Yahoo)
    "SP500", "VIX", "BTC", "ETH",
    # Credit
    "Credit_Spread", "US_TNX",
]

# 計算式の検証ルール
CALCULATION_RULES = {
    "Net_Liquidity": {
        "formula": "Fed_Assets - TGA - ON_RRP - SRF - FIMA",
        "components": ["Fed_Assets", "TGA", "ON_RRP", "SRF", "FIMA"],
        "tolerance": 1.0  # 誤差許容範囲（Billions）
    },
    "SomaBillsRatio": {
        "formula": "(SOMA_Bills / SOMA_Total) * 100",
        "components": ["SOMA_Bills", "SOMA_Total"],
        "tolerance": 0.1  # 誤差許容範囲（%）
    }
}

# 最小指標数（各カテゴリ）
MIN_INDICATOR_COUNTS = {
    "FRED": 40,
    "Yahoo": 10,
    "Total_Monitored": 60,
}
