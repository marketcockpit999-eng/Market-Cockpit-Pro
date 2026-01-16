# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Data Processor
データ加工、計算、検証関数を管理
"""

from datetime import datetime
from .config import DATA_FRESHNESS_RULES, VALIDATION_RANGES


def get_data_freshness_status(last_valid_dates: dict, release_dates: dict = None) -> dict:
    """
    Check data freshness for all 67 indicators defined in DATA_FRESHNESS_RULES.
    Only counts items explicitly defined in rules - ignores extra DataFrame columns.
    Priority: Actual release_dates (provider update) > last_valid_dates (observation date)
    Returns: dict with 'summary' and 'details'
    """
    today = datetime.now().date()
    
    results = {
        'fresh': [],
        'stale': [],
        'critical': [],
        'missing': [],
        'details': {}
    }
    
    # Build complete list of defined indicators with their categories
    defined_indicators = {}  # indicator -> category
    for category, config in DATA_FRESHNESS_RULES.items():
        for ind in config['indicators']:
            defined_indicators[ind] = category
    
    # Iterate over DEFINED indicators only (not all DataFrame columns)
    for indicator, category in defined_indicators.items():
        rules = DATA_FRESHNESS_RULES[category]
        
        if indicator in last_valid_dates:
            try:
                date_str = last_valid_dates[indicator]
                check_date_str = date_str
                is_priority_release = False
                
                if release_dates and indicator in release_dates and release_dates[indicator]:
                    check_date_str = release_dates[indicator]
                    is_priority_release = True
                    
                last_date = datetime.strptime(check_date_str, '%Y-%m-%d').date()
                days_old = (today - last_date).days
                
                if days_old <= rules['fresh']:
                    status = 'fresh'
                    results['fresh'].append(indicator)
                elif days_old <= rules['stale']:
                    status = 'stale'
                    results['stale'].append(indicator)
                else:
                    status = 'critical'
                    results['critical'].append(indicator)
                
                results['details'][indicator] = {
                    'last_date': date_str,
                    'release_date': release_dates.get(indicator) if release_dates else None,
                    'days_old': days_old,
                    'status': status,
                    'category': category,
                    'is_release_based': is_priority_release,
                    'expected_max': rules['fresh']
                }
            except:
                results['missing'].append(indicator)
                results['details'][indicator] = {
                    'last_date': None,
                    'days_old': None,
                    'status': 'missing',
                    'category': category,
                    'expected_max': None
                }
        else:
            # Indicator defined in rules but not in DataFrame
            results['missing'].append(indicator)
            results['details'][indicator] = {
                'last_date': None,
                'days_old': None,
                'status': 'missing',
                'category': category,
                'expected_max': None
            }
    
    # Calculate summary - total is always the number of defined indicators (67)
    total = len(defined_indicators)
    results['summary'] = {
        'total': total,
        'fresh_count': len(results['fresh']),
        'stale_count': len(results['stale']),
        'critical_count': len(results['critical']),
        'missing_count': len(results['missing']),
        'health_score': round(len(results['fresh']) / max(total, 1) * 100, 1)
    }
    
    return results


def validate_data_ranges(df, show_warnings=True) -> dict:
    """
    Validate that data values fall within expected ranges.
    Returns dict of any validation issues found.
    """
    issues = {}
    
    for indicator, (min_val, max_val) in VALIDATION_RANGES.items():
        if indicator in df.columns:
            series = df[indicator].dropna()
            if len(series) > 0:
                latest = series.iloc[-1]
                if latest < min_val or latest > max_val:
                    issues[indicator] = {
                        'value': latest,
                        'expected_range': (min_val, max_val),
                        'status': 'OUT_OF_RANGE'
                    }
    
    return issues


def get_mom_yoy(col_name, df_original, freq='M'):
    """
    Calculate Month-over-Month and Year-over-Year changes.
    
    Args:
        col_name: Column name to analyze
        df_original: Original DataFrame (non-ffilled)
        freq: 'M' for monthly, 'Q' for quarterly, 'W' for weekly
    
    Returns:
        tuple: (mom_pct, yoy_pct) or (None, None) if not enough data
    """
    series = df_original.get(col_name)
    if series is None:
        return None, None
    
    data = series.dropna()
    if len(data) < 2:
        return None, None
    
    curr = data.iloc[-1]
    prev = data.iloc[-2]
    
    # MoM calculation
    if prev != 0:
        mom = ((curr / prev) - 1) * 100
    else:
        mom = None
    
    # YoY calculation (depends on frequency)
    yoy = None
    if freq == 'M':
        periods_back = 12
    elif freq == 'Q':
        periods_back = 4
    elif freq == 'W':
        periods_back = 52
    else:
        periods_back = 12
    
    if len(data) > periods_back:
        prev_yr = data.iloc[-periods_back - 1]
        if prev_yr != 0:
            yoy = ((curr / prev_yr) - 1) * 100
    
    return mom, yoy


def get_freshness_badge(last_updated_str: str) -> str:
    """
    Return a badge based on how recently the data was updated.
    🆕 = Updated within 24 hours
    ✅ = Updated within 7 days
    ⏳ = Updated within 30 days
    ⚠️ = Not updated in 30+ days
    """
    if not last_updated_str:
        return ""
    
    try:
        last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d')
        now = datetime.now()
        days_ago = (now - last_updated).days
        
        if days_ago <= 1:
            return "🆕"
        elif days_ago <= 7:
            return "✅"
        elif days_ago <= 30:
            return "⏳"
        else:
            return "⚠️"
    except:
        return ""
