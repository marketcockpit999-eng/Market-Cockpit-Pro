# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Display Checker
================================================================================
Validates that all indicators have their required display elements.

Based on DISPLAY_SPEC.md (the "book" = source of truth)

Standard 9 Elements:
  1. label        - Indicator name (MANDATORY)
  2. help_text    - Tooltip explanation (MANDATORY)
  3. value        - Current value (MANDATORY)
  4. delta        - Change from previous (OPTIONAL)
  5. data_period  - Data date/period (MANDATORY)
  6. release_date - Source update date (MANDATORY)
  7. notes        - Brief description (OPTIONAL)
  8. sparkline    - 60-day mini chart (OPTIONAL)
  9. full_chart   - Long-term chart (OPTIONAL)

Display Patterns:
  - standard:    77 items - Standard 9 elements
  - mom_yoy:      6 items - Standard + MoM%/YoY%
  - manual_calc:  6 items - Special calculation logic
  - web_scrape:   2 items - Web scraping with fallback
  - calculated:   1 item  - Derived from components
  - api:          9 items - Individual API calls
================================================================================
"""

import re
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta

# from .indicators import INDICATORS  # Moved to check_all checks to avoid circular import
from .help_texts import HELP_EN, HELP_JA


# =============================================================================
# DISPLAY SPEC DEFINITIONS (from DISPLAY_SPEC.md)
# =============================================================================

# Standard 9 Elements categorized by requirement level
STANDARD_ELEMENTS = {
    'mandatory': ['label', 'help_text', 'value', 'data_period', 'release_date'],
    'optional': ['delta', 'notes', 'sparkline', 'full_chart'],
}

# Pattern-specific requirements
PATTERN_SPECS = {
    'standard': {
        'description': 'Standard metric with 9 elements',
        'base': STANDARD_ELEMENTS,
        'additions': {},
    },
    'mom_yoy': {
        'description': 'Month-over-month and Year-over-year display',
        'base': STANDARD_ELEMENTS,
        'additions': {
            'mandatory': [],
            'optional': ['mom_percent', 'yoy_percent', 'yoy_chart'],
        },
    },
    'manual_calc': {
        'description': 'Manually calculated metrics (pattern varies)',
        'base': STANDARD_ELEMENTS,
        'additions': {},
    },
    'web_scrape': {
        'description': 'Web-scraped data with fallback',
        'base': STANDARD_ELEMENTS,
        'additions': {
            'mandatory': [],
            'optional': ['fallback_notice'],
        },
    },
    'calculated': {
        'description': 'Derived from other indicators',
        'base': STANDARD_ELEMENTS,
        'additions': {
            'mandatory': ['has_components'],
            'optional': [],
        },
    },
    'api': {
        'description': 'External API data (may lack some elements)',
        'base': {
            'mandatory': ['label', 'help_text', 'value'],  # Reduced requirements
            'optional': ['delta', 'notes', 'data_period', 'release_date'],
        },
        'additions': {},
    },
}


# =============================================================================
# MANUAL_CALC SPECIFIC CHECKS
# =============================================================================

MANUAL_CALC_SPECS = {
    'NFP': {
        'check_type': 'month_change',
        'min_periods': 2,
        'description': 'Non-Farm Payrolls monthly change',
    },
    'UNRATE': {
        'check_type': 'level_with_delta',
        'min_periods': 2,
        'description': 'Unemployment rate with month-over-month change',
    },
    'AvgHourlyEarnings': {
        'check_type': 'mom_yoy_pct',
        'min_periods': 13,  # Need 12 months for YoY
        'description': 'Average hourly earnings with MoM% and YoY%',
    },
    'ICSA': {
        'check_type': 'level_with_delta',
        'min_periods': 2,
        'description': 'Initial jobless claims with week-over-week change',
    },
    'RealGDP': {
        'check_type': 'qoq_annualized',
        'min_periods': 2,
        'description': 'Real GDP quarter-over-quarter annualized rate',
    },
    'ADP': {
        'check_type': 'month_change',
        'min_periods': 2,
        'description': 'ADP employment monthly change',
    },
}


# =============================================================================
# CALCULATED INDICATOR SPECS
# =============================================================================

CALCULATED_SPECS = {
    'Global_Liquidity_Proxy': {
        'components': ['SOMA_Total', 'ECB_Assets', 'TGA', 'ON_RRP'],
        'formula': 'SOMA_Total + ECB_Assets - TGA - ON_RRP',
    },
}


# =============================================================================
# CHECKER CLASSES
# =============================================================================

class CheckResult:
    """Result of a single indicator check"""
    
    def __init__(self, indicator_name: str, pattern: str):
        self.indicator_name = indicator_name
        self.pattern = pattern
        self.mandatory_passed: List[str] = []
        self.mandatory_failed: List[str] = []
        self.optional_passed: List[str] = []
        self.optional_missing: List[str] = []
        self.warnings: List[str] = []
        self.details: Dict[str, Any] = {}
    
    @property
    def is_ok(self) -> bool:
        """True if all mandatory checks passed"""
        return len(self.mandatory_failed) == 0
    
    @property
    def status(self) -> str:
        if self.is_ok:
            if self.optional_missing or self.warnings:
                return '[WARN]'
            return '[OK]'
        return '[FAIL]'
    
    def add_mandatory_pass(self, check_name: str, detail: str = ''):
        self.mandatory_passed.append(check_name)
        if detail:
            self.details[check_name] = detail
    
    def add_mandatory_fail(self, check_name: str, detail: str = ''):
        self.mandatory_failed.append(check_name)
        if detail:
            self.details[check_name] = detail
    
    def add_optional_pass(self, check_name: str, detail: str = ''):
        self.optional_passed.append(check_name)
        if detail:
            self.details[check_name] = detail
    
    def add_optional_missing(self, check_name: str, detail: str = ''):
        self.optional_missing.append(check_name)
        if detail:
            self.details[check_name] = detail
    
    def add_warning(self, message: str):
        self.warnings.append(message)
    
    def __str__(self) -> str:
        lines = [f"{self.status} {self.indicator_name} ({self.pattern})"]
        if self.mandatory_failed:
            lines.append(f"  [FAIL] Missing (mandatory): {', '.join(self.mandatory_failed)}")
        if self.optional_missing:
            lines.append(f"  [WARN] Missing (optional): {', '.join(self.optional_missing)}")
        if self.warnings:
            lines.append(f"  [NOTE] Warnings: {', '.join(self.warnings)}")
        return '\n'.join(lines)


class DisplayChecker:
    """Main checker class for validating indicator display elements"""
    
    def __init__(self, df: pd.DataFrame = None, df_original: Optional[Dict] = None):
        """
        Initialize checker with data
        
        Args:
            df: Main DataFrame with forward-filled data (optional for static checks)
            df_original: Dict of original series (not forward-filled)
        """
        self.df = df if df is not None else pd.DataFrame()
        self.df_original = df_original if df_original is not None else {}
        self.results: Dict[str, CheckResult] = {}
    
    def check_all(self) -> Dict[str, List[CheckResult]]:
        """Check all indicators and return results grouped by pattern"""
        from .indicators import INDICATORS
        results_by_pattern = {
            'standard': [],
            'mom_yoy': [],
            'manual_calc': [],
            'web_scrape': [],
            'calculated': [],
            'api': [],
        }
        
        for name, config in INDICATORS.items():
            pattern = config.get('display_pattern', 'standard')
            result = self.check_indicator(name, config)
            self.results[name] = result
            
            if pattern in results_by_pattern:
                results_by_pattern[pattern].append(result)
        
        return results_by_pattern
    
    def check_indicator(self, name: str, config: dict) -> CheckResult:
        """Check a single indicator against its pattern requirements"""
        pattern = config.get('display_pattern', 'standard')
        result = CheckResult(name, pattern)
        
        # Get pattern spec
        spec = PATTERN_SPECS.get(pattern, PATTERN_SPECS['standard'])
        base = spec['base']
        additions = spec.get('additions', {})
        
        # Combine mandatory requirements
        mandatory = list(base.get('mandatory', []))
        mandatory.extend(additions.get('mandatory', []))
        
        # Combine optional requirements
        optional = list(base.get('optional', []))
        optional.extend(additions.get('optional', []))
        
        # Check each element
        for element in mandatory:
            passed, detail = self._check_element(name, config, element)
            if passed:
                result.add_mandatory_pass(element, detail)
            else:
                result.add_mandatory_fail(element, detail)
        
        for element in optional:
            passed, detail = self._check_element(name, config, element)
            if passed:
                result.add_optional_pass(element, detail)
            else:
                result.add_optional_missing(element, detail)
        
        # Pattern-specific additional checks
        if pattern == 'manual_calc':
            self._check_manual_calc_specific(name, config, result)
        elif pattern == 'calculated':
            self._check_calculated_specific(name, config, result)
        elif pattern == 'mom_yoy':
            self._check_mom_yoy_specific(name, config, result)
        
        return result
    
    def _check_element(self, name: str, config: dict, element: str) -> Tuple[bool, str]:
        """Check a single element. Returns (passed, detail)"""
        
        if element == 'label':
            # Label is always present if indicator exists in INDICATORS
            return True, f"'{name}'"
        
        elif element == 'help_text':
            # Check if help text exists in help_texts.py
            help_key = f'help_{name}'
            has_en = help_key in HELP_EN
            has_ja = help_key in HELP_JA
            if has_en and has_ja:
                return True, 'EN+JA'
            elif has_en:
                return True, 'EN only (JA missing)'
            elif has_ja:
                return True, 'JA only (EN missing)'
            else:
                return False, f'No help text for {help_key}'
        
        elif element == 'value':
            # Check if data exists in DataFrame
            if self.df.empty:
                # Static check mode - can't verify data
                return True, 'Data check skipped (no DataFrame)'
            
            if name not in self.df.columns:
                # Check if it's a non-stored indicator (API type)
                if config.get('df_stored', True) is False:
                    return True, 'Not stored in DataFrame (API)'
                return False, f'{name} not in DataFrame'
            
            series = self.df[name]
            if series.isna().all():
                return False, 'All values are NaN'
            
            latest = series.dropna().iloc[-1] if len(series.dropna()) > 0 else None
            return True, f'Latest: {latest}'
        
        elif element == 'delta':
            # Check if we can calculate delta
            if self.df.empty:
                return True, 'Data check skipped (no DataFrame)'
            
            orig_series = self.df_original.get(name)
            if orig_series is not None:
                valid_data = orig_series.dropna()
                if len(valid_data) >= 2:
                    return True, f'{len(valid_data)} points'
                return False, f'Only {len(valid_data)} point(s)'
            
            # Fallback to df
            if name in self.df.columns:
                valid_data = self.df[name].dropna()
                if len(valid_data) >= 2:
                    return True, f'{len(valid_data)} points (forward-filled)'
            
            return False, 'Insufficient data'
        
        elif element == 'data_period':
            # Data period comes from index dates
            if self.df.empty:
                return True, 'Data check skipped (no DataFrame)'
            
            if name in self.df.columns and hasattr(self.df.index, 'max'):
                latest_date = self.df[name].dropna().index.max() if name in self.df.columns else None
                if latest_date:
                    return True, str(latest_date)[:10]
            
            return True, 'Date available at runtime'
        
        elif element == 'release_date':
            # Release date is fetched at runtime from FRED metadata
            # We can only verify the mechanism exists, not the actual date
            source = config.get('source', 'UNKNOWN')
            if source in ['FRED', 'YAHOO', 'MANUAL']:
                return True, f'Source: {source}'
            return True, f'Source: {source} (verify at runtime)'
        
        elif element == 'notes':
            # Check if notes exists in indicator config
            notes = config.get('notes', '')
            if notes:
                return True, notes[:30] + '...' if len(notes) > 30 else notes
            return False, 'No notes defined'
        
        elif element == 'sparkline':
            # Need at least 10 data points for a meaningful sparkline
            if self.df.empty:
                return True, 'Data check skipped (no DataFrame)'
            
            if name in self.df.columns:
                valid_data = self.df[name].dropna()
                if len(valid_data) >= 10:
                    return True, f'{len(valid_data)} points'
                return False, f'Only {len(valid_data)} points (need 10+)'
            
            return False, 'Not in DataFrame'
        
        elif element == 'full_chart':
            # Need historical data for chart
            if self.df.empty:
                return True, 'Data check skipped (no DataFrame)'
            
            if name in self.df.columns:
                valid_data = self.df[name].dropna()
                if len(valid_data) >= 30:  # About 1 month of daily data
                    return True, f'{len(valid_data)} points'
            
            return True, 'Chart available at runtime'
        
        elif element == 'has_components':
            # For calculated indicators, check if all components exist
            calc_spec = CALCULATED_SPECS.get(name)
            if calc_spec:
                components = calc_spec['components']
                missing = [c for c in components if c not in self.df.columns]
                if missing:
                    return False, f'Missing components: {missing}'
                return True, f'All components present: {components}'
            return False, 'No calculation spec defined'
        
        elif element in ['mom_percent', 'yoy_percent', 'yoy_chart', 'fallback_notice']:
            # These are runtime-generated elements
            return True, 'Generated at runtime'
        
        else:
            return True, f'Unknown element: {element}'
    
    def _check_manual_calc_specific(self, name: str, config: dict, result: CheckResult):
        """Additional checks for manual_calc pattern"""
        spec = MANUAL_CALC_SPECS.get(name)
        if not spec:
            result.add_warning(f'No manual_calc spec defined for {name}')
            return
        
        min_periods = spec['min_periods']
        
        if self.df.empty:
            result.add_warning('Cannot verify calculation data without DataFrame')
            return
        
        orig_series = self.df_original.get(name)
        if orig_series is None and name in self.df.columns:
            orig_series = self.df[name]
        
        if orig_series is not None:
            valid_data = orig_series.dropna()
            if len(valid_data) >= min_periods:
                result.details['calc_data'] = f'{len(valid_data)} periods (need {min_periods})'
            else:
                result.add_warning(f'Need {min_periods} periods, have {len(valid_data)}')
    
    def _check_calculated_specific(self, name: str, config: dict, result: CheckResult):
        """Additional checks for calculated pattern"""
        # Component check is handled in _check_element for 'has_components'
        pass
    
    def _check_mom_yoy_specific(self, name: str, config: dict, result: CheckResult):
        """Additional checks for mom_yoy pattern"""
        if self.df.empty:
            return
        
        orig_series = self.df_original.get(name)
        if orig_series is None and name in self.df.columns:
            orig_series = self.df[name]
        
        if orig_series is not None:
            valid_data = orig_series.dropna()
            if len(valid_data) < 13:
                result.add_warning(f'YoY calculation needs 13 periods, have {len(valid_data)}')
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        total = len(self.results)
        passed = sum(1 for r in self.results.values() if r.is_ok)
        failed = total - passed
        warnings = sum(1 for r in self.results.values() if r.optional_missing or r.warnings)
        
        by_pattern = {}
        for name, result in self.results.items():
            pattern = result.pattern
            if pattern not in by_pattern:
                by_pattern[pattern] = {'total': 0, 'passed': 0, 'failed': 0, 'warnings': 0}
            by_pattern[pattern]['total'] += 1
            if result.is_ok:
                by_pattern[pattern]['passed'] += 1
            else:
                by_pattern[pattern]['failed'] += 1
            if result.optional_missing or result.warnings:
                by_pattern[pattern]['warnings'] += 1
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'pass_rate': f'{passed/total*100:.1f}%' if total > 0 else 'N/A',
            'by_pattern': by_pattern,
        }
    
    def get_missing_help_texts(self) -> List[str]:
        """Get list of indicators missing help text"""
        missing = []
        for name, result in self.results.items():
            if 'help_text' in result.mandatory_failed:
                missing.append(name)
        return missing
    
    def get_missing_notes(self) -> List[str]:
        """Get list of indicators missing notes"""
        missing = []
        for name, result in self.results.items():
            if 'notes' in result.optional_missing:
                missing.append(name)
        return missing
    
    def print_report(self, verbose: bool = False, show_ok: bool = False):
        """Print check report"""
        summary = self.get_summary()
        
        print("=" * 70)
        print("DISPLAY CHECKER REPORT (Based on DISPLAY_SPEC.md)")
        print("=" * 70)
        print(f"\nTotal Indicators: {summary['total']}")
        print(f"[OK] Passed: {summary['passed']} ({summary['pass_rate']})")
        print(f"[FAIL] Failed: {summary['failed']}")
        print(f"[WARN] With Warnings: {summary['warnings']}")
        
        print("\n--- By Pattern ---")
        for pattern, stats in summary['by_pattern'].items():
            status = '[OK]' if stats['failed'] == 0 else '[FAIL]'
            warn = f" [WARN]{stats['warnings']}" if stats['warnings'] > 0 else ''
            print(f"{status} {pattern}: {stats['passed']}/{stats['total']}{warn}")
        
        # Print failures
        failures = [r for r in self.results.values() if not r.is_ok]
        if failures:
            print("\n" + "=" * 70)
            print("FAILED INDICATORS (Missing Mandatory Elements)")
            print("=" * 70)
            for result in failures:
                print(f"\n{result}")
        
        # Print warnings (optional missing)
        warnings_only = [r for r in self.results.values() 
                        if r.is_ok and (r.optional_missing or r.warnings)]
        if warnings_only and verbose:
            print("\n" + "-" * 70)
            print("WARNINGS (Missing Optional Elements)")
            print("-" * 70)
            for result in warnings_only:
                print(f"\n{result}")
        
        # Print all OK indicators if requested
        if show_ok and verbose:
            ok_results = [r for r in self.results.values() if r.is_ok and not r.optional_missing and not r.warnings]
            print("\n" + "-" * 70)
            print("OK INDICATORS")
            print("-" * 70)
            for result in ok_results:
                print(f"[OK] {result.indicator_name}")
        
        # Missing help texts summary
        missing_help = self.get_missing_help_texts()
        if missing_help:
            print("\n" + "-" * 70)
            print(f"MISSING HELP TEXTS ({len(missing_help)} items)")
            print("-" * 70)
            for name in missing_help:
                print(f"  - help_{name}")
        
        print("\n" + "=" * 70)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def run_display_check(df: pd.DataFrame = None, df_original: Optional[Dict] = None, 
                      verbose: bool = False) -> DisplayChecker:
    """
    Run display check on market data
    
    Args:
        df: Main DataFrame with forward-filled data (optional)
        df_original: Dict of original series (optional)
        verbose: Print detailed report
    
    Returns:
        DisplayChecker instance with results
    """
    checker = DisplayChecker(df, df_original)
    checker.check_all()
    checker.print_report(verbose=verbose)
    return checker


def run_static_check(verbose: bool = False) -> DisplayChecker:
    """
    Run static check (no data required)
    Checks: label, help_text, notes
    
    Returns:
        DisplayChecker instance with results
    """
    checker = DisplayChecker()
    checker.check_all()
    checker.print_report(verbose=verbose)
    return checker


def get_failed_indicators(checker: DisplayChecker) -> List[str]:
    """Get list of indicator names that failed mandatory checks"""
    return [name for name, result in checker.results.items() if not result.is_ok]


def get_indicators_needing_attention(checker: DisplayChecker) -> List[str]:
    """Get list of indicators with failures or warnings"""
    return [name for name, result in checker.results.items() 
            if not result.is_ok or result.optional_missing or result.warnings]


# =============================================================================
# PATTERN-TO-FUNCTION MAPPING (from DISPLAY_SPEC.md)
# =============================================================================

# =============================================================================
# ELEMENT COMPOSITION WARNINGS (Phase 3.5)
# =============================================================================

# Check specific arguments that affect 9-element display
ELEMENT_WARNINGS = {
    'show_metric_with_sparkline': {
        # explanation_key="" means help_text won't show properly
        'explanation_key': {
            'check_empty': True,
            'message': 'explanation_key is empty (help_text may be missing)',
            'severity': 'WARN',
        },
        # notes="" is optional but recommended
        'notes': {
            'check_empty': True,
            'message': 'notes is empty',
            'severity': 'INFO',
        },
    },
    'display_macro_card': {
        # show_level=False hides the main metric
        'show_level': {
            'check_false': True,
            'message': 'show_level=False (level metric will be hidden)',
            'severity': 'WARN',
        },
        # notes="" is optional but recommended
        'notes': {
            'check_empty': True,
            'message': 'notes is empty',
            'severity': 'INFO',
        },
    },
}


def parse_function_call(content: str, func_name: str) -> List[Dict[str, Any]]:
    """
    Parse all calls to a function and extract arguments.
    Handles multi-line calls and nested parentheses.
    
    Args:
        content: File content to search
        func_name: Function name (e.g., 'show_metric_with_sparkline')
    
    Returns:
        List of dicts with 'key', 'raw_args', and parsed 'kwargs'
    """
    results = []
    
    # regex to find function name and opening parenthesis
    # ensures it's not part of another identifier
    pattern = re.compile(rf'(?<![a-zA-Z0-9_]){func_name}\s*\(')
    
    for match in pattern.finditer(content):
        start_idx = match.end()
        
        # Manually find the matching closing parenthesis
        depth = 1
        in_string = None
        i = start_idx
        
        while i < len(content) and depth > 0:
            char = content[i]
            
            # Handle strings (simplistic approach)
            if char in '"\'' and in_string is None:
                in_string = char
            elif char == in_string:
                # Check for basic escaped quotes
                if i > 0 and content[i-1] != '\\':
                    in_string = None
            elif in_string:
                pass
            # Handle parentheses
            elif char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            
            i += 1
            
        if depth == 0:
            args_str = content[start_idx:i-1]
            parsed = _parse_args_string(args_str)
            
            # Extract the key (usually 3rd positional arg for both sparkline and macro_card)
            key = None
            if 'pos_2' in parsed:
                key = parsed['pos_2'].strip("'\" ")
            
            results.append({
                'key': key,
                'raw_args': args_str.strip(),
                'kwargs': parsed,
            })
            
    return results


def _parse_args_string(args_str: str) -> Dict[str, str]:
    """
    Parse function arguments string into a dictionary.
    
    Handles:
    - Positional args: stored as pos_0, pos_1, ...
    - Keyword args: stored by name
    
    Example:
        "label, series, 'KEY', explanation_key=''"
        -> {'pos_0': 'label', 'pos_1': 'series', 'pos_2': "'KEY'",
            'explanation_key': "''"}
    """
    result = {}
    
    # Split by comma, but be careful with nested parentheses and strings
    args = _smart_split(args_str)
    
    pos_idx = 0
    for arg in args:
        arg = arg.strip()
        if not arg:
            continue
        
        # Check if keyword argument (contains '=')
        if '=' in arg and not arg.startswith("'") and not arg.startswith('"'):
            # Handle keyword argument
            parts = arg.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                result[key] = value
        else:
            # Positional argument
            result[f'pos_{pos_idx}'] = arg
            pos_idx += 1
    
    return result


def _smart_split(s: str) -> List[str]:
    """
    Split string by comma, respecting parentheses and quotes.
    """
    result = []
    current = []
    depth = 0
    in_string = None
    
    for char in s:
        if char in '"\'' and in_string is None:
            in_string = char
            current.append(char)
        elif char == in_string:
            in_string = None
            current.append(char)
        elif in_string:
            current.append(char)
        elif char == '(':
            depth += 1
            current.append(char)
        elif char == ')':
            depth -= 1
            current.append(char)
        elif char == ',' and depth == 0:
            result.append(''.join(current))
            current = []
        else:
            current.append(char)
    
    if current:
        result.append(''.join(current))
    
    return result


def check_element_warnings(func_name: str, kwargs: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Check parsed kwargs against element warning rules.
    
    Returns list of warnings found.
    """
    warnings = []
    
    rules = ELEMENT_WARNINGS.get(func_name, {})
    
    for arg_name, rule in rules.items():
        value = kwargs.get(arg_name)
        
        # Check for empty string
        if rule.get('check_empty') and value is not None:
            # Empty string is "''", '""', or ''
            if value in ("''", '""', ''):
                warnings.append({
                    'arg': arg_name,
                    'value': value,
                    'message': rule['message'],
                    'severity': rule['severity'],
                })
        
        # Check for False value
        if rule.get('check_false') and value is not None:
            if value.lower() in ('false',):
                warnings.append({
                    'arg': arg_name,
                    'value': value,
                    'message': rule['message'],
                    'severity': rule['severity'],
                })
    
    return warnings


# Expected function for each pattern (None = skip verification)
PATTERN_TO_FUNCTION = {
    'standard': 'show_metric_with_sparkline',
    'mom_yoy': 'display_macro_card',
    'calculated': 'show_metric_with_sparkline',
    'manual_calc': None,  # Custom logic in page
    'web_scrape': None,   # Custom fetch functions
    'api': None,          # Individual API calls
}

# Inverse mapping for error detection
FUNCTION_TO_EXPECTED_PATTERNS = {
    'show_metric_with_sparkline': ['standard', 'calculated'],
    'display_macro_card': ['mom_yoy'],
}


# =============================================================================
# DISPLAY PATTERN VERIFICATION
# =============================================================================

def verify_display_patterns(app_root: str) -> Dict[str, List[str]]:
    """
    Verify that all 100+ indicators are displayed with correct patterns.
    
    Scans all pages/*.py files to find:
    - show_metric_with_sparkline(label, series, key, ...)
    - display_macro_card(title, series, key, ...)
    - show_metric(label, series, unit, exp_key, ...)
    - Manual df/df_original access
    
    Args:
        app_root: Root directory of the application
    
    Returns:
        Dictionary with pattern classifications and error list
    """
    import os
    from .indicators import INDICATORS
    
    results = {
        'pattern_standard': [],      # Metrics with sparkline
        'pattern_detailed': [],      # Macro cards with MoM/YoY
        'pattern_manual': [],        # Manually handled in page code
        'pattern_special': [],       # API indicators (usually display handled elsewhere)
        'errors': [],                # Missing or malformed
    }
    
    found_indicators = set()
    usage_map = {} # key -> list of filenames
    
    # Scan all pages files
    pages_dir = os.path.join(app_root, 'pages')
    if not os.path.exists(pages_dir):
        results['errors'].append(f"Pages directory not found: {pages_dir}")
        return results
    
    # Robust patterns to find keys in various display functions
    # 1. show_metric_with_sparkline(label, series, 'KEY', ...)
    spark_pat = re.compile(r'show_metric_with_sparkline\s*\(\s*[^,]+,\s*[^,]+,\s*[\'"]([\w_]+)[\'"]', re.DOTALL)
    
    # 2. display_macro_card(title, series, 'KEY', ...)
    macro_pat = re.compile(r'display_macro_card\s*\(\s*[^,]+,\s*[^,]+,\s*[\'"]([\w_]+)[\'"]', re.DOTALL)
    
    # 3. show_metric(label, series, unit, 'EXP_KEY', ...) or explanation_key='KEY'
    metric_pat = re.compile(r'show_metric\s*\(\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*(?:explanation_key\s*=\s*)?[\'"]([\w_]+)[\'"]', re.DOTALL)
    
    # 4. General df access: df.get('KEY'), df['KEY'], df_original.get('KEY')
    df_pat = re.compile(r'(?:df|df_original)(?:\.get\(|\[)[\'"]([\w_]+)[\'"]', re.DOTALL)

    # 5. Richmond Fed custom fetch functions
    richmond_mfg_pat = re.compile(r'get_richmond_fed_survey\s*\(\s*\)', re.DOTALL)
    richmond_svc_pat = re.compile(r'get_richmond_fed_services_survey\s*\(\s*\)', re.DOTALL)

    # Scan each pages file
    for filename in sorted(os.listdir(pages_dir)):
        if not filename.endswith('.py'):
            continue
        
        filepath = os.path.join(pages_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find sparkline metrics
            for key in spark_pat.findall(content):
                found_indicators.add(key)
                if key not in usage_map: usage_map[key] = []
                if filename not in usage_map[key]: usage_map[key].append(filename)
                if not any(d['key'] == key for d in results['pattern_standard']):
                    results['pattern_standard'].append({'key': key, 'file': filename})
            
            # Find macro cards
            for key in macro_pat.findall(content):
                found_indicators.add(key)
                if key not in usage_map: usage_map[key] = []
                if filename not in usage_map[key]: usage_map[key].append(filename)
                results['pattern_detailed'].append({'key': key, 'file': filename})
            
            # =========================================================
            # PHASE 3.5: Parse function arguments for element warnings
            # =========================================================
            # Initialize element_warnings list if not exists
            if 'element_warnings' not in results:
                results['element_warnings'] = []
            
            # Check show_metric_with_sparkline calls
            for call_info in parse_function_call(content, 'show_metric_with_sparkline'):
                if call_info['key']:
                    warnings = check_element_warnings('show_metric_with_sparkline', call_info['kwargs'])
                    for w in warnings:
                        results['element_warnings'].append({
                            'key': call_info['key'],
                            'file': filename,
                            'function': 'show_metric_with_sparkline',
                            'arg': w['arg'],
                            'value': w['value'],
                            'message': w['message'],
                            'severity': w['severity'],
                        })
            
            # Check display_macro_card calls
            for call_info in parse_function_call(content, 'display_macro_card'):
                if call_info['key']:
                    warnings = check_element_warnings('display_macro_card', call_info['kwargs'])
                    for w in warnings:
                        results['element_warnings'].append({
                            'key': call_info['key'],
                            'file': filename,
                            'function': 'display_macro_card',
                            'arg': w['arg'],
                            'value': w['value'],
                            'message': w['message'],
                            'severity': w['severity'],
                        })
            
            # Find other metrics or df access (manual handling)
            for key in metric_pat.findall(content):
                if key not in found_indicators:
                    found_indicators.add(key)
                    if key not in usage_map: usage_map[key] = []
                    if filename not in usage_map[key]: usage_map[key].append(filename)
                    results['pattern_manual'].append({'key': key, 'file': filename, 'type': 'show_metric'})

            for key in df_pat.findall(content):
                if key not in found_indicators:
                    # Only count as manual if it belongs to INDICATORS
                    if key in INDICATORS:
                        found_indicators.add(key)
                        if key not in usage_map: usage_map[key] = []
                        if filename not in usage_map[key]: usage_map[key].append(filename)
                        results['pattern_manual'].append({'key': key, 'file': filename, 'type': 'manual_data_access'})

            # Find Richmond Fed custom fetches
            if richmond_mfg_pat.search(content):
                key = 'Richmond_Fed_Mfg'
                if key not in found_indicators:
                    found_indicators.add(key)
                    if key not in usage_map: usage_map[key] = []
                    if filename not in usage_map[key]: usage_map[key].append(filename)
                    results['pattern_manual'].append({'key': key, 'file': filename, 'type': 'custom_fetch'})

            if richmond_svc_pat.search(content):
                key = 'Richmond_Fed_Services'
                if key not in found_indicators:
                    found_indicators.add(key)
                    if key not in usage_map: usage_map[key] = []
                    if filename not in usage_map[key]: usage_map[key].append(filename)
                    results['pattern_manual'].append({'key': key, 'file': filename, 'type': 'custom_fetch'})
        
        except Exception as e:
            results['errors'].append(f"Error reading {filename}: {str(e)}")
    
    # =========================================================================
    # PATTERN-TO-FUNCTION CONSISTENCY CHECK (New in 2026-01-26)
    # =========================================================================
    results['pattern_mismatches'] = []  # New category for mismatches
    
    # Build lookup: key -> {function_used, file}
    function_usage = {}
    for item in results['pattern_standard']:
        function_usage[item['key']] = {'function': 'show_metric_with_sparkline', 'file': item['file']}
    for item in results['pattern_detailed']:
        function_usage[item['key']] = {'function': 'display_macro_card', 'file': item['file']}
    
    # Check each indicator's expected vs actual function
    for key, config in INDICATORS.items():
        pattern = config.get('display_pattern', 'standard')
        expected_func = PATTERN_TO_FUNCTION.get(pattern)
        
        # Skip patterns that don't have expected functions (manual_calc, web_scrape, api)
        if expected_func is None:
            continue
        
        # Check if indicator was found with a specific function
        if key in function_usage:
            actual_func = function_usage[key]['function']
            actual_file = function_usage[key]['file']
            
            if actual_func != expected_func:
                results['pattern_mismatches'].append({
                    'key': key,
                    'pattern': pattern,
                    'expected': expected_func,
                    'actual': actual_func,
                    'file': actual_file,
                })
    
    # Final classification of all registry indicators
    for key, config in INDICATORS.items():
        if key in found_indicators:
            continue
            
        # API indicators are often displayed in custom sections (Sentiment, Tokenized assets)
        if config.get('df_stored', True) is False:
            results['pattern_special'].append({
                'key': key,
                'reason': 'API indicator (likely custom display)'
            })
        else:
            results['errors'].append(f"Indicator not found in any pages file: {key}")
    
    return results


def print_pattern_verification_report(results: Dict[str, List]) -> None:
    """Print human-readable report of display pattern verification"""
    
    print("=" * 80)
    print("DISPLAY PATTERN VERIFICATION REPORT")
    print("=" * 80)
    
    total_found = (len(results['pattern_standard']) + 
                  len(results['pattern_detailed']) + 
                  len(results['pattern_manual']) + 
                  len(results['pattern_special']))
    
    print(f"\nTotal indicators found in pages: {total_found}")
    print(f"[OK] Standard (Sparkline): {len(results['pattern_standard'])}")
    print(f"[OK] Detailed (Macro Card): {len(results['pattern_detailed'])}")
    print(f"[OK] Manual (Page Code): {len(results['pattern_manual'])}")
    print(f"[INFO] Special (API-based): {len(results['pattern_special'])}")
    print(f"[FAIL] Missing/Errors: {len(results['errors'])}")
    
    # Phase 3.5: Element composition summary
    element_warnings = results.get('element_warnings', [])
    if element_warnings:
        warn_count = sum(1 for w in element_warnings if w['severity'] == 'WARN')
        info_count = sum(1 for w in element_warnings if w['severity'] == 'INFO')
        print(f"[WARN] Element Warnings: {warn_count}")
        print(f"[INFO] Element Info: {info_count}")
    
    # Standard pattern
    if results['pattern_standard']:
        print("\n" + "-" * 80)
        print(f"STANDARD SPARKLINE PATTERN ({len(results['pattern_standard'])} indicators)")
        print("-" * 80)
        by_file = {}
        for item in results['pattern_standard']:
            file = item['file']
            if file not in by_file: by_file[file] = []
            by_file[file].append(item['key'])
        
        for file in sorted(by_file.keys()):
            print(f"\n{file}:")
            for key in sorted(by_file[file]):
                print(f"  - {key}")
    
    # Detailed pattern
    if results['pattern_detailed']:
        print("\n" + "-" * 80)
        print(f"DETAILED MACRO CARD PATTERN ({len(results['pattern_detailed'])} indicators)")
        print("-" * 80)
        by_file = {}
        for item in results['pattern_detailed']:
            file = item['file']
            if file not in by_file: by_file[file] = []
            by_file[file].append(item['key'])
        
        for file in sorted(by_file.keys()):
            print(f"\n{file}:")
            for key in sorted(by_file[file]):
                print(f"  - {key}")

    # Manual pattern
    if results['pattern_manual']:
        print("\n" + "-" * 80)
        print(f"MANUAL DISPLAY PATTERN ({len(results['pattern_manual'])} indicators)")
        print("-" * 80)
        for item in results['pattern_manual']:
            print(f"  {item['key']:<20} -> {item['file']} ({item['type']})")
    
    # Special patterns
    if results['pattern_special']:
        print("\n" + "-" * 80)
        print(f"SPECIAL/API INDICATORS ({len(results['pattern_special'])} indicators)")
        print("-" * 80)
        for item in results['pattern_special']:
            print(f"  {item['key']:<20} -> {item['reason']}")
            
    # Pattern Mismatches
    mismatches = results.get('pattern_mismatches', [])
    if mismatches:
        print("\n" + "=" * 80)
        print(f"PATTERN-FUNCTION MISMATCHES ({len(mismatches)}) - SPEC VIOLATIONS!")
        print("=" * 80)
        for item in mismatches:
            print(f"  [FAIL] {item['key']}")
            print(f"         Pattern: {item['pattern']} -> Expected: {item['expected']}")
            print(f"         Actual: {item['actual']} in {item['file']}")
    
    # =========================================================================
    # PHASE 3.5: Element Composition Warnings
    # =========================================================================
    element_warnings = results.get('element_warnings', [])
    if element_warnings:
        # Group by severity
        warn_items = [w for w in element_warnings if w['severity'] == 'WARN']
        info_items = [w for w in element_warnings if w['severity'] == 'INFO']
        
        if warn_items:
            print("\n" + "-" * 80)
            print(f"ELEMENT COMPOSITION WARNINGS ({len(warn_items)} items) - Phase 3.5")
            print("-" * 80)
            for item in warn_items:
                print(f"  [WARN] {item['key']} ({item['file']})")
                print(f"         {item['function']}: {item['message']}")
        
        if info_items:
            print("\n" + "-" * 80)
            print(f"ELEMENT COMPOSITION INFO ({len(info_items)} items)")
            print("-" * 80)
            # Group by file for cleaner output
            by_file = {}
            for item in info_items:
                file = item['file']
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(item)
            
            for file in sorted(by_file.keys()):
                print(f"  {file}:")
                for item in by_file[file]:
                    print(f"    [INFO] {item['key']}: {item['message']}")
    
    # Errors
    if results['errors']:
        print("\n" + "=" * 80)
        print(f"ERRORS / MISSING ({len(results['errors'])})")
        print("=" * 80)
        for error in sorted(results['errors']):
            print(f"  [FAIL] {error}")
    
    # Final Summary
    print("\n" + "=" * 80)
    total_issues = len(mismatches) + len(results['errors'])
    if total_issues == 0:
        print("[OK] All patterns match their expected display functions!")
    else:
        print(f"[FAIL] {total_issues} issue(s) found - see above")
        
        # 初心者向けアクション提案
        print("\n" + "-" * 80)
        print("SUGGESTED ACTIONS (修正方法):")
        print("-" * 80)
        
        if mismatches:
            print("\n[Pattern Mismatch] 表示関数が仕様と一致しません:")
            print("  -> docs/DISPLAY_SPEC.md の「パターンと表示関数の対応」を確認")
            print("  -> standard パターン: show_metric_with_sparkline() を使用")
            print("  -> mom_yoy パターン: display_macro_card() を使用")
        
        if results['errors']:
            missing_count = sum(1 for e in results['errors'] if 'not found' in e)
            if missing_count > 0:
                print(f"\n[Missing Indicator] {missing_count}個の指標がページに見つかりません:")
                print("  -> 該当ページの pages/*.py を確認")
                print("  -> show_metric_with_sparkline() の呼び出しを追加")
                print("  -> または indicators.py の ui_page 設定を確認")
        
        # Phase 3.5 warnings advice
        element_warnings = results.get('element_warnings', [])
        warn_items = [w for w in element_warnings if w['severity'] == 'WARN']
        if warn_items:
            print(f"\n[Element Warning] {len(warn_items)}個の構成要素警告:")
            print("  -> explanation_key が空: help_text が表示されない可能性")
            print("  -> show_level=False: レベルメトリクスが非表示")
            print("  -> docs/DISPLAY_SPEC.md の9要素仕様を確認")
    
    print("=" * 80)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    import sys
    import os
    
    # Check if --verify-patterns flag is provided
    if '--verify-patterns' in sys.argv:
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"Verifying display patterns in: {app_root}")
        print()
        
        results = verify_display_patterns(app_root)
        print_pattern_verification_report(results)
        
        # Exit with error if any errors or mismatches found
        if results['errors'] or results.get('pattern_mismatches', []):
            sys.exit(1)
        sys.exit(0)
    
    # Otherwise run normal display check
    print("Display Checker - Static Mode (no data)")
    from .indicators import INDICATORS
    print(f"Checking {len(INDICATORS)} indicators...")
    print(f"Patterns: {list(PATTERN_SPECS.keys())}")
    print()
    
    verbose = '-v' in sys.argv or '--verbose' in sys.argv
    checker = run_static_check(verbose=verbose)
    
    # Exit with error code if failures
    if checker.get_summary()['failed'] > 0:
        sys.exit(1)
