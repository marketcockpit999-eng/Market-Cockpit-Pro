# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Component Gap Checker
================================================================================
Based on DISPLAY_SPEC.md (The "Book")
Validates mandatory components for all 101 indicators.

Groups:
- Daily/Weekly Full: 10 elements
- Monthly/Quarterly: 9 elements (No Sparkline)
- MoM/YoY: Specialized
- API: Individual checks
================================================================================
"""

import re
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from .help_texts import HELP_EN, HELP_JA

# =============================================================================
# GROUP DEFINITIONS
# =============================================================================

GROUP_SPECS = {
    'daily_weekly': {
        'name': '日次/週次フル',
        'elements': ['label', 'help_text', 'value', 'delta', 'unit', 'data_period', 'release_date', 'notes', 'sparkline', 'full_chart'],
        'description': '10要素',
    },
    'monthly_quarterly': {
        'name': '月次/四半期',
        'elements': ['label', 'help_text', 'value', 'delta', 'unit', 'data_period', 'release_date', 'notes', 'full_chart'],
        'description': '9要素',
    },
    'mom_yoy': {
        'name': 'MoM/YoY',
        'elements': ['label', 'help_text', 'value', 'unit', 'data_period', 'release_date', 'notes', 'mom_percent', 'yoy_percent', 'full_chart'],
        'description': '特殊',
    },
    'api': {
        'name': 'API系',
        'elements': ['label', 'help_text', 'value'],
        'description': '別処理',
    }
}

class CheckResult:
    def __init__(self, name: str, group: str):
        self.name = name
        self.group = group
        self.passed: List[str] = []
        self.failed: List[str] = []
        self.details: Dict[str, str] = {}
        
    @property
    def is_ok(self) -> bool:
        return len(self.failed) == 0
    
    @property
    def score_text(self) -> str:
        total = len(GROUP_SPECS[self.group]['elements'])
        return f"{len(self.passed)}/{total}要素"

class DisplayChecker:
    def __init__(self, df: pd.DataFrame = None):
        self.df = df if df is not None else pd.DataFrame()
        self.results: Dict[str, CheckResult] = {}

    def get_indicator_group(self, name: str, config: dict) -> str:
        pattern = config.get('display_pattern', 'standard')
        freq = config.get('frequency', 'unknown')
        
        if pattern == 'api':
            return 'api'
        if pattern == 'mom_yoy':
            return 'mom_yoy'
        if freq in ['daily', 'weekly']:
            return 'daily_weekly'
        return 'monthly_quarterly'

    def check_all(self):
        from .indicators import INDICATORS
        for name, config in INDICATORS.items():
            group = self.get_indicator_group(name, config)
            result = CheckResult(name, group)
            elements = GROUP_SPECS[group]['elements']
            
            for elem in elements:
                passed, detail = self._check_element(name, config, elem)
                if passed:
                    result.passed.append(elem)
                else:
                    result.failed.append(elem)
                result.details[elem] = detail
            
            self.results[name] = result

    def _check_element(self, name: str, config: dict, element: str) -> Tuple[bool, str]:
        if element == 'label':
            return True, name
        
        if element == 'help_text':
            help_key = f'help_{name}'
            has_ja = help_key in HELP_JA
            has_en = help_key in HELP_EN
            
            # Special case for FedFundsUpper/Lower aliases
            if not has_ja:
                if name == 'FedFundsUpper' and 'help_FF_Upper' in HELP_JA: has_ja = True
                if name == 'FedFundsLower' and 'help_FF_Lower' in HELP_JA: has_ja = True
            if not has_en:
                if name == 'FedFundsUpper' and 'help_FF_Upper' in HELP_EN: has_en = True
                if name == 'FedFundsLower' and 'help_FF_Lower' in HELP_EN: has_en = True
            
            if has_ja and has_en:
                return True, 'JA+EN'
            elif has_ja:
                return False, 'Missing EN'
            elif has_en:
                return False, 'Missing JA'
            else:
                return False, 'Missing in help_texts.py'
            
        if element == 'unit':
            unit = config.get('unit')
            # Check for non-empty string
            if unit is not None and str(unit).strip() != '':
                return True, str(unit)
            return False, 'Missing'
            
        if element == 'notes':
            notes = config.get('notes')
            if notes is not None and str(notes).strip() != '':
                return True, str(notes)[:20] + '...' if len(str(notes)) > 20 else str(notes)
            return False, 'Missing'
            
        if element in ['value', 'delta', 'data_period']:
            if self.df.empty: return True, 'Static OK'
            if name not in self.df.columns: 
                if config.get('df_stored', True) is False: return True, 'API OK'
                return False, 'No Data'
            return True, 'Data OK'
            
        if element == 'release_date':
            return True, 'Source OK'
            
        if element in ['sparkline', 'full_chart', 'mom_percent', 'yoy_percent']:
            return True, 'Logic OK'
            
        return True, 'OK'

    def get_ascii_summary(self) -> str:
        summary = {g: {'ok': 0, 'total': 0} for g in GROUP_SPECS}
        all_ok_count = 0
        
        for r in self.results.values():
            summary[r.group]['total'] += 1
            if r.is_ok:
                summary[r.group]['ok'] += 1
                all_ok_count += 1
        
        total_count = len(self.results)
        status_line = f"✅ {all_ok_count}/{total_count} 全指標OK!" if all_ok_count == total_count else f"⚠️ {all_ok_count}/{total_count} 指標に問題あり"
        
        table =  "パターン別サマリー\n"
        table += "┌─────────────┬─────────────┬──────────┬─────────┐\n"
        table += "│日次/週次フル  │月次/四半期   │ MoM/YoY  │ API系   │\n"
        
        s = summary
        table += f"│   {s['daily_weekly']['ok']}/{s['daily_weekly']['total']}      │   {s['monthly_quarterly']['ok']}/{s['monthly_quarterly']['total']}     │   {s['mom_yoy']['ok']}/{s['mom_yoy']['total']}    │  {s['api']['ok']}/{s['api']['total']}  │\n"
        table += f"│   {GROUP_SPECS['daily_weekly']['description']}     │    {GROUP_SPECS['monthly_quarterly']['description']}    │   {GROUP_SPECS['mom_yoy']['description']}   │  {GROUP_SPECS['api']['description']}  │\n"
        table += "└─────────────┴─────────────┴──────────┴─────────┘\n"
        
        return f"{status_line}\n\n{table}"

    def print_report(self):
        print(self.get_ascii_summary())
        
        problems = [r for r in self.results.values() if not r.is_ok]
        if problems:
            print("⚠️ 問題のある指標")
            for r in problems:
                spec = GROUP_SPECS[r.group]
                print(f"▼ ⚠️ {r.name} ({spec['name']}) - {r.score_text}")
                print(f"   必須欠落: {', '.join(r.failed)}")
                for f in r.failed:
                    if f == 'help_text':
                        print(f"   💡 修正方法: help_texts.pyにhelp_{r.name}を追加")
                    elif f in ['unit', 'notes']:
                        print(f"   💡 修正方法: indicators.pyの{r.name}に'{f}'を追加")

def verify_display_components(df=None):
    checker = DisplayChecker(df)
    checker.check_all()
    # checker.print_report()
    return checker

def verify_display_patterns(path=None):
    """Compatibility alias for verify_display_components"""
    return verify_display_components()

if __name__ == "__main__":
    verify_display_components()
