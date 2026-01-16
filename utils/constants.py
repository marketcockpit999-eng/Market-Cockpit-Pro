# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Constants (REDIRECT FILE)
================================================================================
⚠️  THIS FILE IS DEPRECATED - DO NOT EDIT
    All definitions have moved to utils/indicators.py
    
    This file exists only for backward compatibility.
    Import from utils.config or utils.indicators instead.
================================================================================
"""

# Redirect all imports to config.py (which imports from indicators.py)
from .config import (
    # API & Settings
    FRED_API_KEY,
    PAGE_TITLE,
    MANUAL_DATA_FILE,
    
    # Indicator Definitions (from indicators.py)
    INDICATORS,
    FRED_INDICATORS,
    YAHOO_INDICATORS,
    DATA_FREQUENCY,
    DATA_FRESHNESS_RULES,
    VALIDATION_RANGES,
    FRED_UNITS,
    
    # Helper Functions
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
    
    # Other configs
    EXPLANATIONS,
    MONITORED_AGENCIES,
    RSS_FEEDS,
    CONTEXT_KEYWORDS,
)

import warnings
warnings.warn(
    "utils.constants is deprecated. Import from utils.config or utils.indicators instead.",
    DeprecationWarning,
    stacklevel=2
)
