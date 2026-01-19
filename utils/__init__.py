# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Utils Package
全ユーティリティモジュールを統合エクスポート
"""

# Config & Indicators
from .config import (
    FRED_API_KEY,
    PAGE_TITLE,
    MANUAL_DATA_FILE,
    GEMINI_MODEL,
    CLAUDE_MODEL,
    DATA_FRESHNESS_RULES,
    DATA_FREQUENCY,
    FRED_INDICATORS,
    YAHOO_INDICATORS,
    FRED_UNITS,
    VALIDATION_RANGES,
    EXPLANATIONS,
    MONITORED_AGENCIES,
    RSS_FEEDS,
    CONTEXT_KEYWORDS,
    MANUAL_GLOBAL_M2,
)

# i18n (Internationalization)
from .i18n import (
    t,
    set_language,
    get_current_language,
    get_language_options,
    render_language_selector,
    SUPPORTED_LANGUAGES,
    TRANSLATIONS,
)

# Indicator Registry (Single Source of Truth)
from .indicators import (
    INDICATORS,
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

# Data Fetcher
from .data_fetcher import (
    get_market_data,
    get_fred_release_dates,
    get_pe_ratios,
    get_crypto_leverage_data,
    get_stablecoin_data,
    get_stablecoin_historical,
    get_tokenized_treasury_data,
    get_protocol_historical,
    get_crypto_fear_greed,
    get_cnn_fear_greed,
    get_put_call_ratio,
    get_aaii_sentiment,
    get_fomc_sep_projections,
    get_cme_fedwatch,
    load_manual_data,
    save_manual_data,
    fetch_h41_data,
)

# Data Processor
from .data_processor import (
    get_data_freshness_status,
    validate_data_ranges,
    get_mom_yoy,
    get_freshness_badge,
)

# Charts
from .charts import (
    show_metric,
    show_metric_with_sparkline,
    plot_dual_axis,
    plot_soma_composition,
    display_macro_card,
)

# AI Clients
from .ai_clients import (
    init_ai_clients,
    get_market_summary,
    run_gemini_analysis,
    run_claude_analysis,
)

# News
from .news import (
    get_time_diff_str,
    search_google_news,
    check_for_market_alerts,
    fetch_agency_rss,
    format_rss_entry,
)

# Version
__version__ = "2.2.0"  # Added i18n support
__all__ = [
    # i18n
    "t", "set_language", "get_current_language",
    "get_language_options", "render_language_selector",
    "SUPPORTED_LANGUAGES", "TRANSLATIONS",
    # Config
    "FRED_API_KEY", "PAGE_TITLE", "MANUAL_DATA_FILE",
    "GEMINI_MODEL", "CLAUDE_MODEL",
    "DATA_FRESHNESS_RULES", "DATA_FREQUENCY",
    "FRED_INDICATORS", "YAHOO_INDICATORS", "FRED_UNITS",
    "VALIDATION_RANGES", "EXPLANATIONS",
    "MONITORED_AGENCIES", "RSS_FEEDS", "CONTEXT_KEYWORDS",
    "MANUAL_GLOBAL_M2",
    # Indicator Registry
    "INDICATORS",
    "get_fred_indicators", "get_yahoo_indicators",
    "get_data_frequency", "get_freshness_rules",
    "get_validation_ranges", "get_fred_units",
    "get_indicators_for_page", "get_indicators_for_ai",
    "get_indicators_by_category", "get_indicator_info",
    "get_all_indicator_names",
    # Data Fetcher
    "get_market_data", "get_fred_release_dates",
    "get_pe_ratios", "get_crypto_leverage_data",
    "get_stablecoin_data", "get_stablecoin_historical",
    "get_tokenized_treasury_data", "get_protocol_historical",
    "get_crypto_fear_greed", "get_cnn_fear_greed",
    "get_put_call_ratio", "get_aaii_sentiment",
    "get_fomc_sep_projections", "get_cme_fedwatch",
    "load_manual_data", "save_manual_data", "fetch_h41_data",
    # Data Processor
    "get_data_freshness_status", "validate_data_ranges",
    "get_mom_yoy", "get_freshness_badge",
    # Charts
    "show_metric", "show_metric_with_sparkline",
    "plot_dual_axis", "plot_soma_composition", "display_macro_card",
    # AI Clients
    "init_ai_clients", "get_market_summary",
    "run_gemini_analysis", "run_claude_analysis",
    # News
    "get_time_diff_str", "search_google_news",
    "check_for_market_alerts", "fetch_agency_rss", "format_rss_entry",
]
