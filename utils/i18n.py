# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Internationalization (i18n)
================================================================================
多言語対応モジュール

Usage:
    from utils import t, set_language, get_current_language
    
    # サイドバーで言語切り替え
    set_language('ja')  # or 'en'
    
    # テキスト取得
    st.subheader(t("liquidity_title"))
================================================================================
"""

import streamlit as st
from typing import Dict, Any, Optional

# =============================================================================
# SUPPORTED LANGUAGES
# =============================================================================
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'ja': '日本語',
}

DEFAULT_LANGUAGE = 'en'

# =============================================================================
# TRANSLATIONS DICTIONARY
# =============================================================================
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'en': {
        # --- US M2 Description ---
        'us_m2_desc': '💡 US Money Supply - Auto-fetched from FRED',
        'm2_nominal_notes': 'Nominal',
        'm2_real_notes': 'Real M2 (1982-84 base)',
        
        # --- Time Difference Strings ---
        'time_unknown': 'Unknown',
        'time_just_now': 'Just now',
        'time_minutes_ago': '{n} min ago',
        'time_hours_ago': '{n} hours ago',
        'time_days_ago': '{n} days ago',
        
        # --- App Title & Navigation ---
        'app_title': 'Market Cockpit Pro',
        'app_subtitle': 'Update interval: 10 min | Sources: FRED, Yahoo Finance, DeFiLlama, Alternative.me',
        
        # --- Sidebar ---
        'sidebar_force_update': '🔄 Force Update',
        'sidebar_download_csv': '📥 Download CSV',
        'sidebar_update_status': '🔄 Update Status',
        'sidebar_fresh': '🟢 Fresh',
        'sidebar_stale': '🟡 Stale',
        'sidebar_critical_warning': '🔴 {count} items are outdated',
        'sidebar_health_score': 'Health Score: {score}%',
        'sidebar_alerts': '⚠️ Alerts',
        'sidebar_no_alerts': '✅ No critical alerts',
        
        # --- Alert Messages ---
        'alert_vix_high': '⚠️ VIX spiked to {value} - Market fear is elevated',
        'alert_vix_medium': '📊 VIX rose to {value} - Caution required',
        'alert_reserves_low': '⚠️ Bank reserves dropped to {value}B - Liquidity stress risk',
        'alert_on_rrp_depleted': '🔴 ON RRP depleted to {value}B - Excess liquidity gone',
        'alert_credit_spread_wide': '⚠️ Credit spread widened to {value}% - Credit risk rising',
        'alert_yield_curve_inverted': '⚠️ Yield curve inverted ({value}%) - Recession warning',
        'alert_primary_credit_surge': '🔴 Discount window usage surged ({value}B) - Bank liquidity crisis signs',
        
        'sidebar_ai_status': '🤖 AI Status',
        'sidebar_ready': '✅ Ready',
        'sidebar_not_configured': '❌ Not configured',
        'sidebar_last_update': 'Last Update: {date}',
        'sidebar_data_sources': 'Data Sources: FRED, Yahoo Finance, DeFiLlama, Alternative.me',
        'back_to_top': 'Back to top',
        
        # --- Page Titles ---
        'page_liquidity': '📊 Liquidity & Rates',
        'page_global_money': '🌏 Global Money & FX',
        'page_us_economic': '📈 US Economic Data',
        'page_crypto': '🪙 Crypto Liquidity',
        'page_ai_analysis': '🤖 AI Analysis',
        'page_monte_carlo': '🎲 Monte Carlo',
        'page_market_voices': '📰 Market Voices',
        'page_sentiment': '🎭 Market Sentiment',
        'page_banking': '🏦 Banking Sector',
        'page_analysis_lab': '🧪 Market Analysis Lab',
        'page_currency_lab': '💱 Currency Lab',
        'page_verdict': '⚖️ Market Verdict',
        
        # --- Common Labels ---
        'loading': 'Loading...',
        'no_data': 'No data available',
        'error_data_not_loaded': 'Data not loaded. Please start from main.py.',
        'source_update_date': '🔄 Source Update: {date}',
        'long_term_trend': 'Long-term Trend (2 years)',
        'vs_avg': 'vs avg',
        
        # --- Data Labels (charts.py) ---
        'data_period': 'Data Period',
        'data_date': 'Data Date',
        'source_update': 'Source Update',
        'sparkline_label': '60-day Trend',
        'mom': 'MoM',
        'yoy': 'YoY',
        
        # --- Liquidity Page ---
        'liquidity_title': '🏦 Liquidity & The Fed',
        'valuation_leverage': '📊 Valuation & Leverage Indicators',
        'valuation_leverage_desc': 'Check market overheating and leverage status at a glance',
        'net_liquidity': 'Net Liquidity',
        'net_liquidity_notes': "Market's true fuel",
        'net_liquidity_chart_title': 'Net Liquidity vs S&P 500 (2 years)',
        'on_rrp': 'ON RRP',
        'on_rrp_notes': 'Excess reserves',
        'reserves': 'Reserves',
        'reserves_notes': 'Bank reserve balances',
        'tga': 'TGA',
        'tga_notes': 'Government account',
        'market_plumbing': '🔧 Market Plumbing (Repo & Liquidity)',
        'srf': 'SRF',
        'srf_notes': 'Domestic repo market',
        'fima': 'FIMA',
        'fima_notes': 'Foreign dollar liquidity',
        'sofr': 'SOFR',
        'sofr_notes': 'Secured overnight rate',
        'effr_iorb': 'EFFR - IORB',
        'effr_iorb_notes': 'Fed reserve status',
        'fed_balance_sheet': '🏛️ Fed Balance Sheet (SOMA)',
        'rmp_status': '📊 RMP Status',
        'soma_composition': 'SOMA Composition (Total & Treasury)',
        'soma_total': 'SOMA Total',
        'soma_total_notes': 'Total holdings',
        'soma_treasury': 'SOMA Treasury',
        'soma_treasury_notes': 'Treasury securities held',
        'soma_bills': 'SOMA Bills',
        'soma_bills_notes': 'T-Bills held (RMP core metric)',
        'treasury_share': 'Treasury Share',
        'treasury_share_notes': 'Treasury holdings ratio',
        
        # --- RMP Status ---
        'rmp_monitoring': '📊 RMP Monitoring (Started Dec 12, 2025)',
        'rmp_active': '✅ RMP Active: +${value}B/week (target pace)',
        'rmp_accelerating': '⚠️ RMP Accelerating: +${value}B/week (exceeds normal pace!)',
        'rmp_slowing': '🔄 RMP Slowing: +${value}B/week (pace deceleration)',
        'rmp_selling': '⛔ Bills Selling: ${value}B/week (RMP stopped?)',
        
        'emergency_loans': '🚨 Emergency Loans (Discount Window)',
        'total_loans': 'Total Loans',
        'total_loans_notes': 'Emergency lending total',
        'primary_credit': 'Primary Credit',
        'primary_credit_notes': 'For healthy banks',
        'risk_bonds': '⚠️ Risk & Bonds',
        'risk_bonds_desc': '💡 Monitor market risk and bond market trends',
        'vix_index': 'VIX Index',
        'vix_notes': 'Fear index',
        'credit_spread': 'Credit Spread',
        'credit_spread_notes': 'Junk bond spread',
        'us_10y_yield': 'US 10Y Yield',
        'us_10y_notes': 'Long-term rate',
        
        # --- Valuation & Leverage ---
        'sp500_pe': 'S&P 500 P/E',
        'sp500_pe_help': 'Historical avg ~19.5. Above 25 = overheated, below 15 = undervalued',
        'nasdaq_pe': 'NASDAQ P/E (QQQ)',
        'nasdaq_pe_help': 'Tech stock valuation indicator',
        'btc_funding_rate': 'BTC Funding Rate',
        'long_heavy': 'Long heavy',
        'short_heavy': 'Short heavy',
        'neutral': 'Neutral',
        'funding_rate_help': 'Funding Rate > 0.1% = Long overweight (overheated). < -0.1% = Short overweight',
        'btc_ls_ratio': 'BTC Long/Short Ratio',
        'long_biased': 'Long biased',
        'short_biased': 'Short biased',
        'balanced': 'Balanced',
        'ls_ratio_help': 'Long/Short account ratio. 1.0 = balanced',
        
        # --- Open Interest ---
        'open_interest_title': '📈 Open Interest (Leverage Buildup)',
        'btc_open_interest': 'BTC Open Interest',
        'eth_open_interest': 'ETH Open Interest',
        'danger_zone': 'Danger Zone',
        'elevated': 'Elevated',
        'low': 'Low',
        'normal': 'Normal',
        'vs_30d_avg': 'vs 30-day avg',
        'ath_ratio': '30-day high ratio',
        'status': 'Status',
        'source': 'Source',
        'accumulating_data': '📈 Accumulating data ({days}/7 days) - Hyperliquid (DEX)',
        'open_interest_guide': '''
💡 **How to read Open Interest**
- **+20% vs 30-day avg** 🔴: Excessive leverage → High liquidation cascade risk
- **±5% vs 30-day avg** 🟢: Normal range
- **Source**: Hyperliquid (DEX) - Decentralized exchange data auto-accumulated
- **Accumulation**: Comparison available after 7 days, full function after 30 days
''',
        
        # --- Global Money Page ---
        'global_money_title': '🌏 Global Money Supply & FX',
        'global_m2': 'Global M2 Supply',
        'global_m2_desc': 'Track global liquidity trends across major economies',
        'us_m2': 'US M2',
        'china_m2': 'China M2',
        'japan_m2': 'Japan M2',
        'eu_m2': 'EU M2',
        'fx_rates': '💱 FX Rates',
        'dxy': 'DXY (Dollar Index)',
        'usdjpy': 'USD/JPY',
        'eurusd': 'EUR/USD',
        
        # --- US Economic Page ---
        'us_economic_title': '📈 US Economic Indicators',
        'employment': '👷 Employment',
        'nfp': 'Non-Farm Payrolls',
        'nfp_notes': 'Monthly job creation',
        'adp': 'ADP Employment',
        'adp_notes': 'Private sector jobs',
        'unemployment': 'Unemployment Rate',
        'unemployment_notes': 'U-3 rate',
        'jolts': 'JOLTS Job Openings',
        'jolts_notes': 'Labor demand',
        'icsa': 'Initial Claims',
        'icsa_notes': 'Weekly jobless claims',
        'inflation': '📊 Inflation',
        'cpi': 'CPI',
        'cpi_notes': 'Consumer prices YoY',
        'core_cpi': 'Core CPI',
        'core_cpi_notes': 'Ex food & energy',
        'michigan_inflation_title': 'Michigan Inflation Expectations (1Y)',
        'michigan_inflation_label': 'Inflation Exp',
        'michigan_inflation_desc': '💡 Consumer inflation expectations survey - Fed closely monitors this',
        'michigan_inflation_notes': '1-year ahead expected inflation rate',
        'fed_target': 'Fed 2% target',
        'ppi': 'PPI',
        'ppi_notes': 'Producer prices',
        'core_pce': 'Core PCE',
        'core_pce_label': 'Core PCE',
        'core_pce_notes': "Fed's preferred measure",
        'economy': '🏭 Economy',
        'retail_sales': 'Retail Sales',
        'retail_sales_notes': 'Consumer spending',
        'gdp': 'Real GDP',
        'gdp_notes': 'Quarterly growth',
        'consumer_sentiment': 'Consumer Sentiment',
        'consumer_sentiment_notes': 'UMich survey',
        'yield_curve': 'Yield Curve (10Y-2Y)',
        'yield_curve_notes': 'Recession indicator',
        
        # --- Crypto Page ---
        'crypto_title': '🪙 Crypto Liquidity & Stablecoins',
        'stablecoins': '💵 Stablecoin Supply',
        'stablecoin_desc': 'Crypto market liquidity proxy',
        'usdt': 'USDT (Tether)',
        'usdc': 'USDC (Circle)',
        'dai': 'DAI',
        'fear_greed': '😱 Fear & Greed Index',
        'extreme_fear': 'Extreme Fear',
        'fear': 'Fear',
        'greed': 'Greed',
        'extreme_greed': 'Extreme Greed',
        
        # --- AI Analysis Page ---
        'ai_analysis_title': '🤖 AI Market Analysis',
        'ai_analysis_desc': 'AI-powered market commentary and insights',
        'generate_analysis': '🔮 Generate Analysis',
        'generating': 'Generating...',
        'gemini_analysis': '🌟 Gemini Analysis',
        'claude_analysis': '🤖 Claude Analysis',
        
        # --- Monte Carlo Page ---
        'monte_carlo_title': '🎲 Monte Carlo Simulation',
        'monte_carlo_desc': 'Price path simulation with multiple distribution models',
        'simulation_params': 'Simulation Parameters',
        'initial_price': 'Initial Price ($)',
        'days': 'Days',
        'simulations': 'Simulations',
        'volatility': 'Annual Volatility (%)',
        'drift': 'Annual Drift (%)',
        'distribution': 'Distribution Model',
        'student_t': 'Student-t (Fat Tails)',
        'jump_diffusion': 'Jump Diffusion',
        'run_simulation': '▶️ Run Simulation',
        'results': 'Results',
        'median_price': 'Median Final Price',
        'percentile_5': '5th Percentile',
        'percentile_95': '95th Percentile',
        
        # --- Market Voices Page ---
        'market_voices_title': '📰 Market Voices',
        'primary_sources': '🔍 Primary Source Hunter',
        'primary_sources_desc': 'Search government & central bank primary sources',
        'search_keyword': 'Search Keyword',
        'search_mode': 'Search Mode',
        'mode_primary': 'Primary Sources (Pro)',
        'mode_general': 'General News',
        'context_select': 'Context Selection',
        'search_button': '🔎 Search Primary Sources',
        
        # --- Sentiment Page ---
        'sentiment_title': '🎭 Market Sentiment',
        'sentiment_desc': 'Investor psychology indicators',
        'crypto_fear_greed': 'Crypto Fear & Greed',
        'cnn_fear_greed': 'CNN Fear & Greed',
        'aaii_sentiment': 'AAII Investor Sentiment',
        'put_call_ratio': 'Put/Call Ratio',
        'bullish': 'Bullish',
        'bearish': 'Bearish',
        'bull_bear_spread': 'Bull-Bear Spread',
        
        # --- Banking Page ---
        'banking_title': '🏦 Banking Sector Health',
        'lending_standards': 'Lending Standards',
        'ci_lending': 'C&I Lending Standards',
        'cre_lending': 'CRE Lending Standards',
        'bank_deposits': 'Bank Deposits',
        'small_bank_deposits': 'Small Bank Deposits',
        'delinquency': 'Delinquency Rates',
        'cc_delinquency': 'Credit Card Delinquency',
        
        # --- Analysis Lab Page ---
        'analysis_lab_title': '🧪 Market Analysis Lab',
        'analysis_lab_desc': 'Advanced market analysis tools',
        
        # --- Global Money Page Extended ---
        'global_money_subtitle': '💡 Global liquidity, FX, commodities, and crypto trends',
        'global_m2_total': '🌍 Global M2 Total (True Total)',
        'formula': 'Formula: US + CN(USD) + JP(USD) + EU(USD)',
        'vs_prior': 'vs Prior',
        'global_liquidity_proxy': '🌊 Global Liquidity Proxy (Fed + ECB)',
        'global_liquidity_desc': '💡 Fed Assets + ECB Assets (USD). High market sensitivity liquidity indicator.',
        'daily_change': 'Daily Change',
        'trend_ytd': 'Trend (YTD)',
        'yoy_growth': 'YoY Growth (%)',
        'yoy_growth_desc': '💡 Year-over-year change trend',
        'liquidity_expanding': '🟢 Liquidity Expanding',
        'liquidity_contracting': '🔴 Liquidity Contracting',
        'insufficient_data_yoy': 'Insufficient data for YoY calculation (252+ days needed)',
        'regional_m2': '💵 Regional M2 Breakdown',
        'manual_update': 'Manual Update',
        'auto_fetch_unavail': '⚠️ Auto-fetch unavailable',
        'announced_by': 'Announced by',
        'nominal': 'Nominal',
        'real': 'Real',
        'cpi_adjusted': 'CPI {cpi}% adjusted',
        'credit_impulse': '📊 Credit Impulse',
        'credit_impulse_desc': '⚠️ Proxy: BIS quarterly credit data via FRED (CRDQCNAPABIS)',
        'credit_impulse_notes': '(Credit flow change/GDP)',
        'long_term_5y': 'Long-term Trend (5 years)',
        'fx_section': '💱 Foreign Exchange',
        'dollar_index': 'Dollar Index',
        'dollar_strength': 'Dollar strength indicator',
        'yen_carry': 'Yen carry',
        'euro_dollar': 'Euro dollar',
        'yuan': 'Yuan',
        'global_indices': '📈 Global Indices',
        'global_indices_desc': '💡 Major stock indices',
        'nikkei_notes': 'Nikkei 225 Index',
        'sp500_notes': 'US large-cap index',
        'commodities_section': '🛢️ Commodities',
        'gold_futures': 'Gold futures',
        'silver_futures': 'Silver futures',
        'oil_futures': 'Oil futures',
        'copper_futures': 'Copper futures (leading indicator)',
        'crypto_section': '🪙 Cryptocurrency',
        'risk_on_indicator': 'Risk-on indicator',
        'defi_base': 'DeFi base',
        
        # --- Fiat Health Monitor ---
        'fiat_health_subtitle': '💡 Visualize fiat currency purchasing power decline (Gold/BTC denominated)',
        'fiat_gold_denominated': '🥇 Gold-denominated Currency Values',
        'fiat_decline_note': '↓Decline = Currency purchasing power loss (2Y ago=100)',
        'fiat_btc_denominated': '₿ BTC-denominated Currency Values',
        'fiat_gold_btc': '🥇₿ Gold-denominated BTC',
        'fiat_btc_gold_oz': 'How many oz of Gold can 1 BTC buy?',
        'fiat_health_no_data': '⚠️ Fiat Health Monitor: Insufficient data',
        
        # --- Crypto Page Extended ---
        'crypto_subtitle': '💡 Crypto market liquidity and RWA (Real World Assets) tokenization trends',
        'stablecoin_section': '💵 Stablecoin Supply',
        'total_stablecoin': 'Total Stablecoin Supply',
        'stablecoin_total_help': 'Total supply of all stablecoins',
        'stablecoin_history': '📈 Stablecoin Supply History',
        'short_term': 'Short Term (90d)',
        'long_term_all': 'Long Term (All Time)',
        'top_stablecoins': 'Top 10 Stablecoins by Supply',
        'supply_distribution': 'Supply Distribution',
        'last_update': '📅 Last Update',
        'stablecoin_fetch_failed': '⚠️ Failed to fetch stablecoin data.',
        'tokenized_treasury': '📜 Tokenized Treasuries',
        'treasury_tvl': 'Treasury TVL',
        'treasury_help': 'Tokenized US Treasury',
        'tokenized_gold': '🪙 Tokenized Gold',
        'gold_tvl': 'Gold TVL',
        'gold_help': 'Tokenized gold',
        'other_rwa': '🏢 Other RWA',
        'other_rwa_tvl': 'Other RWA TVL',
        'other_rwa_help': 'Other real world assets',
        'tokenized_us_treasury': '📜 Tokenized US Treasuries',
        'rwa_fetch_failed': '⚠️ Failed to fetch RWA data.',
        'market_depth': '💧 Market Depth (Liquidity Quality)',
        'market_depth_desc': 'Centralized (CEX) vs Decentralized (DEX) Liquidity Cost',
        'avg_cex_spread': 'Avg CEX Spread',
        'avg_dex_spread': 'Avg DEX Spread',
        'higher_cost': '{ratio}x Higher Cost',
        'market_depth_unavail': 'Market Depth data unavailable (CoinGecko API limit or timeout)',
        'market_depth_chart_title': 'Bid-Ask Spread (%) Comparison',
        'crypto_why_important': '''
💡 **Why This Matters**
- **Stablecoins**: Measure capital inflow/outflow to crypto market
- **Tokenized Treasury**: Gauge of institutional participation
- **Tokenized Gold**: Digitization of traditional safe assets
''',
        
        # --- US Economic Page Extended ---
        'us_economic_page_title': '📈 US Economic Data',
        'us_economic_section_rates': '🏦 1. Interest Rates',
        'ff_upper': 'FF Target Rate (Upper)',
        'ff_upper_label': 'FF Upper',
        'effr_label': 'EFFR',
        'sofr_label': 'SOFR',
        'ff_upper_notes': 'Policy rate upper bound',
        'ff_lower': 'FF Target Rate (Lower)',
        'ff_lower_notes': 'Policy rate lower bound',
        'effr_notes': 'Effective FF Rate',
        'sofr_notes_full': 'Secured rate (repo market)',
        'us_economic_section_employment': '👷 2. Employment',
        'jolts_title': 'JOLTS Job Openings',
        'jolts_label': 'JOLTS Level',
        'nfp_title': 'Non-Farm Payrolls (MoM)',
        'result': 'Result',
        'thousand_people': 'K ({val:.1f}0K people)',
        'nfp_monthly_change': 'NFP Monthly Change Trend',
        'unemployment_rate': 'Unemployment Rate',
        'vs_last_month': 'vs last month',
        'avg_hourly_earnings': 'Average Hourly Earnings',
        'icsa_title': 'Initial Claims (ICSA)',
        'latest_week': 'Latest Week',
        'vs_last_week': 'vs last week',
        'us_economic_section_inflation': '⚖️ 3. Inflation',
        'cpi_title': 'Consumer Price Index (CPI)',
        'core_cpi_title': 'Core CPI',
        'ppi_title': 'Producer Price Index (PPI)',
        'cpi_notes_full': 'Consumer Price Index',
        'core_pce_title': 'Core PCE Inflation (YoY)',
        'current_inflation': 'Current Inflation Rate',
        'ppi_notes_full': 'Producer Price Index',
        'us_economic_section_economy': '📈 4. Economy',
        'retail_sales_title': 'Retail Sales',
        'consumer_sentiment_title': 'Consumer Sentiment',
        'gdp_label': 'GDP Level',
        'gdp_title': 'Real GDP (Annualized Growth)',
        'qoq_annualized': 'QoQ Annualized',
        'level': 'Level',
        'yield_curve_title': '🔗 Yield Curve (2Y-10Y)',
        'yield_curve_label': '2Y-10Y Spread',
        'inversion_boundary': 'Inversion boundary',
        
        # --- US Economic Page: Leading & Housing (2026-01-22 added) ---
        'us_economic_section_leading': 'Leading Indicators',
        'leading_indicators_desc': '💡 Economic leading indicators for forecasting business cycles',
        'ism_pmi_notes': 'Manufacturing health (50+ = expansion)',
        'expansion_contraction_boundary': 'Expansion/Contraction boundary',
        'leading_index_title': 'Chicago Fed Activity Index',
        'leading_index_label': 'Chicago Fed CFNAI',
        'leading_index_notes': 'Chicago Fed CFNAI (3-month MA) - Economic activity leading indicator, Above 0 = Expansion / Below 0 = Slowdown',
        'zero_line': 'Zero line',
        'us_economic_section_housing': 'Housing',
        'housing_indicators_desc': '💡 Housing market leading indicators',
        'housing_starts_title': 'Housing Starts',
        'housing_starts_label': 'Housing Starts',
        'housing_starts_notes': 'New housing construction (SAAR, thousands)',
        'building_permits_title': 'Building Permits',
        'building_permits_label': 'Building Permits',
        'building_permits_notes': 'Authorized building permits (SAAR, thousands)',
        
        # --- AI Analysis Page Extended ---
        'ai_data_count': 'AI Monitoring: {ai_count} / {total_count}',
        'ai_data_excluded': '⚠️ {count} items excluded from AI analysis',
        'ai_all_monitored': '✅ All data monitored',
        'ai_collecting_data': '📊 Collecting market data...',
        'ai_settings': '⚙️ Analysis Settings',
        'ai_select': 'Select AI',
        'ai_focus_areas': '🎯 Focus Areas',
        'ai_focus_prompt': 'Items to focus AI on',
        'ai_focus_liquidity': 'Liquidity (Plumbing)',
        'ai_focus_inflation': 'Inflation & Interest',
        'ai_focus_employment': 'Employment & Recession',
        'ai_focus_banking': 'Banking & Credit Crisis',
        'ai_focus_geopolitics': 'Geopolitics & Commodities',
        'ai_focus_crypto': 'Cryptocurrency',
        'ai_full_analysis': '🚀 Full Market Analysis',
        'ai_gemini_analyzing': '🔷 Gemini 3 Flash analyzing...',
        'ai_claude_analyzing': '🟣 Claude 4.5 Opus analyzing...',
        'ai_custom_analysis': '🎯 Custom Analysis',
        'ai_custom_prompt': 'What would you like to focus on?',
        'ai_custom_placeholder': 'e.g. Compare ON RRP trend with stock market',
        'ai_run_custom': '🔍 Run Custom Analysis',
        'ai_search_news': '📰 Search Latest News',
        'ai_search_placeholder': 'e.g. Fed rate cut',
        'ai_search_button': '🔎 Search News',
        'ai_policy_context': '''You are a legendary global macro strategist.
Rather than simply summarizing news, you analyze the "plumbing" behind the data - the flow of liquidity and market participant incentives.''',
        'ai_response_language': 'IMPORTANT: You must respond entirely in English, regardless of the input language.',
        'ai_analysis_instruction': 'Please analyze the following market data structurally:',
        
        # --- Monte Carlo Page Extended ---
        'mc_title': '🎲 Monte Carlo Simulation',
        'mc_subtitle': '💡 Price path simulation with multiple distribution models',
        'mc_settings': '⚙️ Settings',
        'mc_asset': 'Asset',
        'mc_period_days': 'Forecast Period (days)',
        'mc_simulations': 'Simulations',
        'mc_model': 'Distribution Model',
        'mc_model_normal': 'Normal (Gaussian)',
        'mc_model_t': 'Student-t (Fat-tails)',
        'mc_model_jump': 'Jump-Diffusion (Merton)',
        'mc_run': '▶️ Run Simulation',
        'mc_running': '🔄 Running simulation...',
        'mc_results': '📊 Results',
        'mc_expected_price': 'Expected Price (Median)',
        'mc_bullish': 'Bullish (90%)',
        'mc_bearish': 'Bearish (10%)',
        'mc_var_95': 'VaR 95%',
        'mc_evt_var_99': 'EVT VaR 99%',
        'mc_var_ci': 'VaR 95% Confidence Interval',
        'mc_regime': 'Market Regime',
        'mc_jump_freq': 'Jump Frequency',
        'mc_regime_high_vol': '🔥 High Volatility',
        'mc_regime_low_vol': '❄️ Low Volatility',
        'mc_regime_normal': '📊 Normal',
        'mc_regime_unknown': 'Unknown',
        'mc_advanced': '📊 Advanced Analytics',
        'mc_vol_regime': 'Volatility Regime',
        'mc_evt_analysis': 'Extreme Value Theory (EVT)',
        'mc_fat_tails': 'Fat-tail risk',
        'mc_about': '📖 About Monte Carlo Simulation',
        'mc_disclaimer': '⚠️ This is not investment advice. Past data simulation does not guarantee future performance.',
        'mc_x_template': '📱 Copy to X/Twitter',
        'mc_generate_x': '🐦 Generate X Post',
        'mc_preset_assets': 'Preset Assets',
        'mc_custom_ticker': 'Custom Tickers',
        'mc_custom_placeholder': 'e.g. AAPL, 7203.T, ETH-USD',
        'mc_custom_help': 'Enter yfinance tickers separated by commas',
        'mc_distribution': 'Distribution',
        'mc_dist_help': 'Normal: Standard GBM. Student-t: Fat-tail support. Jump-Diffusion: Black swan events.',
        'mc_parameters': '📊 Parameters',
        'mc_period_years': 'Forecast Period (years)',
        'mc_trials': 'Trials',
        'mc_market_regime': 'Market Regime',
        'mc_analysis_of': '📊 {asset} ({ticker}) Analysis',
        'mc_fetch_failed': 'Data fetch failed: {ticker}',
        'mc_bullish_label': '**Bullish (Top 10%):**',
        'mc_bearish_label': '**Bearish (Bottom 10%):**',
        'mc_risk_metrics': '🛡 **Risk Metrics**',
        'mc_var_ci_label': 'VaR 95% CI: [{lower:.2f}%, {upper:.2f}%]',
        'mc_historical_stats': '📊 **Historical Stats**',
        'mc_annualized_return': '**Annualized Return:**',
        'mc_annualized_vol': '**Annualized Vol:**',
        'mc_df_estimated': '**Degrees of Freedom (est.):**',
        'mc_df_note': 'Lower DF = fatter tails (more volatile)',
        'mc_jump_avg': 'Avg Jump: {avg:.1f}%',
        'mc_welcome_title': '### 🎲 Welcome to Monte Carlo Simulation',
        'mc_welcome_intro': 'This page provides **financial engineering-based** asset price simulations.',
        'mc_model_guide_title': '**🎯 Model Selection Guide (Recommended):**',
        'mc_model_table': '''| Model | When to Use | Target Assets |
|--------|--------------|-------|
| **Normal** ⭐Recommended | Regular forecasting / Beginners | Stocks, Indices |
| **Student-t** | Want to consider crash risk | High volatility assets |
| **Jump-Diffusion** | Want worst-case scenarios | Crypto, Emerging markets |''',
        'mc_model_tip': "💡 **If unsure, Normal is fine.** Student-t and Jump-Diffusion give more pessimistic forecasts.",
        'mc_tech_title': '**Implemented Techniques (8 core methods):**',
        'mc_tech_list': '''- Variance Reduction (Antithetic Variates)
- Distribution Models (Normal, Student-t, Jump-Diffusion)
- Risk Analysis (VaR, CVaR, EVT, Bootstrap)
- Market Analysis (Regime Detection, Jump Parameter Estimation)''',
        'mc_disclaimer_title': '⚠️ **Disclaimer:**',
        'mc_disclaimer_list': '''- This app output is **not investment advice**
- Based on historical data simulation, **does not guarantee future results**
- Investment decisions must be made at **your own risk**''',
        'mc_start_instruction': '👆 Select assets from the settings above to start simulation.',
        
        # --- Market Voices Page Extended ---
        'mv_subtitle': '💡 Primary sources from Fed/Treasury/Major central banks - No AI interpretation',
        'mv_direct_links': '🏛️ Major Institution Direct Links',
        'mv_us': '🇺🇸 United States',
        'mv_overseas': '🌍 Overseas Central Banks',
        'mv_rss_feeds': '📡 Real-time RSS Feeds',
        'mv_no_articles': '📭 No articles found',
        'mv_error_feed': '⚠️ Error retrieving feed',
        'mv_ecb': 'ECB (European Central Bank)',
        'mv_boj': 'BOJ (Bank of Japan)',
        'mv_boe': 'BOE (Bank of England)',
        'mv_pboc': 'PBoC (People\'s Bank of China)',
        'mv_guide_title': '📚 How to Read Information Sources',
        'mv_guide_content': '''### Primary vs Secondary Information

| Type | Example | Reliability |
|------|-----|--------|
| **Primary** | Fed statements, Minutes, Statistical data | ⭐⭐⭐ |
| Secondary | Reuters, Bloomberg articles | ⭐⭐ |
| Tertiary | Social media, Personal blogs | ⭐ |

### Fed Watch Key Points

- **FOMC Statement**: Policy rate and future direction
- **Minutes**: Released 3 weeks later, detailed committee discussions
- **SEP (Economic Projections)**: Dot Plot = Committee members\' rate forecasts
- **Powell Press Conference**: Read "between the lines" of the statement

### Cautions

⚠️ Don\'t judge by headlines alone  
⚠️ "According to sources" is not confirmed information  
⚠️ Market reaction ≠ Correct interpretation
''',
        'mv_footer': '💬 This page is a link collection. Analysis and interpretation are up to you.',
        
        # --- Sentiment Page Extended ---
        'sent_subtitle': '💡 Market psychology at a glance - Fear & Greed, Put/Call Ratio, Investor Sentiment',
        'sent_fg_section': '🎯 Fear & Greed Index',
        'sent_cnn_fg': '📈 CNN Fear & Greed (Stocks)',
        'sent_crypto_fg': '₿ Crypto Fear & Greed',
        'sent_vix': '📊 VIX Index (Fear Index)',
        'sent_extreme_fear': 'Extreme Fear',
        'sent_fear': 'Fear',
        'sent_neutral': 'Neutral',
        'sent_greed': 'Greed',
        'sent_extreme_greed': 'Extreme Greed',
        'sent_30d_trend': '📊 30-day trend',
        'sent_cnn_unavail': '📊 CNN Fear & Greed currently unavailable (API limit)',
        'sent_aaii_section': '📊 AAII Investor Sentiment',
        'sent_aaii_desc': 'US individual investor sentiment survey (weekly)',
        'sent_aaii_bullish': 'Bullish',
        'sent_aaii_bearish': 'Bearish',
        'sent_aaii_neutral': 'Neutral',
        'sent_bull_bear_spread': 'Bull-Bear Spread',
        'sent_bull_bear_extreme': '🔴 Extreme bullish/bearish',
        'sent_aaii_unavail': '📊 AAII Sentiment data unavailable',
        'sent_put_call_section': '📊 Options Market (Put/Call Ratio)',
        'sent_put_call_desc': 'Options market sentiment indicator',
        'sent_put_call_high': '🔴 Risk-off (Hedging heavy)',
        'sent_put_call_low': '🟢 Risk-on (Complacent)',
        'sent_put_call_normal': '🟡 Normal range',
        'sent_put_call_unavail': '📊 Put/Call Ratio data unavailable',
        'sent_60d_trend': '📊 60-day trend',
        'sent_crypto_error': '⚠️ Crypto Fear & Greed fetch error',
        'sent_vix_no_data': '⚠️ VIX data unavailable',
        'vix_low': '🟢 Low Volatility',
        'vix_normal': '🟡 Normal',
        'vix_elevated': '🟠 Elevated',
        'vix_high_fear': '🔴 High Fear',
        'sent_aaii_title': '👥 AAII Investor Sentiment Survey',
        'sent_aaii_contrarian': 'Individual investor sentiment survey (weekly) - Famous as contrarian indicator',
        'sent_aaii_bullish_label': '🐂 Bullish',
        'sent_aaii_neutral_label': '😐 Neutral',
        'sent_aaii_bearish_label': '🐻 Bearish',
        'sent_spread_overheated': '(Overheated)',
        'sent_spread_somewhat_bullish': '(Somewhat Bullish)',
        'sent_spread_neutral': '(Neutral)',
        'sent_spread_somewhat_bearish': '(Somewhat Bearish)',
        'sent_spread_bottom_signal': '(Bottom Signal?)',
        'sent_aaii_update': '🔄 Source Update: {date} (Weekly)',
        'sent_distribution': '**Sentiment Distribution:**',
        'sent_category': 'Category',
        'sent_ratio': 'Ratio',
        'sent_spread_guide_title': '📈 How to read Bull-Bear Spread',
        'sent_spread_guide': '''**Bull-Bear Spread** = Bullish% − Bearish%

| Value | Meaning | Interpretation |
|-----|------|------|
| **+20% or more** | Bullish dominant | 🔴 Overheated (Top signal?) |
| **+10% to +20%** | Somewhat bullish | 🟠 Optimistic |
| **−10% to +10%** | Neutral | 🟢 Balanced |
| **−10% to −20%** | Somewhat bearish | 🟠 Pessimistic |
| **−20% or less** | Bearish dominant | 🔴 Bottom signal? |

💡 **Contrarian Strategy**: Tops often form when everyone is bullish, bottoms when bearish!
''',
        'sent_aaii_error': '⚠️ AAII data fetch error',
        'sent_put_call_title': '### 📊 Put/Call Ratio',
        'sent_put_call_subtitle': 'Options market bullish/bearish degree - High = Bearish, Low = Bullish',
        'sent_put_call_preparing': '📝 Put/Call Ratio data source is being prepared. Showing VIX as proxy.',
        'sent_put_call_ref': 'VIX (Reference): {value:.1f}',
        'sent_guide_section': '### 📚 How to Read Sentiment Indicators',
        'sent_guide_expand': '💡 Indicator Interpretation Guide',
        'sent_guide_content': '''| Indicator | Extreme Fear | Fear | Neutral | Greed | Extreme Greed |
|------|-----------|------|------|------|-----------|
| **Fear & Greed** | 0-25 | 25-45 | 45-55 | 55-75 | 75-100 |
| **VIX** | >30 | 20-30 | 15-20 | 10-15 | <10 |
| **Put/Call** | >1.2 | 0.9-1.2 | 0.7-0.9 | 0.5-0.7 | <0.5 |

**Contrarian Strategy Tips:**
- "Extreme Fear" may be a buying opportunity
- "Extreme Greed" may be a profit-taking signal
- Be cautious when AAII shows extremely high bullish sentiment
''',
        
        # --- Banking Page Extended ---
        'bank_subtitle': '💡 FRB H.8 Weekly Data & SLOOS Quarterly Survey - Bank lending and credit conditions',
        'bank_h8_section': '📊 H.8 Weekly Data',
        'bank_h8_desc': 'FRB weekly aggregate data for all US commercial banks',
        'bank_cash': 'Bank Cash Holdings',
        'bank_cash_notes': 'Bank cash hoarding',
        'bank_ci_loans': 'C&I Loans Outstanding',
        'bank_ci_loans_notes': 'Commercial & Industrial loans',
        'bank_cre_loans': 'CRE Loans Outstanding',
        'bank_cre_loans_notes': 'Commercial Real Estate loans',
        'bank_sloos_section': '📋 SLOOS Quarterly Survey',
        'bank_sloos_desc': 'Senior Loan Officer Opinion Survey (Quarterly)',
        'bank_ci_tightening': 'C&I Lending Standards',
        'bank_ci_tightening_notes': 'Positive = Tightening',
        'bank_cre_tightening': 'CRE Lending Standards',
        'bank_cre_tightening_notes': 'Positive = Tightening',
        'bank_ci_demand': 'C&I Loan Demand',
        'bank_ci_demand_notes': 'Positive = Strong demand',
        'bank_cre_demand': 'CRE Loan Demand',
        'bank_cre_demand_notes': 'Positive = Strong demand',
        'bank_deposits_section': '💰 Deposits & Delinquency',
        'bank_large_deposits': 'Large Bank Deposits',
        'bank_small_deposits': 'Small Bank Deposits',
        'bank_cc_delinquency': 'Credit Card Delinquency',
        
        # --- Banking Page: H.8 Consumer & Deposits ---
        'bank_h8_consumer': '💳 H.8 Consumer & Deposits',
        'bank_credit_card': 'Credit Card Loans',
        'bank_credit_card_notes': 'Consumer credit strength',
        'bank_consumer_loans': 'Consumer Loans',
        'bank_consumer_loans_notes': 'Consumer loan balance',
        'bank_securities': 'Bank Securities',
        'bank_securities_notes': 'Interest rate risk',
        'bank_deposits_title': 'Bank Deposits',
        'bank_deposits_notes': 'Funding changes',
        
        # --- Banking Page: Financial Stress Indicators ---
        'bank_stress_section': '⚠️ Financial Stress Indicators',
        'bank_move': 'MOVE Index',
        'bank_move_desc': 'Bond fear index',
        'bank_move_notes': 'Spikes before crises',
        'bank_small_deposits_desc': 'Small bank deposit balance',
        'bank_small_deposits_notes': 'Sharp drop = bank run warning',
        'bank_nfci': 'NFCI',
        'bank_nfci_desc': 'Chicago Fed Financial Conditions',
        'bank_nfci_notes': '+ tight, - loose',
        'bank_cc_delinquency_desc': 'Consumer stress indicator',
        'bank_cc_delinquency_notes': 'Rise = recession warning',
        'bank_breakeven': 'Breakeven 10Y',
        'bank_breakeven_desc': 'Expected inflation',
        'bank_breakeven_notes': '2.2-2.3% stable',
        'bank_cp_spread': 'CP Spread',
        'bank_cp_spread_desc': 'Short-term corporate funding stress',
        'bank_cp_spread_notes': 'Spike = Lehman-level warning',
        'bank_total_loans': 'Total Loans',
        'bank_total_loans_desc': 'Credit creation',
        'bank_total_loans_notes': 'Decline = credit crunch',
        'bank_copper_gold': 'Copper/Gold Ratio',
        'bank_copper_gold_desc': 'Economic leading indicator',
        'bank_cu_au_ratio': 'Cu/Au Ratio',
        'bank_cu_au_help': 'Copper($)/Gold($) * 1000',
        
        # --- Banking Page: C&I Lending SLOOS ---
        'bank_ci_std_small': 'C&I Standards (Small Firms)',
        'bank_ci_std_small_notes': 'Employment leading indicator',
        'bank_ci_tightening_indicator_notes': '>0 tightening, >20% warning',
        'bank_ci_demand_indicator_notes': 'Watch gap vs standards',
        
        # --- Banking Page: CRE Lending SLOOS ---
        'bank_cre_section': '🏢 CRE Lending - SLOOS',
        'bank_cre_construction': 'Construction & Land',
        'bank_cre_construction_notes': 'Real estate development gate',
        'bank_cre_multifamily': 'Multifamily',
        'bank_cre_multifamily_notes': 'Housing supply impact',
        'bank_cre_office': 'Office/Non-Residential',
        'bank_cre_office_notes': 'Office crisis watch',
        'bank_cre_demand_indicator_notes': 'Real estate investment appetite',
        
        # --- Banking Page: Loan Comparison ---
        'bank_loan_comparison': '📈 Loan Balance Comparison',
        
        # --- Analysis Lab Page Extended ---
        'lab_subtitle': '💡 Lab for analyzing macro liquidity and financial conditions',
        'lab_glp_section': '🌊 Global Liquidity Proxy (GLP)',
        'lab_glp_about': '📖 What is GLP?',
        'lab_glp_no_data': 'GLP data unavailable',
        'lab_m2v_section': '🔄 M2 Velocity',
        'lab_m2v_about': '📖 What is M2 Velocity?',
        'lab_fsi_section': '📊 Financial Stress Index (FSI)',
        'lab_fsi_about': '📖 What is FSI?',
        'lab_credit_section': '📊 Credit Conditions',
        'lab_bond_etf_section': '📊 Corporate Bond ETFs',
        'lab_ig_etf': 'Investment Grade (LQD)',
        'lab_hy_etf': 'High Yield (HYG)',
        'lab_data_period': '📅 Data Period',
        'lab_source_update': '🔄 Source Update',
        'lab_calculated': 'Calculated value',
        
        # --- Analysis Lab: M2V & FSI Status ---
        'lab_m2v_unavailable': 'M2V data unavailable',
        'lab_m2v_historic_low': '🔵 Historic low (money hoarding)',
        'lab_m2v_low': '🟡 Low level',
        'lab_m2v_normal': '🟢 Normal range',
        'lab_fsi_unavailable': 'FSI data unavailable',
        'lab_fsi_loose': '🟢 Loose (Risk-on)',
        'lab_fsi_normal': '🟡 Normal',
        'lab_fsi_caution': '🟠 Caution',
        'lab_fsi_crisis': '🔴 Crisis level',
        
        # --- Analysis Lab: Lag Correlation ---
        'lab_lag_correlation': '📊 Lag Correlation Analysis',
        'lab_lag_desc': '💡 GLP leading indicator analysis for stocks/BTC',
        'lab_compare_with': 'Compare with',
        'lab_best_lag': 'Best Lag',
        'lab_lag_help': 'GLP leads by this many days',
        'lab_correlation': 'Correlation',
        'lab_correlation_help': 'Correlation coefficient (-1 to 1)',
        'lab_strong_positive': '🟢 Strong positive correlation',
        'lab_moderate': '🟡 Moderate correlation',
        'lab_weak': '🔴 Weak correlation',
        'lab_insufficient_data_lag': 'Insufficient data (100+ days needed)',
        'lab_target_unavailable': '{target} data unavailable',
        'lab_glp_unavailable': 'GLP data unavailable',
        
        # --- Analysis Lab: Regime Detection ---
        'lab_regime_detection': '🚦 Regime Detection',
        'lab_regime_desc': '💡 Liquidity acceleration/deceleration detection',
        'lab_regime_chance': '## 🟢 Chance',
        'lab_regime_caution': '## 🔴 Caution',
        'lab_liquidity_accelerating': 'Liquidity accelerating',
        'lab_liquidity_decelerating': 'Liquidity decelerating',
        'lab_ma20_change': 'MA20 Change',
        'lab_ma20_help': '5-day change rate',
        'lab_insufficient_data_short': 'Insufficient data',
        
        # --- Analysis Lab: Cross-Asset Spreads ---
        'lab_cross_spreads': '💧 Cross-Asset Spreads',
        'lab_spreads_desc': '💡 Major ETF Bid-Ask spreads for liquidity quality monitoring',
        'lab_status_na': '❓ N/A',
        'lab_status_good': '🟢 Good',
        'lab_status_normal': '🟡 Normal',
        'lab_status_warning': '🔴 Warning',
        'lab_spreads_no_data': 'Spread data could not be retrieved',
        
        # --- Analysis Lab Explanations ---
        'lab_glp_explanation': '''**Global Liquidity Proxy** estimates the amount of money flowing in global financial markets.

**Formula**: `Fed Assets + ECB Assets (USD converted) - TGA - RRP`

| Component | Description |
|------|------|
| **Fed Assets** | US central bank balance sheet (increases with QE) |
| **ECB Assets** | European central bank balance sheet (EUR→USD converted) |
| **TGA** | Treasury General Account (high = absorbing from market) |
| **RRP** | Overnight Reverse Repo (high = absorbing from market) |

**Interpretation**:
- 📈 **GLP Rising** = Liquidity increasing → Tailwind for stocks/BTC
- 📉 **GLP Falling** = Liquidity tightening → Headwind for risk assets''',
        'lab_m2v_explanation': '''**M2 Velocity** indicates how much money is "circulating" in the economy.

**Formula**: `Nominal GDP ÷ M2 Money Supply`

**Interpretation**:
- 📉 **Declining** = Money is stagnant (increasing savings, declining consumption) → Deflation pressure
- 📈 **Rising** = Money is circulating actively (active consumption) → Inflation pressure''',
        'lab_fsi_explanation': '''**Financial Stress Index** is published by the St. Louis Fed to measure the "tension level" of financial markets.

**Thresholds**:
| Value | State | Meaning |
|----|------|------|
| **< -0.5** | 🟢 Loose | Risk-on environment, favorable for investment |
| **-0.5 to 0.5** | 🟡 Normal | Normal market conditions |
| **0.5 to 1.5** | 🟠 Caution | Stress rising, be cautious |
| **> 1.5** | 🔴 Crisis | Financial crisis level |''',
        
        # --- Currency Lab Page ---
        'currency_lab_title': '💱 Currency Comparison Lab',
        'currency_lab_subtitle': 'Compare currencies in Gold, BTC, and USD denominations',
        'currency_lab_settings': '🎛️ Currency Lab Settings',
        'currency_lab_period': '📅 Display Period',
        'currency_lab_normalize': '📏 Normalize (Base=100)',
        'currency_lab_gold_section': '🥇 Gold-denominated Currencies',
        'currency_lab_gold_desc': '💡 Index how much Gold 1 oz costs in each currency (Base=100). Rising = Currency depreciation',
        'currency_lab_gold_meaning_title': '📖 What does Gold-denominated mean?',
        'currency_lab_gold_meaning': '''**Gold-denominated** measures each currency's purchasing power in terms of Gold.

- **Rising** → Gold costs more in that currency = Currency purchasing power decreased
- **Falling** → Gold costs less in that currency = Currency purchasing power increased

All fiat currencies tend to lose value against Gold over the long term.''',
        'currency_lab_select_gold': '🪙 Select currencies to display',
        'currency_lab_select_hint': '👆 Please select currencies',
        'currency_lab_btc_section': '₿ BTC-denominated Currencies',
        'currency_lab_btc_desc': '💡 Index how much 1 BTC costs in each currency. Spike = Reflects BTC crash',
        'currency_lab_btc_meaning_title': '📖 What does BTC-denominated mean?',
        'currency_lab_btc_meaning': '''**BTC-denominated** measures each currency's purchasing power in terms of Bitcoin.

- **Rising** → BTC costs more in that currency = Currency purchasing power decreased (BTC surged)
- **Falling** → BTC costs less in that currency = Currency purchasing power increased (BTC dropped)

More volatile than Gold, reflecting short-term market sentiment.''',
        'currency_lab_select_btc': '₿ Select currencies to display',
        'currency_lab_usd_section': '💵 USD-denominated (FX & Assets)',
        'currency_lab_usd_desc': '💡 Traditional FX pairs and major asset USD prices',
        'currency_lab_usd_meaning_title': '📖 What does USD-denominated mean?',
        'currency_lab_usd_meaning': '''**USD-denominated** shows traditional exchange rates and asset prices.

- **USD/JPY rising** → Yen weakening, Dollar strengthening
- **EUR/USD rising** → Euro strengthening, Dollar weakening
- **BTC/USD rising** → Bitcoin rising

Compare different asset types on the same currency basis.''',
        'currency_lab_select_usd': '💵 Select pairs to display',
        'currency_lab_cross_section': '🔀 Cross Comparison',
        'currency_lab_cross_desc': '💡 Compare same currency in Gold vs BTC denomination',
        'currency_lab_cross_meaning_title': '📖 What does Cross Comparison mean?',
        'currency_lab_cross_meaning': '''**Comparing the same currency in Gold vs BTC denomination** reveals:

- Both falling → That currency is strong
- Both rising → That currency is weak
- Only Gold-denominated rising → Gold rally (Inflation concerns?)
- Only BTC-denominated rising → BTC rally (Risk-on?)

Visualize differences between traditional assets (Gold) and digital assets (BTC).''',
        'currency_lab_select_cross': '🌍 Select currency to compare',
        'currency_lab_btc_vs_gold': 'BTC vs Gold',
        'currency_lab_insufficient_data': 'Insufficient data',
        'currency_lab_tip': '💡 **Tip**: Switch period and normalization in sidebar for different analysis perspectives',
        
        # --- Multi-Region Spread Monitor ---
        'market_hours_reference': 'Market Hours Reference',
        'region': 'Region',
        'market_hours_local': 'Hours (Local Time)',
        
        # --- AI Category Reports ---
        'ai_category_reports': '📊 Category Reports',
        'ai_category_reports_desc': 'Deep-dive analysis with web search for each category',
        'ai_select_category': 'Select a category for specialized analysis:',
        'ai_generating_report': '🔍 Generating {category} report with web search...',
        'ai_report_generated': '📋 {category} Report',
        'ai_web_search_note': '💡 This report includes latest information via Gemini web search',
        
        # --- Data Frequency Labels ---
        'freq_daily': 'Daily',
        'freq_weekly': 'Weekly',
        'freq_monthly': 'Monthly',
        'freq_quarterly': 'Quarterly',
    },
    
    'ja': {
        # --- US M2 Description ---
        'us_m2_desc': '💡 米国のマネーサプライ - FREDから自動取得',
        'm2_nominal_notes': '名目M2',
        'm2_real_notes': '実質M2 (1982-84基準)',
        
        # --- Time Difference Strings ---
        'time_unknown': '不明',
        'time_just_now': 'たった今',
        'time_minutes_ago': '{n}分前',
        'time_hours_ago': '{n}時間前',
        'time_days_ago': '{n}日前',
        
        # --- App Title & Navigation ---
        'app_title': 'Market Cockpit Pro',
        'app_subtitle': '更新間隔: 10分 | ソース: FRED, Yahoo Finance, DeFiLlama, Alternative.me',
        
        # --- Sidebar ---
        'sidebar_force_update': '🔄 強制更新',
        'sidebar_download_csv': '📥 CSV ダウンロード',
        'sidebar_update_status': '🔄 更新ステータス',
        'sidebar_fresh': '🟢 最新',
        'sidebar_stale': '🟡 古い',
        'sidebar_critical_warning': '🔴 {count} 件が期限切れ',
        'sidebar_health_score': 'ヘルススコア: {score}%',
        'sidebar_alerts': '⚠️ アラート',
        'sidebar_no_alerts': '✅ 重大なアラートなし',
        
        # --- Alert Messages ---
        'alert_vix_high': '⚠️ VIXが{value}に上昇 - 市場の恐怖が高まっています',
        'alert_vix_medium': '📊 VIXが{value}に上昇 - 注意が必要です',
        'alert_reserves_low': '⚠️ 銀行準備金が{value}Bに低下 - 流動性逈迫リスク',
        'alert_on_rrp_depleted': '🔴 ON RRPが{value}Bに枯渇 - 余剰流動性が消滅',
        'alert_credit_spread_wide': '⚠️ クレジットスプレッドが{value}%に拡大 - 信用リスク上昇',
        'alert_yield_curve_inverted': '⚠️ イールドカーブ逆転中 ({value}%) - リセッション警告',
        'alert_primary_credit_surge': '🔴 ディスカウントウィンドウ利用急増 ({value}B) - 銀行流動性危機の兆候',
        
        'sidebar_ai_status': '🤖 AIステータス',
        'sidebar_ready': '✅ 準備完了',
        'sidebar_not_configured': '❌ 未設定',
        'sidebar_last_update': '最終更新: {date}',
        'sidebar_data_sources': 'データソース: FRED, Yahoo Finance, DeFiLlama, Alternative.me',
        'back_to_top': 'トップへ戻る',
        
        # --- Page Titles ---
        'page_liquidity': '📊 流動性 & 金利',
        'page_global_money': '🌏 グローバルマネー & FX',
        'page_us_economic': '📈 米国経済指標',
        'page_crypto': '🪙 暗号資産流動性',
        'page_ai_analysis': '🤖 AI分析',
        'page_monte_carlo': '🎲 モンテカルロ',
        'page_market_voices': '📰 マーケットボイス',
        'page_sentiment': '🎭 市場センチメント',
        'page_banking': '🏦 銀行セクター',
        'page_analysis_lab': '🧪 分析ラボ',
        'page_currency_lab': '💱 通貨ラボ',
        
        # --- Common Labels ---
        'loading': '読み込み中...',
        'no_data': 'データなし',
        'error_data_not_loaded': 'データが読み込まれていません。main.pyから起動してください。',
        'source_update_date': '🔄 提供元更新: {date}',
        'long_term_trend': '長期推移 (2年)',
        'vs_avg': '平均比',
        
        # --- Data Labels (charts.py) ---
        'data_period': 'データ期間',
        'data_date': 'データ日付',
        'source_update': '提供元更新日',
        'sparkline_label': '60日推移',
        'mom': '前月比',
        'yoy': '前年比',
        
        # --- Liquidity Page ---
        'liquidity_title': '🏦 流動性 & Fed',
        'valuation_leverage': '📊 バリュエーション & レバレッジ指標',
        'valuation_leverage_desc': '市場の過熱感とレバレッジ状況を一目で確認',
        'net_liquidity': 'Net Liquidity',
        'net_liquidity_notes': '市場の真の燃料',
        'net_liquidity_chart_title': 'Net Liquidity vs S&P 500 (2年)',
        'on_rrp': 'ON RRP',
        'on_rrp_notes': '余剰準備金',
        'reserves': 'Reserves',
        'reserves_notes': '銀行準備預金',
        'tga': 'TGA',
        'tga_notes': '政府口座',
        'market_plumbing': '🔧 市場配管 (Repo & 流動性)',
        'srf': 'SRF',
        'srf_notes': '国内レポ市場',
        'fima': 'FIMA',
        'fima_notes': '海外ドル流動性',
        'sofr': 'SOFR',
        'sofr_notes': '担保付翌日物金利',
        'effr_iorb': 'EFFR - IORB',
        'effr_iorb_notes': 'Fed準備金状況',
        'fed_balance_sheet': '🏛️ Fedバランスシート (SOMA)',
        'rmp_status': '📊 RMPステータス',
        'soma_composition': 'SOMA構成 (総額 & 国債)',
        'soma_total': 'SOMA 総額',
        'soma_total_notes': '保有総額',
        'soma_treasury': 'SOMA 国債',
        'soma_treasury_notes': '国債保有総額',
        'soma_bills': 'SOMA 短期国債',
        'soma_bills_notes': 'T-Bills保有量（RMP核心指標）',
        'treasury_share': '国債比率',
        'treasury_share_notes': '国債保有比率',
        
        # --- RMP Status ---
        'rmp_monitoring': '📊 RMP監視 (2025年12月12日開始)',
        'rmp_active': '✅ RMP稼働中: +${value}B/週 (目標ペース)',
        'rmp_accelerating': '⚠️ RMP加速中: +${value}B/週 (通常ペース超過!)',
        'rmp_slowing': '🔄 RMP減速中: +${value}B/週 (ペース低下)',
        'rmp_selling': '⛔ Bills売却: ${value}B/週 (RMP停止?)',
        
        'emergency_loans': '🚨 緊急融資 (Discount Window)',
        'total_loans': '融資総額',
        'total_loans_notes': '緊急融資合計',
        'primary_credit': 'Primary Credit',
        'primary_credit_notes': '健全銀行向け',
        'risk_bonds': '⚠️ リスク & 債券',
        'risk_bonds_desc': '💡 市場リスクと債券市場の動向を監視',
        'vix_index': 'VIX指数',
        'vix_notes': '恐怖指数',
        'credit_spread': 'クレジットスプレッド',
        'credit_spread_notes': 'ジャンク債スプレッド',
        'us_10y_yield': '米10年金利',
        'us_10y_notes': '長期金利',
        
        # --- Valuation & Leverage ---
        'sp500_pe': 'S&P 500 P/E',
        'sp500_pe_help': '歴史的平均は約19.5。25超=過熱、15未満=割安',
        'nasdaq_pe': 'NASDAQ P/E (QQQ)',
        'nasdaq_pe_help': 'ハイテク株のバリュエーション指標',
        'btc_funding_rate': 'BTC Funding Rate',
        'long_heavy': 'ロング過多',
        'short_heavy': 'ショート過多',
        'neutral': '中立',
        'funding_rate_help': 'Funding Rate > 0.1% = ロング過重 (過熱)。< -0.1% = ショート過重',
        'btc_ls_ratio': 'BTC Long/Short比率',
        'long_biased': 'ロング優勢',
        'short_biased': 'ショート優勢',
        'balanced': 'バランス',
        'ls_ratio_help': 'Long/Shortのアカウント比率。1.0 = 均衡',
        
        # --- Open Interest ---
        'open_interest_title': '📈 Open Interest (レバレッジ蓄積)',
        'btc_open_interest': 'BTC建玉',
        'eth_open_interest': 'ETH建玉',
        'danger_zone': '危険ゾーン',
        'elevated': '高め',
        'low': '低',
        'normal': '正常',
        'vs_30d_avg': '30日平均比',
        'ath_ratio': '30日高値比',
        'status': 'ステータス',
        'source': 'ソース',
        'accumulating_data': '📈 データ蓄積中 ({days}/7日) - Hyperliquid (DEX)',
        'open_interest_guide': '''
💡 **Open Interestの読み方**
- **30日平均+20%以上** 🔴: レバレッジ過剰 → ロスカット連鎖リスク大
- **30日平均±5%** 🟢: 正常範囲
- **ソース**: Hyperliquid (DEX) - 分散取引所データを自動蓄積
- **蓄積期間**: 7日後から比較可能、30日後でフル機能
''',
        
        # --- Global Money Page ---
        'global_money_title': '🌏 グローバルマネーサプライ & FX',
        'global_m2': 'グローバルM2供給量',
        'global_m2_desc': '主要経済圏のグローバル流動性トレンドを追跡',
        'us_m2': '米国 M2',
        'china_m2': '中国 M2',
        'japan_m2': '日本 M2',
        'eu_m2': 'EU M2',
        'fx_rates': '💱 為替レート',
        'dxy': 'DXY (ドル指数)',
        'usdjpy': 'USD/JPY',
        'eurusd': 'EUR/USD',
        
        # --- US Economic Page ---
        'us_economic_title': '📈 米国経済指標',
        'employment': '👷 雇用',
        'nfp': '非農業部門雇用者数',
        'nfp_notes': '月間雇用創出',
        'adp': 'ADP雇用統計',
        'adp_notes': '民間雇用',
        'unemployment': '失業率',
        'unemployment_notes': 'U-3失業率',
        'jolts': 'JOLTS求人件数',
        'jolts_notes': '労働需要',
        'icsa': '新規失業保険申請件数',
        'icsa_notes': '週間失業申請',
        'inflation': '📊 インフレ',
        'cpi': 'CPI',
        'cpi_notes': '消費者物価(前年比)',
        'core_cpi': 'コアCPI',
        'core_cpi_notes': '食品・エネルギー除く',
        'michigan_inflation_title': 'ミシガン大学期待インフレ率（1年先）',
        'michigan_inflation_label': 'ミシガン大学期待インフレ率',
        'michigan_inflation_desc': '💡 消費者のインフレ予想調査 - Fedが注視する重要指標',
        'michigan_inflation_notes': '1年先の予想インフレ率',
        'fed_target': 'Fed目標 2%',
        'ppi': 'PPI',
        'ppi_notes': '生産者物価',
        'core_pce': 'コアPCE',
        'core_pce_label': 'コアPCE物価指数',
        'core_pce_notes': 'Fedの重視指標',
        'economy': '🏭 経済',
        'retail_sales': '小売売上高',
        'retail_sales_notes': '消費支出',
        'gdp': '実質GDP',
        'gdp_notes': '四半期成長率',
        'consumer_sentiment': '消費者信頼感',
        'consumer_sentiment_notes': 'ミシガン大調査',
        'yield_curve': 'イールドカーブ (10Y-2Y)',
        'yield_curve_notes': '景気後退指標',
        
        # --- Crypto Page ---
        'crypto_title': '🪙 暗号資産流動性 & ステーブルコイン',
        'stablecoins': '💵 ステーブルコイン供給量',
        'stablecoin_desc': '暗号資産市場の流動性代理指標',
        'usdt': 'USDT (Tether)',
        'usdc': 'USDC (Circle)',
        'dai': 'DAI',
        'fear_greed': '😱 Fear & Greed指数',
        'extreme_fear': '極度の恐怖',
        'fear': '恐怖',
        'greed': '貪欲',
        'extreme_greed': '極度の貪欲',
        
        # --- AI Analysis Page ---
        'ai_analysis_title': '🤖 AIマーケット分析',
        'ai_analysis_desc': 'AI搭載のマーケットコメンタリーと洞察',
        'generate_analysis': '🔮 分析を生成',
        'generating': '生成中...',
        'gemini_analysis': '🌟 Gemini分析',
        'claude_analysis': '🤖 Claude分析',
        
        # --- Monte Carlo Page ---
        'monte_carlo_title': '🎲 モンテカルロシミュレーション',
        'monte_carlo_desc': '複数の分布モデルによる価格パスシミュレーション',
        'simulation_params': 'シミュレーションパラメータ',
        'initial_price': '初期価格 ($)',
        'days': '日数',
        'simulations': 'シミュレーション回数',
        'volatility': '年間ボラティリティ (%)',
        'drift': '年間ドリフト (%)',
        'distribution': '分布モデル',
        'student_t': 'Student-t (ファットテール)',
        'jump_diffusion': 'ジャンプ拡散',
        'run_simulation': '▶️ シミュレーション実行',
        'results': '結果',
        'median_price': '最終価格中央値',
        'percentile_5': '5パーセンタイル',
        'percentile_95': '95パーセンタイル',
        
        # --- Market Voices Page ---
        'market_voices_title': '📰 マーケットボイス',
        'primary_sources': '🔍 一次情報ハンター',
        'primary_sources_desc': '政府・中央銀行の一次情報を検索',
        'search_keyword': '検索キーワード',
        'search_mode': '検索モード',
        'mode_primary': '一次情報 (Pro)',
        'mode_general': '一般ニュース',
        'context_select': 'コンテキスト選択',
        'search_button': '🔎 一次情報を検索',
        
        # --- Sentiment Page ---
        'sentiment_title': '🎭 市場センチメント',
        'sentiment_desc': '投資家心理指標',
        'crypto_fear_greed': '暗号資産 Fear & Greed',
        'cnn_fear_greed': 'CNN Fear & Greed',
        'aaii_sentiment': 'AAII投資家センチメント',
        'put_call_ratio': 'Put/Callレシオ',
        'bullish': '強気',
        'bearish': '弱気',
        'bull_bear_spread': '強気弱気スプレッド',
        
        # --- Banking Page ---
        'banking_title': '🏦 銀行セクターの健全性',
        'lending_standards': '貸出基準',
        'ci_lending': 'C&I貸出基準',
        'cre_lending': 'CRE貸出基準',
        'bank_deposits': '銀行預金',
        'small_bank_deposits': '中小銀行預金',
        'delinquency': '延滞率',
        'cc_delinquency': 'クレジットカード延滞率',
        
        # --- Analysis Lab Page ---
        'analysis_lab_title': '🧪 マーケット分析ラボ',
        'analysis_lab_desc': '高度なマーケット分析ツール',
        
        # --- Global Money Page Extended ---
        'global_money_subtitle': '💡 グローバル流動性、為替、コモディティ、暗号資産のトレンド',
        'global_m2_total': '🌍 グローバルM2総額 (真の総額)',
        'formula': '計算式: US + CN(USD) + JP(USD) + EU(USD)',
        'vs_prior': '前回比',
        'global_liquidity_proxy': '🌊 グローバル流動性プロキシ (Fed + ECB)',
        'global_liquidity_desc': '💡 Fed資産 + ECB資産 (USD)。市場感応度の高い流動性指標。',
        'daily_change': '日次変化',
        'trend_ytd': '推移 (YTD)',
        'yoy_growth': '前年比成長率 (%)',
        'yoy_growth_desc': '💡 前年同期比の変化トレンド',
        'liquidity_expanding': '🟢 流動性拡大中',
        'liquidity_contracting': '🔴 流動性縮小中',
        'insufficient_data_yoy': '前年比計算にはデータ不足 (252日以上必要)',
        'regional_m2': '💵 地域別M2内訳',
        'manual_update': '手動更新',
        'auto_fetch_unavail': '⚠️ 自動取得不可',
        'announced_by': '発表元',
        'nominal': '名目',
        'real': '実質',
        'cpi_adjusted': 'CPI {cpi}% 調整済',
        'credit_impulse': '📊 クレジットインパルス',
        'credit_impulse_desc': '⚠️ 代理指標: FRED経由のBIS四半期信用データ (CRDQCNAPABIS)',
        'credit_impulse_notes': '(信用フロー変化/GDP)',
        'long_term_5y': '長期推移 (5年)',
        'fx_section': '💱 外国為替',
        'dollar_index': 'ドル指数',
        'dollar_strength': 'ドルの強さ指標',
        'yen_carry': '円キャリー',
        'euro_dollar': 'ユーロドル',
        'yuan': '人民元',
        'global_indices': '📈 グローバル株価指数',
        'global_indices_desc': '💡 主要株価指数',
        'nikkei_notes': '日経225指数',
        'sp500_notes': '米国大型株指数',
        'commodities_section': '🛢️ コモディティ',
        'gold_futures': '金先物',
        'silver_futures': '銀先物',
        'oil_futures': '原油先物',
        'copper_futures': '銅先物 (先行指標)',
        'crypto_section': '🪙 暗号資産',
        'risk_on_indicator': 'リスクオン指標',
        'defi_base': 'DeFiベース',
        
        # --- Fiat Health Monitor ---
        'fiat_health_subtitle': '💡 不換紙幣の購買力低下を可視化（Gold/BTC建て）',
        'fiat_gold_denominated': '🥇 Gold建て通貨価値',
        'fiat_decline_note': '↓下落 = 通貨の購買力低下（2年前=100）',
        'fiat_btc_denominated': '₿ BTC建て通貨価値',
        'fiat_gold_btc': '🥇₿ Gold建てBTC',
        'fiat_btc_gold_oz': '1 BTCで何ozのGoldが買えるか',
        'fiat_health_no_data': '⚠️ Fiat Health Monitor: データが不足しています',
        
        # --- Crypto Page Extended ---
        'crypto_subtitle': '💡 暗号資産市場の流動性とRWA (実物資産) トークン化のトレンド',
        'stablecoin_section': '💵 ステーブルコイン供給量',
        'total_stablecoin': 'ステーブルコイン総供給量',
        'stablecoin_total_help': '全ステーブルコインの総供給量',
        'stablecoin_history': '📈 ステーブルコイン供給量推移',
        'short_term': '短期 (90日)',
        'long_term_all': '長期 (全期間)',
        'top_stablecoins': 'トップ10ステーブルコイン (供給量順)',
        'supply_distribution': '供給量分布',
        'last_update': '📅 最終更新',
        'stablecoin_fetch_failed': '⚠️ ステーブルコインデータの取得に失敗しました。',
        'tokenized_treasury': '📜 トークン化国債',
        'treasury_tvl': '国債TVL',
        'treasury_help': 'トークン化米国債',
        'tokenized_gold': '🪙 トークン化ゴールド',
        'gold_tvl': 'ゴールドTVL',
        'gold_help': 'トークン化された金',
        'other_rwa': '🏢 その他RWA',
        'other_rwa_tvl': 'その他RWA TVL',
        'other_rwa_help': 'その他の実物資産',
        'tokenized_us_treasury': '📜 トークン化米国債',
        'rwa_fetch_failed': '⚠️ RWAデータの取得に失敗しました。',
        'market_depth': '💧 市場深度 (流動性品質)',
        'market_depth_desc': '中央集権型 (CEX) vs 分散型 (DEX) 流動性コスト',
        'avg_cex_spread': '平均CEXスプレッド',
        'avg_dex_spread': '平均DEXスプレッド',
        'higher_cost': '{ratio}倍高コスト',
        'market_depth_unavail': '市場深度データ利用不可 (CoinGecko APIリミットまたはタイムアウト)',
        'market_depth_chart_title': 'Bid-Askスプレッド (%) 比較',
        'crypto_why_important': '''
💡 **なぜこれが重要か**
- **ステーブルコイン**: 暗号資産市場への資金流入/流出を測定
- **トークン化国債**: 機関投資家参入の指標
- **トークン化ゴールド**: 従来のセーフヘイブン資産のデジタル化
''',
        
        # --- US Economic Page Extended ---
        'us_economic_page_title': '📈 米国経済指標',
        'us_economic_section_rates': '🏦 1. 金利',
        'ff_upper': 'FF誘導目標 (上限)',
        'ff_upper_label': 'FF金利（上限）',
        'effr_label': 'EFFR',
        'sofr_label': 'SOFR',
        'ff_upper_notes': '政策金利上限',
        'ff_lower': 'FF誘導目標 (下限)',
        'ff_lower_notes': '政策金利下限',
        'effr_notes': '実効FF金利',
        'sofr_notes_full': '担保付金利 (レポ市場)',
        'us_economic_section_employment': '👷 2. 雇用',
        'jolts_title': 'JOLTS求人件数',
        'jolts_label': 'JOLTS求人労働異動調査',
        'nfp_title': '非農業部門雇用者数 (前月比)',
        'result': '結果',
        'thousand_people': '千人 ({val:.1f}万人)',
        'nfp_monthly_change': 'NFP月次変化トレンド',
        'unemployment_rate': '失業率',
        'vs_last_month': '先月比',
        'avg_hourly_earnings': '平均時給',
        'icsa_title': '新規失業保険申請件数 (ICSA)',
        'latest_week': '最新週',
        'vs_last_week': '先週比',
        'us_economic_section_inflation': '⚖️ 3. インフレ',
        'cpi_title': '消費者物価指数 (CPI)',
        'core_cpi_title': 'コアCPI',
        'ppi_title': '生産者物価指数 (PPI)',
        'cpi_notes_full': '消費者物価指数',
        'core_pce_title': 'コアPCEインフレ (前年比)',
        'current_inflation': '現在のインフレ率',
        'ppi_notes_full': '生産者物価指数',
        'us_economic_section_economy': '📈 4. 経済',
        'retail_sales_title': '小売売上高',
        'consumer_sentiment_title': 'ミシガン大学消費者信頼感指数',
        'gdp_label': '実質GDP',
        'gdp_title': '実質GDP (年率換算成長率)',
        'qoq_annualized': '前期比年率',
        'level': '水準',
        'yield_curve_title': '🔗 イールドカーブ (2Y-10Y)',
        'yield_curve_label': '2Y-10Yスプレッド',
        'inversion_boundary': '逆イールド境界',
        
        # --- US Economic Page: Leading & Housing (2026-01-22 added) ---
        'us_economic_section_leading': '先行指標',
        'leading_indicators_desc': '💡 景気サイクル予測のための先行指標',
        'ism_pmi_notes': '製造業の健全性（50以上=拡大）',
        'expansion_contraction_boundary': '拡大/縮小の境界',
        'leading_index_title': 'シカゴ連銀景気指数',
        'leading_index_label': 'シカゴ連銀CFNAI',
        'leading_index_notes': 'シカゴ連銀CFNAI（3ヶ月移動平均）経済活動の先行指標、0超=拡大/0未満=減速',
        'zero_line': 'ゼロライン',
        'us_economic_section_housing': '住宅',
        'housing_indicators_desc': '💡 住宅市場の先行指標',
        'housing_starts_title': '住宅着工件数',
        'housing_starts_label': '住宅着工件数',
        'housing_starts_notes': '新規住宅建設（年率換算、千戸）',
        'building_permits_title': '建築許可件数',
        'building_permits_label': '建築許可件数',
        'building_permits_notes': '許可済み建築件数（年率換算、千戸）',
        
        # --- AI Analysis Page Extended ---
        'ai_data_count': 'AI監視中: {ai_count} / {total_count}',
        'ai_data_excluded': '⚠️ {count} 件がAI分析から除外',
        'ai_all_monitored': '✅ 全データ監視中',
        'ai_collecting_data': '📊 市場データ収集中...',
        'ai_settings': '⚙️ 分析設定',
        'ai_select': 'AI選択',
        'ai_focus_areas': '🎯 注目領域',
        'ai_focus_prompt': 'AIに注目させる項目',
        'ai_focus_liquidity': '流動性 (配管)',
        'ai_focus_inflation': 'インフレ & 金利',
        'ai_focus_employment': '雇用 & 景気後退',
        'ai_focus_banking': '銀行 & 信用危機',
        'ai_focus_geopolitics': '地政学 & コモディティ',
        'ai_focus_crypto': '暗号資産',
        'ai_full_analysis': '🚀 フルマーケット分析',
        'ai_gemini_analyzing': '🔷 Gemini 3 Flash 分析中...',
        'ai_claude_analyzing': '🟣 Claude 4.5 Opus 分析中...',
        'ai_custom_analysis': '🎯 カスタム分析',
        'ai_custom_prompt': '何に注目しますか？',
        'ai_custom_placeholder': '例: ON RRPのトレンドと株式市場を比較',
        'ai_run_custom': '🔍 カスタム分析を実行',
        'ai_search_news': '📰 最新ニュースを検索',
        'ai_search_placeholder': '例: Fed利下げ',
        'ai_search_button': '🔎 ニュース検索',
        'ai_policy_context': '''あなたは伝説的なグローバル・マクロ・ストラテジストです。
単なるニュースの要約ではなく、データの背後にある「配管（Plumbing）」、つまり流動性の動きと市場参加者のインセンティブを分析します。''',
        'ai_response_language': '重要: 必ず日本語で回答してください。',
        'ai_analysis_instruction': '以下の市場データを構造的に分析してください:',
        
        # --- Monte Carlo Page Extended ---
        'mc_title': '🎲 モンテカルロシミュレーション',
        'mc_subtitle': '💡 複数の分布モデルによる価格パスシミュレーション',
        'mc_settings': '⚙️ 設定',
        'mc_asset': '資産',
        'mc_period_days': '予測期間 (日)',
        'mc_simulations': 'シミュレーション回数',
        'mc_model': '分布モデル',
        'mc_model_normal': '正規分布 (ガウス)',
        'mc_model_t': 'Student-t (ファットテール)',
        'mc_model_jump': 'ジャンプ拡散 (Merton)',
        'mc_run': '▶️ シミュレーション実行',
        'mc_running': '🔄 シミュレーション実行中...',
        'mc_results': '📊 結果',
        'mc_expected_price': '期待価格 (中央値)',
        'mc_bullish': '強気 (90%)',
        'mc_bearish': '弱気 (10%)',
        'mc_var_95': 'VaR 95%',
        'mc_evt_var_99': 'EVT VaR 99%',
        'mc_var_ci': 'VaR 95% 信頼区間',
        'mc_regime': '市場レジーム',
        'mc_jump_freq': 'ジャンプ頻度',
        'mc_regime_high_vol': '🔥 高ボラティリティ',
        'mc_regime_low_vol': '❄️ 低ボラティリティ',
        'mc_regime_normal': '📊 通常',
        'mc_regime_unknown': '不明',
        'mc_advanced': '📊 高度な分析',
        'mc_vol_regime': 'ボラティリティレジーム',
        'mc_evt_analysis': '極値理論 (EVT)',
        'mc_fat_tails': 'ファットテールリスク',
        'mc_about': '📖 モンテカルロシミュレーションについて',
        'mc_disclaimer': '⚠️ これは投資アドバイスではありません。過去のデータシミュレーションは将来の結果を保証しません。',
        'mc_x_template': '📱 X/Twitterにコピー',
        'mc_generate_x': '🐦 Xポストを生成',
        'mc_preset_assets': 'プリセット資産',
        'mc_custom_ticker': 'カスタムティッカー',
        'mc_custom_placeholder': '例: AAPL, 7203.T, ETH-USD',
        'mc_custom_help': 'yfinanceティッカーをカンマ区切りで入力',
        'mc_distribution': '分布',
        'mc_dist_help': '正規: 標準GBM。Student-t: ファットテール対応。ジャンプ拡散: ブラックスワンイベント。',
        'mc_parameters': '📊 パラメータ',
        'mc_period_years': '予測期間 (年)',
        'mc_trials': '試行回数',
        'mc_market_regime': '市場レジーム',
        'mc_analysis_of': '📊 {asset} ({ticker}) 分析',
        'mc_fetch_failed': 'データ取得失敗: {ticker}',
        'mc_bullish_label': '**強気 (上位10%):**',
        'mc_bearish_label': '**弱気 (下位10%):**',
        'mc_risk_metrics': '🛡 **リスク指標**',
        'mc_var_ci_label': 'VaR 95% CI: [{lower:.2f}%, {upper:.2f}%]',
        'mc_historical_stats': '📊 **過去の統計**',
        'mc_annualized_return': '**年率リターン:**',
        'mc_annualized_vol': '**年率ボラティリティ:**',
        'mc_df_estimated': '**自由度 (推定):**',
        'mc_df_note': '低いDF = よりファットなテール (より変動的)',
        'mc_jump_avg': '平均ジャンプ: {avg:.1f}%',
        'mc_welcome_title': '### 🎲 モンテカルロシミュレーションへようこそ',
        'mc_welcome_intro': 'このページでは**金融工学ベース**の資産価格シミュレーションを提供します。',
        'mc_model_guide_title': '**🎯 モデル選択ガイド (推奨):**',
        'mc_model_table': '''| モデル | 使用場面 | 対象資産 |
|--------|--------------|-------|
| **正規分布** ⭐推奨 | 通常の予測 / 初心者 | 株式、指数 |
| **Student-t** | 暴落リスクを考慮したい | 高ボラティリティ資産 |
| **ジャンプ拡散** | 最悪シナリオを見たい | 暗号資産、新興国市場 |''',
        'mc_model_tip': '💡 **迷ったら正規分布でOK。** Student-tとジャンプ拡散はより悲観的な予測になります。',
        'mc_tech_title': '**実装テクニック (8つのコア手法):**',
        'mc_tech_list': '''- 分散削減 (対称変量法)
- 分布モデル (正規分布、Student-t、ジャンプ拡散)
- リスク分析 (VaR、CVaR、EVT、ブートストラップ)
- 市場分析 (レジーム検出、ジャンプパラメータ推定)''',
        'mc_disclaimer_title': '⚠️ **免責事項:**',
        'mc_disclaimer_list': '''- このアプリの出力は**投資アドバイスではありません**
- 過去データのシミュレーションに基づき、**将来の結果を保証しません**
- 投資判断は**自己責任**で行ってください''',
        'mc_start_instruction': '👆 上の設定から資産を選択してシミュレーションを開始。',
        
        # --- Market Voices Page Extended ---
        'mv_subtitle': '💡 Fed/財務省/主要中央銀行からの一次情報 - AI解釈なし',
        'mv_direct_links': '🏛️ 主要機関への直接リンク',
        'mv_us': '🇺🇸 米国',
        'mv_overseas': '🌍 海外中央銀行',
        'mv_rss_feeds': '📡 リアルタイムRSSフィード',
        'mv_no_articles': '📭 記事が見つかりません',
        'mv_error_feed': '⚠️ フィード取得エラー',
        'mv_ecb': 'ECB (欧州中央銀行)',
        'mv_boj': 'BOJ (日本銀行)',
        'mv_boe': 'BOE (イングランド銀行)',
        'mv_pboc': 'PBoC (中国人民銀行)',
        'mv_guide_title': '📚 情報ソースの読み方',
        'mv_guide_content': '''### 一次情報 vs 二次情報

| タイプ | 例 | 信頼性 |
|------|-----|--------|
| **一次情報** | Fed声明、議事録、統計データ | ⭐⭐⭐ |
| 二次情報 | ロイター、ブルームバーグ記事 | ⭐⭐ |
| 三次情報 | SNS、個人ブログ | ⭐ |

### Fedウォッチの要点

- **FOMC声明**: 政策金利と今後の方向性
- **議事録**: 3週間後に公開、委員会の詳細な議論
- **SEP (経済予測)**: ドットプロット = 委員のレート予想
- **パウエル記者会見**: 声明の"行間を読む"

### 注意事項

⚠️ ヘッドラインだけで判断しない  
⚠️ "関係者によると"は未確認情報  
⚠️ 市場の反応 ≠ 正しい解釈
''',
        'mv_footer': '💬 このページはリンク集です。分析と解釈はあなた次第。',
        
        # --- Sentiment Page Extended ---
        'sent_subtitle': '💡 市場心理を一目で - Fear & Greed、Put/Callレシオ、投資家センチメント',
        'sent_fg_section': '🎯 Fear & Greed指数',
        'sent_cnn_fg': '📈 CNN Fear & Greed (株式)',
        'sent_crypto_fg': '₿ 暗号資産 Fear & Greed',
        'sent_vix': '📊 VIX指数 (恐怖指数)',
        'sent_extreme_fear': '極度の恐怖',
        'sent_fear': '恐怖',
        'sent_neutral': '中立',
        'sent_greed': '貪欲',
        'sent_extreme_greed': '極度の貪欲',
        'sent_30d_trend': '📊 30日推移',
        'sent_cnn_unavail': '📊 CNN Fear & Greed 現在利用不可 (APIリミット)',
        'sent_aaii_section': '📊 AAII投資家センチメント',
        'sent_aaii_desc': '米国個人投資家センチメント調査 (週次)',
        'sent_aaii_bullish': '強気',
        'sent_aaii_bearish': '弱気',
        'sent_aaii_neutral': '中立',
        'sent_bull_bear_spread': '強気弱気スプレッド',
        'sent_bull_bear_extreme': '🔴 極端な強気/弱気',
        'sent_aaii_unavail': '📊 AAIIセンチメントデータ利用不可',
        'sent_put_call_section': '📊 オプション市場 (Put/Callレシオ)',
        'sent_put_call_desc': 'オプション市場のセンチメント指標',
        'sent_put_call_high': '🔴 リスクオフ (ヘッジ過多)',
        'sent_put_call_low': '🟢 リスクオン (油断)',
        'sent_put_call_normal': '🟡 正常範囲',
        'sent_put_call_unavail': '📊 Put/Callレシオデータ利用不可',
        'sent_60d_trend': '📊 60日推移',
        'sent_crypto_error': '⚠️ 暗号資産 Fear & Greed 取得エラー',
        'sent_vix_no_data': '⚠️ VIXデータ利用不可',
        'vix_low': '🟢 低ボラティリティ',
        'vix_normal': '🟡 通常',
        'vix_elevated': '🟠 やや高い',
        'vix_high_fear': '🔴 高い恐怖',
        'sent_aaii_title': '👥 AAII投資家センチメント調査',
        'sent_aaii_contrarian': '個人投資家センチメント調査 (週次) - 逆張り指標として有名',
        'sent_aaii_bullish_label': '🐂 強気',
        'sent_aaii_neutral_label': '😐 中立',
        'sent_aaii_bearish_label': '🐻 弱気',
        'sent_spread_overheated': '(過熱)',
        'sent_spread_somewhat_bullish': '(やや強気)',
        'sent_spread_neutral': '(中立)',
        'sent_spread_somewhat_bearish': '(やや弱気)',
        'sent_spread_bottom_signal': '(底打ちシグナル?)',
        'sent_aaii_update': '🔄 提供元更新: {date} (週次)',
        'sent_distribution': '**センチメント分布:**',
        'sent_category': 'カテゴリ',
        'sent_ratio': '比率',
        'sent_spread_guide_title': '📈 強気弱気スプレッドの読み方',
        'sent_spread_guide': '''**強気弱気スプレッド** = 強気% − 弱気%

| 値 | 意味 | 解釈 |
|-----|------|------|
| **+20%以上** | 強気優勢 | 🔴 過熱 (天井シグナル?) |
| **+10%〜+20%** | やや強気 | 🟠 楽観的 |
| **−10%〜+10%** | 中立 | 🟢 バランス |
| **−10%〜−20%** | やや弱気 | 🟠 悲観的 |
| **−20%以下** | 弱気優勢 | 🔴 底打ちシグナル? |

💡 **逆張り戦略**: 皆が強気の時に天井、弱気の時に底を形成することが多い！
''',
        'sent_aaii_error': '⚠️ AAIIデータ取得エラー',
        'sent_put_call_title': '### 📊 Put/Callレシオ',
        'sent_put_call_subtitle': 'オプション市場の強気弱気度 - 高い=弱気、低い=強気',
        'sent_put_call_preparing': '📝 Put/Callレシオデータソースは準備中です。VIXを代理指標として表示。',
        'sent_put_call_ref': 'VIX (参考): {value:.1f}',
        'sent_guide_section': '### 📚 センチメント指標の読み方',
        'sent_guide_expand': '💡 指標解釈ガイド',
        'sent_guide_content': '''| 指標 | 極度の恐怖 | 恐怖 | 中立 | 貪欲 | 極度の貪欲 |
|------|-----------|------|------|------|-----------|
| **Fear & Greed** | 0-25 | 25-45 | 45-55 | 55-75 | 75-100 |
| **VIX** | >30 | 20-30 | 15-20 | 10-15 | <10 |
| **Put/Call** | >1.2 | 0.9-1.2 | 0.7-0.9 | 0.5-0.7 | <0.5 |

**逆張り戦略のヒント:**
- "極度の恐怖"は買いのチャンスかも
- "極度の貪欲"は利確のシグナルかも
- AAIIが極端に強気の時は注意
''',
        
        # --- Banking Page Extended ---
        'bank_subtitle': '💡 FRB H.8週次データ & SLOOS四半期調査 - 銀行貸出と信用状況',
        'bank_h8_section': '📊 H.8 週次データ',
        'bank_h8_desc': 'FRB発表の全米商業銀行週次集計データ',
        'bank_cash': '銀行現金保有高',
        'bank_cash_notes': '銀行の現金退蔵',
        'bank_ci_loans': 'C&I融資残高',
        'bank_ci_loans_notes': '商工業融資',
        'bank_cre_loans': 'CRE融資残高',
        'bank_cre_loans_notes': '商業用不動産融資',
        'bank_sloos_section': '📋 SLOOS 四半期調査',
        'bank_sloos_desc': 'シニアローンオフィサー意見調査 (四半期)',
        'bank_ci_tightening': 'C&I貸出基準',
        'bank_ci_tightening_notes': 'プラス=引き締め',
        'bank_cre_tightening': 'CRE貸出基準',
        'bank_cre_tightening_notes': 'プラス=引き締め',
        'bank_ci_demand': 'C&I融資需要',
        'bank_ci_demand_notes': 'プラス=需要旺盛',
        'bank_cre_demand': 'CRE融資需要',
        'bank_cre_demand_notes': 'プラス=需要旺盛',
        'bank_deposits_section': '💰 預金 & 延滞',
        'bank_large_deposits': '大銀行預金',
        'bank_small_deposits': '中小銀行預金',
        'bank_cc_delinquency': 'クレジットカード延滞率',
        
        # --- Banking Page: H.8 Consumer & Deposits ---
        'bank_h8_consumer': '💳 H.8 消費者向け & 預金',
        'bank_credit_card': 'クレジットカード融資',
        'bank_credit_card_notes': '消費者信用の強さ',
        'bank_consumer_loans': '消費者ローン',
        'bank_consumer_loans_notes': '消費者ローン残高',
        'bank_securities': '銀行保有証券',
        'bank_securities_notes': '金利リスク',
        'bank_deposits_title': '銀行預金',
        'bank_deposits_notes': '調達変化',
        
        # --- Banking Page: Financial Stress Indicators ---
        'bank_stress_section': '⚠️ 金融ストレス指標',
        'bank_move': 'MOVE指数',
        'bank_move_desc': '債券版恐怖指数',
        'bank_move_notes': '危機前に急騰',
        'bank_small_deposits_desc': '中小銀行預金残高',
        'bank_small_deposits_notes': '急落=取り付け騒ぎ警告',
        'bank_nfci': 'NFCI',
        'bank_nfci_desc': 'シカゴ連銀金融環境指数',
        'bank_nfci_notes': '+引締め, -緩和',
        'bank_cc_delinquency_desc': '消費者ストレス指標',
        'bank_cc_delinquency_notes': '上昇=景気後退警告',
        'bank_breakeven': 'ブレークイーブン 10Y',
        'bank_breakeven_desc': '予想インフレ率',
        'bank_breakeven_notes': '2.2-2.3%で安定',
        'bank_cp_spread': 'CPスプレッド',
        'bank_cp_spread_desc': '短期企業資金調達ストレス',
        'bank_cp_spread_notes': '急騰=リーマン級警告',
        'bank_total_loans': '融資総額',
        'bank_total_loans_desc': '信用創造',
        'bank_total_loans_notes': '減少=信用収縮',
        'bank_copper_gold': '銅/金レシオ',
        'bank_copper_gold_desc': '景気先行指標',
        'bank_cu_au_ratio': 'Cu/Auレシオ',
        'bank_cu_au_help': '銅($)/金($) * 1000',
        
        # --- Banking Page: C&I Lending SLOOS ---
        'bank_ci_std_small': 'C&I基準 (中小企業)',
        'bank_ci_std_small_notes': '雇用の先行指標',
        'bank_ci_tightening_indicator_notes': '>0 引締め, >20% 警告',
        'bank_ci_demand_indicator_notes': '基準とのギャップに注目',
        
        # --- Banking Page: CRE Lending SLOOS ---
        'bank_cre_section': '🏢 CRE融資 - SLOOS',
        'bank_cre_construction': '建設 & 土地',
        'bank_cre_construction_notes': '不動産開発のゲート',
        'bank_cre_multifamily': '集合住宅',
        'bank_cre_multifamily_notes': '住宅供給への影響',
        'bank_cre_office': 'オフィス/非住宅',
        'bank_cre_office_notes': 'オフィス危機の監視',
        'bank_cre_demand_indicator_notes': '不動産投資意欲',
        
        # --- Banking Page: Loan Comparison ---
        'bank_loan_comparison': '📈 融資残高比較',
        
        # --- Analysis Lab Page Extended ---
        'lab_subtitle': '💡 マクロ流動性と金融環境を分析するラボ',
        'lab_glp_section': '🌊 グローバル流動性プロキシ (GLP)',
        'lab_glp_about': '📖 GLPとは?',
        'lab_glp_no_data': 'GLPデータ利用不可',
        'lab_m2v_section': '🔄 M2流通速度',
        'lab_m2v_about': '📖 M2流通速度とは?',
        'lab_fsi_section': '📊 金融ストレス指数 (FSI)',
        'lab_fsi_about': '📖 FSIとは?',
        'lab_credit_section': '📊 信用状況',
        'lab_bond_etf_section': '📊 社債ETF',
        'lab_ig_etf': '投資適格債 (LQD)',
        'lab_hy_etf': 'ハイイールド債 (HYG)',
        'lab_data_period': '📅 データ期間',
        'lab_source_update': '🔄 提供元更新',
        'lab_calculated': '計算値',
        
        # --- Analysis Lab: M2V & FSI Status ---
        'lab_m2v_unavailable': 'M2Vデータ取得不可',
        'lab_m2v_historic_low': '🔵 歴史的低水準 (資金退蔵)',
        'lab_m2v_low': '🟡 低水準',
        'lab_m2v_normal': '🟢 正常範囲',
        'lab_fsi_unavailable': 'FSIデータ取得不可',
        'lab_fsi_loose': '🟢 緩和 (リスクオン)',
        'lab_fsi_normal': '🟡 正常',
        'lab_fsi_caution': '🟠 警戒',
        'lab_fsi_crisis': '🔴 危機レベル',
        
        # --- Analysis Lab: Lag Correlation ---
        'lab_lag_correlation': '📊 ラグ相関分析',
        'lab_lag_desc': '💡 GLP先行指標分析（株式/BTC）',
        'lab_compare_with': '比較対象',
        'lab_best_lag': '最適ラグ',
        'lab_lag_help': 'GLPがこの日数だけ先行',
        'lab_correlation': '相関係数',
        'lab_correlation_help': '相関係数 (-1 〜 1)',
        'lab_strong_positive': '🟢 強い正の相関',
        'lab_moderate': '🟡 中程度の相関',
        'lab_weak': '🔴 弱い相関',
        'lab_insufficient_data_lag': 'データ不足 (100日以上必要)',
        'lab_target_unavailable': '{target}データ取得不可',
        'lab_glp_unavailable': 'GLPデータ取得不可',
        
        # --- Analysis Lab: Regime Detection ---
        'lab_regime_detection': '🚦 レジーム検出',
        'lab_regime_desc': '💡 流動性の加速・減速を検出',
        'lab_regime_chance': '## 🟢 チャンス',
        'lab_regime_caution': '## 🔴 注意',
        'lab_liquidity_accelerating': '流動性加速中',
        'lab_liquidity_decelerating': '流動性減速中',
        'lab_ma20_change': 'MA20変化率',
        'lab_ma20_help': '5日間の変化率',
        'lab_insufficient_data_short': 'データ不足',
        
        # --- Analysis Lab: Cross-Asset Spreads ---
        'lab_cross_spreads': '💧 クロスアセットスプレッド',
        'lab_spreads_desc': '💡 主要ETFのBid-Askスプレッドで流動性品質を監視',
        'lab_status_na': '❓ N/A',
        'lab_status_good': '🟢 良好',
        'lab_status_normal': '🟡 通常',
        'lab_status_warning': '🔴 警戒',
        'lab_spreads_no_data': 'スプレッドデータを取得できませんでした',
        
        # --- Analysis Lab Explanations ---
        'lab_glp_explanation': '''**Global Liquidity Proxy（グローバル流動性プロキシ）** は、世界の金融市場に流れている「お金の量」を推定する指標です。

**計算式**: `FRB資産 + ECB資産(ドル換算) - TGA - RRP`

| 要素 | 説明 |
|------|------|
| **FRB資産** | アメリカ中央銀行のバランスシート（QEで増加） |
| **ECB資産** | 欧州中央銀行のバランスシート（ユーロ→ドル換算） |
| **TGA** | 米財務省の預金口座（多い = 市場から吸収） |
| **RRP** | 翌日物リバースレポ（多い = 市場から吸収） |

**見方**:
- 📈 **GLP上昇** = 市場に流動性が増加 → 株・BTCに追い風
- 📉 **GLP下降** = 流動性引き締め → リスク資産に逆風''',
        'lab_m2v_explanation': '''**M2 Velocity（M2通貨回転率）** は、お金が経済の中でどれだけ「回っている」かを示す指標です。

**計算式**: `名目GDP ÷ M2マネーサプライ`

**見方**:
- 📉 **低下** = お金が滞留している（貯蓄増加、消費控え）→ デフレ圧力
- 📈 **上昇** = お金が活発に回っている（消費活発化）→ インフレ圧力''',
        'lab_fsi_explanation': '''**Financial Stress Index（金融ストレス指数）** は、セントルイス連銀が発表する金融市場の「緊張度」を測る指標です。

**基準**:
| 値 | 状態 | 意味 |
|----|------|------|
| **< -0.5** | 🟢 緩和 | リスクオン環境、投資に有利 |
| **-0.5 〜 0.5** | 🟡 正常 | 通常の市場環境 |
| **0.5 〜 1.5** | 🟠 警戒 | ストレス上昇中、注意 |
| **> 1.5** | 🔴 危機 | 金融危機レベル |''',
        
        # --- Currency Lab Page ---
        'currency_lab_title': '💱 Currency Comparison Lab',
        'currency_lab_subtitle': 'Gold建て・BTC建て・USD建てで通貨を自由に選択して比較',
        'currency_lab_settings': '🎛️ Currency Lab 設定',
        'currency_lab_period': '📅 表示期間',
        'currency_lab_normalize': '📏 正規化 (基準日=100)',
        'currency_lab_gold_section': '🥇 Gold建て通貨',
        'currency_lab_gold_desc': '💡 各通貨でGold 1オンスを買うのに必要な金額を指数化（基準日=100）。上昇=通貨価値下落',
        'currency_lab_gold_meaning_title': '📖 Gold建ての意味',
        'currency_lab_gold_meaning': '''**Gold建て**とは、各通貨の購買力をGoldで測定したものです。

- **上昇** → その通貨でGoldが高くなった = 通貨の購買力が下がった
- **下落** → その通貨でGoldが安くなった = 通貨の購買力が上がった

全ての法定通貨は長期的にGoldに対して価値を失う傾向があります。''',
        'currency_lab_select_gold': '🪙 表示する通貨を選択',
        'currency_lab_select_hint': '👆 通貨を選択してください',
        'currency_lab_btc_section': '₿ BTC建て通貨',
        'currency_lab_btc_desc': '💡 各通貨で1 BTCを買うのに必要な金額を指数化。急騰=BTCの急落を反映',
        'currency_lab_btc_meaning_title': '📖 BTC建ての意味',
        'currency_lab_btc_meaning': '''**BTC建て**とは、各通貨の購買力をBitcoinで測定したものです。

- **上昇** → その通貨でBTCが高くなった = 通貨の購買力が下がった（BTCが高騰）
- **下落** → その通貨でBTCが安くなった = 通貨の購買力が上がった（BTCが下落）

Goldより変動が激しいため、短期的な市場センチメントを反映します。''',
        'currency_lab_select_btc': '₿ 表示する通貨を選択',
        'currency_lab_usd_section': '💵 USD建て（FX & 資産）',
        'currency_lab_usd_desc': '💡 従来のFXペアと主要資産のドル建て価格',
        'currency_lab_usd_meaning_title': '📖 USD建ての意味',
        'currency_lab_usd_meaning': '''**USD建て**は従来の為替レートと資産価格です。

- **USD/JPY上昇** → 円安ドル高
- **EUR/USD上昇** → ユーロ高ドル安
- **BTC/USD上昇** → ビットコイン高

異なる種類の資産を同じ通貨基準で比較できます。''',
        'currency_lab_select_usd': '💵 表示するペアを選択',
        'currency_lab_cross_section': '🔀 クロス比較',
        'currency_lab_cross_desc': '💡 Gold建て vs BTC建てで同じ通貨を比較',
        'currency_lab_cross_meaning_title': '📖 クロス比較の意味',
        'currency_lab_cross_meaning': '''**同じ通貨をGold建てとBTC建てで比較**することで：

- 両方が下落 → その通貨が強い
- 両方が上昇 → その通貨が弱い
- Gold建てのみ上昇 → Gold高（インフレ懸念？）
- BTC建てのみ上昇 → BTC高（リスクオン？）

伝統資産(Gold)とデジタル資産(BTC)の動きの違いを可視化します。''',
        'currency_lab_select_cross': '🌍 比較する通貨',
        'currency_lab_btc_vs_gold': 'BTC vs Gold',
        'currency_lab_insufficient_data': 'データが不足しています',
        'currency_lab_tip': '💡 **Tip**: サイドバーで期間と正規化を切り替えて、異なる視点で分析できます',
        
        # --- Multi-Region Spread Monitor ---
        'market_hours_reference': '市場時間一覧',
        'region': 'リージョン',
        'market_hours_local': '時間帯 (現地時間)',
        
        # --- AI Category Reports ---
        'ai_category_reports': '📊 カテゴリ別レポート',
        'ai_category_reports_desc': 'Web検索を活用したカテゴリ別詳細分析',
        'ai_select_category': '分析したいカテゴリを選択:',
        'ai_generating_report': '🔍 {category}レポートをウェブ検索で生成中...',
        'ai_report_generated': '📋 {category}レポート',
        'ai_web_search_note': '💡 このレポートはGeminiウェブ検索による最新情報を含みます',
        
        # --- Data Frequency Labels ---
        'freq_daily': '日次',
        'freq_weekly': '週次',
        'freq_monthly': '月次',
        'freq_quarterly': '四半期',
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_current_language() -> str:
    """Get current language from session state"""
    if 'lang' not in st.session_state:
        st.session_state['lang'] = DEFAULT_LANGUAGE
    return st.session_state['lang']


def set_language(lang: str) -> None:
    """Set language in session state"""
    if lang in SUPPORTED_LANGUAGES:
        st.session_state['lang'] = lang


def t(key: str, **kwargs) -> str:
    """
    Get translated text for a key.
    
    Args:
        key: Translation key
        **kwargs: Format arguments (e.g., count=5, date='2024-01-01')
    
    Returns:
        Translated string, or key if not found
    """
    lang = get_current_language()
    
    # Get translation dictionary for current language
    translations = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE])
    
    # Get text, fallback to English, then to key itself
    text = translations.get(key)
    if text is None:
        text = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
    
    # Apply format arguments if any
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    
    return text


def get_language_options() -> Dict[str, str]:
    """Get language options for selectbox"""
    return SUPPORTED_LANGUAGES


def render_language_selector() -> str:
    """
    Render language selector in sidebar and return selected language.
    """
    current_lang = get_current_language()
    
    options = list(SUPPORTED_LANGUAGES.keys())
    labels = list(SUPPORTED_LANGUAGES.values())
    
    current_index = options.index(current_lang) if current_lang in options else 0
    
    st.write("🌐 Language / 言語")
    selected_label = st.radio(
        "Language",
        labels,
        index=current_index,
        key="language_selector",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    selected_lang = options[labels.index(selected_label)]
    
    if selected_lang != current_lang:
        set_language(selected_lang)
        st.rerun()
    
    return selected_lang
