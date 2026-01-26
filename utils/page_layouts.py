# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page Layout Definitions
================================================================================
ページレイアウト定義 - 完全自動化のための設定

各ページのセクション構成、表示順序、カラム数を定義。
indicators.pyのui_sectionと連携して自動レンダリングを実現。

Usage:
    from utils.page_layouts import PAGE_LAYOUTS, get_page_layout
    
    layout = get_page_layout('01_liquidity')
    for section in layout['sections']:
        render_section_auto(df, section)
================================================================================
"""

# =============================================================================
# PAGE LAYOUT DEFINITIONS
# =============================================================================

PAGE_LAYOUTS = {
    # =========================================================================
    # Page 01: Liquidity & Rates
    # =========================================================================
    '01_liquidity': {
        'title_key': 'liquidity_title',
        'sections': [
            {
                'id': 'valuation_leverage',
                'title_key': 'valuation_leverage',
                'description_key': 'valuation_leverage_desc',
                'type': 'api',  # Special: API indicators
                'indicators': ['SP500_PE', 'NASDAQ_PE', 'BTC_Funding_Rate', 'BTC_Long_Short_Ratio'],
                'cols': 4,
            },
            {
                'id': 'open_interest',
                'title_key': 'open_interest_title',
                'type': 'api',
                'indicators': ['BTC_Open_Interest', 'ETH_Open_Interest'],
                'cols': 2,
            },
            {
                'id': 'net_liquidity',
                'title_key': 'net_liquidity',
                'type': 'dual_chart',  # Special: Net Liquidity + S&P500 dual axis
                'indicators': ['Net_Liquidity'],
                'chart_pair': 'SP500',  # Right axis indicator
                'cols': 1,
            },
            {
                'id': 'core_liquidity',
                'title_key': 'core_liquidity',
                'type': 'standard',
                'indicators': ['ON_RRP', 'Reserves', 'TGA'],
                'cols': 2,
                'show_charts': True,
            },
            {
                'id': 'market_plumbing',
                'title_key': 'market_plumbing',
                'type': 'standard',
                'indicators': ['SRF', 'FIMA', 'SOFR'],
                'cols': 2,
                'show_charts': True,
            },
            {
                'id': 'effr_iorb',
                'title_key': 'effr_iorb_section',
                'type': 'spread',  # Special: Calculated spread
                'indicators': ['EFFR', 'IORB'],
                'spread_name': 'EFFR_IORB',
                'spread_multiplier': 100,  # Convert to bps
                'spread_unit': 'bps',
            },
            {
                'id': 'ff_target',
                'title_key': 'ff_target_section',
                'type': 'standard',
                'indicators': ['FedFundsUpper', 'FedFundsLower'],
                'cols': 2,
                'show_charts': True,
            },
            {
                'id': 'fed_balance_sheet',
                'title_key': 'fed_balance_sheet',
                'type': 'soma',  # Special: SOMA composition chart + RMP status
                'indicators': ['SOMA_Total', 'SOMA_Treasury', 'SOMA_Bills'],
                'cols': 3,
                'show_soma_chart': True,
                'show_rmp_status': True,
            },
            {
                'id': 'emergency_loans',
                'title_key': 'emergency_loans',
                'type': 'standard',
                'indicators': ['Total_Loans', 'Primary_Credit'],
                'cols': 2,
                'show_charts': True,
            },
            {
                'id': 'risk_bonds',
                'title_key': 'risk_bonds',
                'description_key': 'risk_bonds_desc',
                'type': 'standard',
                'indicators': ['VIX', 'Credit_Spread', 'US_TNX'],
                'cols': 3,
                'show_charts': True,
            },
            {
                'id': 'corp_bond_etf',
                'title_key': 'corp_bond_etf_section',
                'description_key': 'corp_bond_etf_desc',
                'type': 'standard',
                'indicators': ['HYG', 'LQD'],
                'cols': 2,
                'show_charts': True,
            },
        ],
    },
    
    # =========================================================================
    # Page 02: Global Money & FX
    # =========================================================================
    '02_global_money': {
        'title_key': 'global_money_title',
        'sections': [
            {
                'id': 'us_money_supply',
                'title_key': 'us_money_supply',
                'description_key': 'us_m2_desc',
                'type': 'standard',
                'indicators': ['M2SL', 'M2REAL'],
                'cols': 2,
                'show_charts': True,
            },
            {
                'id': 'fx_major',
                'title_key': 'fx_major',
                'type': 'standard',
                'indicators': ['DXY', 'USDJPY', 'EURUSD', 'USDCNY'],
                'cols': 4,
                'show_charts': True,
            },
            {
                'id': 'fx_other',
                'title_key': 'fx_other',
                'type': 'standard',
                'indicators': ['GBPUSD', 'USDCHF', 'AUDUSD'],
                'cols': 3,
                'show_charts': True,
            },
            {
                'id': 'commodities',
                'title_key': 'commodities',
                'type': 'standard',
                'indicators': ['Gold', 'Silver', 'Oil', 'Copper'],
                'cols': 4,
                'show_charts': True,
            },
            {
                'id': 'global_indices',
                'title_key': 'global_indices',
                'type': 'standard',
                'indicators': ['NIKKEI'],
                'cols': 2,
                'show_charts': True,
            },
        ],
    },
    
    # =========================================================================
    # Page 03: US Economic Data
    # =========================================================================
    '03_us_economic': {
        'title_key': 'us_economic_title',
        'sections': [
            {
                'id': 'inflation',
                'title_key': 'inflation_section',
                'type': 'mom_yoy',  # Special: MoM/YoY display
                'indicators': ['CPI', 'CPICore', 'PPI', 'CorePCE'],
                'cols': 2,
            },
            {
                'id': 'inflation_expectations',
                'title_key': 'inflation_expectations',
                'type': 'standard',
                'indicators': ['Michigan_Inflation_Exp'],
                'cols': 2,
                'show_charts': True,
            },
            {
                'id': 'employment',
                'title_key': 'employment_section',
                'type': 'employment',  # Special: Employment calculations
                'indicators': ['UNRATE', 'NFP', 'ADP', 'AvgHourlyEarnings', 'JOLTS', 'ICSA'],
                'cols': 3,
            },
            {
                'id': 'consumption',
                'title_key': 'consumption_section',
                'type': 'mom_yoy',
                'indicators': ['RetailSales', 'ConsumerSent'],
                'cols': 2,
            },
            {
                'id': 'gdp',
                'title_key': 'gdp_section',
                'type': 'standard',
                'indicators': ['RealGDP'],
                'cols': 2,
                'show_charts': True,
            },
            {
                'id': 'manufacturing',
                'title_key': 'manufacturing_section',
                'type': 'standard',
                'indicators': ['Empire_State_Mfg', 'Philly_Fed_Mfg', 'Dallas_Fed_Mfg', 'Richmond_Fed_Mfg'],
                'cols': 4,
                'show_charts': True,
            },
            {
                'id': 'services',
                'title_key': 'services_section',
                'type': 'standard',
                'indicators': ['Philly_Fed_Services', 'Dallas_Fed_Services', 'NY_Fed_Services', 'Richmond_Fed_Services'],
                'cols': 4,
                'show_charts': True,
            },
            {
                'id': 'housing',
                'title_key': 'housing_section',
                'type': 'standard',
                'indicators': ['Housing_Starts', 'Building_Permits'],
                'cols': 2,
                'show_charts': True,
            },
            {
                'id': 'leading',
                'title_key': 'leading_section',
                'type': 'standard',
                'indicators': ['Leading_Index'],
                'cols': 2,
                'show_charts': True,
            },
        ],
    },
    
    # =========================================================================
    # Page 04: Crypto
    # =========================================================================
    '04_crypto': {
        'title_key': 'crypto_title',
        'sections': [
            {
                'id': 'crypto_prices',
                'title_key': 'crypto_prices',
                'type': 'standard',
                'indicators': ['BTC', 'ETH'],
                'cols': 2,
                'show_charts': True,
            },
            {
                'id': 'eth_leverage',
                'title_key': 'eth_leverage',
                'type': 'api',
                'indicators': ['ETH_Funding_Rate', 'ETH_Open_Interest'],
                'cols': 2,
            },
            {
                'id': 'stablecoins',
                'title_key': 'stablecoins',
                'type': 'api',
                'indicators': ['Stablecoin_Total'],
                'cols': 2,
            },
            {
                'id': 'rwa',
                'title_key': 'rwa_section',
                'type': 'api',
                'indicators': ['Treasury_TVL', 'Gold_TVL'],
                'cols': 2,
            },
        ],
    },
    
    # =========================================================================
    # Page 09: Banking Sector
    # =========================================================================
    '09_banking': {
        'title_key': 'banking_title',
        'sections': [
            {
                'id': 'h8_loans',
                'title_key': 'h8_loans_section',
                'type': 'standard',
                'indicators': ['CI_Loans', 'CRE_Loans', 'Credit_Card_Loans', 'Consumer_Loans'],
                'cols': 4,
                'show_charts': True,
            },
            {
                'id': 'h8_assets',
                'title_key': 'h8_assets_section',
                'type': 'standard',
                'indicators': ['Bank_Cash', 'Bank_Securities', 'Bank_Deposits'],
                'cols': 3,
                'show_charts': True,
            },
            {
                'id': 'sloos_ci',
                'title_key': 'sloos_ci_section',
                'type': 'standard',
                'indicators': ['CI_Std_Large', 'CI_Std_Small', 'CI_Demand'],
                'cols': 3,
                'show_charts': True,
            },
            {
                'id': 'sloos_cre',
                'title_key': 'sloos_cre_section',
                'type': 'standard',
                'indicators': ['CRE_Std_Construction', 'CRE_Std_Office', 'CRE_Std_Multifamily', 'CRE_Demand'],
                'cols': 4,
                'show_charts': True,
            },
            {
                'id': 'financial_stress',
                'title_key': 'financial_stress_section',
                'type': 'standard',
                'indicators': ['Small_Bank_Deposits', 'CC_Delinquency', 'CP_Spread', 'NFCI', 'Breakeven_10Y', 'MOVE'],
                'cols': 3,
                'show_charts': True,
            },
        ],
    },
    
    # =========================================================================
    # Page 08: Sentiment
    # =========================================================================
    '08_sentiment': {
        'title_key': 'sentiment_title',
        'sections': [
            {
                'id': 'fear_greed',
                'title_key': 'fear_greed_section',
                'type': 'api',
                'indicators': ['Crypto_Fear_Greed', 'CNN_Fear_Greed'],
                'cols': 2,
            },
        ],
    },
    
    # =========================================================================
    # Page 10: Market Lab
    # =========================================================================
    '10_market_lab': {
        'title_key': 'market_lab_title',
        'sections': [
            {
                'id': 'advanced_liquidity',
                'title_key': 'advanced_liquidity',
                'type': 'standard',
                'indicators': ['M2_Velocity', 'Financial_Stress', 'Global_Liquidity_Proxy'],
                'cols': 3,
                'show_charts': True,
            },
            {
                'id': 'central_banks',
                'title_key': 'central_banks',
                'type': 'standard',
                'indicators': ['ECB_Assets'],
                'cols': 2,
                'show_charts': True,
            },
        ],
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_page_layout(page_name: str) -> dict:
    """Get layout definition for a page"""
    return PAGE_LAYOUTS.get(page_name, {})


def get_section_indicators(page_name: str, section_id: str) -> list:
    """Get indicator list for a specific section"""
    layout = get_page_layout(page_name)
    for section in layout.get('sections', []):
        if section['id'] == section_id:
            return section.get('indicators', [])
    return []


def get_all_page_names() -> list:
    """Get all defined page names"""
    return list(PAGE_LAYOUTS.keys())


def validate_layout_indicators():
    """Validate that all indicators in layouts exist in INDICATORS registry"""
    from .indicators import INDICATORS
    
    errors = []
    for page_name, layout in PAGE_LAYOUTS.items():
        for section in layout.get('sections', []):
            for indicator in section.get('indicators', []):
                if indicator not in INDICATORS:
                    errors.append(f"{page_name}/{section['id']}: Unknown indicator '{indicator}'")
    
    return errors


if __name__ == '__main__':
    # Validation test
    errors = validate_layout_indicators()
    if errors:
        print("Layout validation errors:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("All layout indicators valid!")
    
    # Summary
    print(f"\nDefined pages: {len(PAGE_LAYOUTS)}")
    for page, layout in PAGE_LAYOUTS.items():
        sections = layout.get('sections', [])
        indicators = sum(len(s.get('indicators', [])) for s in sections)
        print(f"  {page}: {len(sections)} sections, {indicators} indicators")
