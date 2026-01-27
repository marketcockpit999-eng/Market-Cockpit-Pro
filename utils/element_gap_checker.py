# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Element Gap Checker
================================================================================
構成要素ギャップ検出: 各指標が「あるべき要素」を持っているか検証

パターン定義:
  A: 日次/週次フル (10要素) - 60日推移あり + 長期チャート
  B1: 月次/四半期シンプル (9要素) - 60日推移なし + 長期チャート
  B2: 月次MoM/YoY (特殊) - 前月比+前年比 + 2チャート
  API: 外部API系 - 別処理

2026-01-27 高橋さんのスクショに基づき作成
================================================================================
"""

from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
import pandas as pd

from .indicators import INDICATORS
from .help_texts import HELP_EN, HELP_JA


# =============================================================================
# パターン定義（高橋さんのスクショから）
# =============================================================================

ELEMENT_PATTERNS = {
    'A_daily_weekly': {
        'name': '日次/週次フル',
        'frequencies': ['daily', 'weekly'],
        'element_count': 10,
        'elements': {
            'mandatory': [
                'heading',           # 1. 大見出し
                'label',             # 2. 小さい項目名
                'help_icon',         # 3. ？ヘルプ
                'value',             # 4. 数値
                'delta',             # 5. 前日/前期比
                'data_period',       # 6. 📅 データ期間
                'release_date',      # 7. 🔄 提供元更新日
            ],
            'optional': [
                'notes',             # 8. 補足文
                'sparkline_60d',     # 9. 📊 60日推移
                'chart_2y',          # 10. 長期推移(2年)
            ],
        },
    },
    'B1_monthly_simple': {
        'name': '月次/四半期シンプル',
        'frequencies': ['monthly', 'quarterly'],
        'display_patterns': ['standard'],  # indicators.pyのdisplay_pattern
        'element_count': 9,
        'elements': {
            'mandatory': [
                'heading',
                'label',
                'help_icon',
                'value',
                'delta',
                'data_period',
                'release_date',
            ],
            'optional': [
                'notes',
                'chart_2y',          # 長期チャートのみ（60日なし）
            ],
        },
    },
    'B2_mom_yoy': {
        'name': '月次MoM/YoY',
        'frequencies': ['monthly'],
        'display_patterns': ['mom_yoy'],
        'element_count': 12,  # 特殊構成
        'elements': {
            'mandatory': [
                'heading',
                'mom_box',           # 前月比ボックス
                'yoy_box',           # 前年比ボックス
                'label',
                'value',
                'delta',
                'data_period',
                'release_date',
            ],
            'optional': [
                'notes',
                'chart_yoy',         # YoY%チャート
                'chart_level',       # Levelチャート
            ],
        },
    },
    'API_external': {
        'name': 'API系（別処理）',
        'df_stored': False,
        'element_count': 'varies',
        'elements': {
            'mandatory': [
                'label',
                'value',
            ],
            'optional': [
                'help_icon',
                'delta',
                'notes',
            ],
        },
    },
}


# =============================================================================
# 分類ロジック
# =============================================================================

def classify_indicator(name: str, config: dict) -> str:
    """
    指標を適切なパターンに分類
    
    Returns:
        パターンキー: 'A_daily_weekly', 'B1_monthly_simple', 'B2_mom_yoy', 'API_external', 'UNKNOWN'
    """
    freq = config.get('frequency', '')
    display = config.get('display_pattern', 'standard')
    df_stored = config.get('df_stored', True)
    
    # API系（dfに入らない）
    if df_stored == False or display == 'api':
        return 'API_external'
    
    # MoM/YoY パターン
    if display == 'mom_yoy':
        return 'B2_mom_yoy'
    
    # 日次/週次 → パターンA
    if freq in ['daily', 'weekly']:
        return 'A_daily_weekly'
    
    # 月次/四半期 → パターンB1
    if freq in ['monthly', 'quarterly']:
        return 'B1_monthly_simple'
    
    return 'UNKNOWN'


def classify_all_indicators() -> Dict[str, List[str]]:
    """
    全指標をパターン別に分類
    
    Returns:
        {パターン: [指標名リスト]}
    """
    results = {
        'A_daily_weekly': [],
        'B1_monthly_simple': [],
        'B2_mom_yoy': [],
        'API_external': [],
        'UNKNOWN': [],
    }
    
    for name, config in INDICATORS.items():
        pattern = classify_indicator(name, config)
        results[pattern].append(name)
    
    return results


# =============================================================================
# 要素チェックロジック
# =============================================================================

class ElementGapChecker:
    """構成要素ギャップ検出クラス"""
    
    def __init__(self, df: pd.DataFrame = None):
        self.df = df if df is not None else pd.DataFrame()
        self.results: Dict[str, Dict] = {}
    
    def check_all(self) -> Dict[str, Dict]:
        """全指標をチェック"""
        for name, config in INDICATORS.items():
            self.results[name] = self.check_indicator(name, config)
        return self.results
    
    def check_indicator(self, name: str, config: dict) -> Dict[str, Any]:
        """
        単一指標の構成要素をチェック
        
        Returns:
            {
                'pattern': パターン名,
                'expected': 期待要素数,
                'present': 存在要素数,
                'missing': [欠落要素リスト],
                'status': 'OK' / 'WARN' / 'FAIL'
            }
        """
        pattern_key = classify_indicator(name, config)
        pattern_spec = ELEMENT_PATTERNS.get(pattern_key, {})
        
        result = {
            'pattern': pattern_spec.get('name', pattern_key),
            'pattern_key': pattern_key,
            'expected': pattern_spec.get('element_count', '?'),
            'present': 0,
            'missing_mandatory': [],
            'missing_optional': [],
            'status': 'OK',
        }
        
        if not pattern_spec:
            result['status'] = 'UNKNOWN'
            return result
        
        elements = pattern_spec.get('elements', {})
        mandatory = elements.get('mandatory', [])
        optional = elements.get('optional', [])
        
        present_count = 0
        
        # 必須要素チェック
        for elem in mandatory:
            has_element, detail = self._check_element(name, config, elem)
            if has_element:
                present_count += 1
            else:
                result['missing_mandatory'].append(elem)
        
        # オプション要素チェック
        for elem in optional:
            has_element, detail = self._check_element(name, config, elem)
            if has_element:
                present_count += 1
            else:
                result['missing_optional'].append(elem)
        
        result['present'] = present_count
        
        # ステータス判定
        if result['missing_mandatory']:
            result['status'] = 'FAIL'
        elif result['missing_optional']:
            result['status'] = 'WARN'
        else:
            result['status'] = 'OK'
        
        return result
    
    def _check_element(self, name: str, config: dict, element: str) -> Tuple[bool, str]:
        """
        個別要素のチェック
        
        Returns:
            (存在するか, 詳細メッセージ)
        """
        
        if element in ['heading', 'label']:
            # 常に存在（指標名から生成）
            return True, name
        
        elif element == 'help_icon':
            # ヘルプテキストが登録されているか
            help_key = f'help_{name}'
            has_help = help_key in HELP_EN or help_key in HELP_JA
            return has_help, f'{help_key} in help_texts'
        
        elif element == 'value':
            # dfにデータがあるか（API系は別処理）
            if config.get('df_stored', True) == False:
                return True, 'API indicator'
            if self.df.empty:
                return True, 'Data check skipped'
            if name in self.df.columns:
                valid = self.df[name].dropna()
                if len(valid) > 0:
                    return True, f'Latest: {valid.iloc[-1]}'
            return False, 'No data'
        
        elif element == 'delta':
            # 前期比計算用データがあるか
            if self.df.empty:
                return True, 'Data check skipped'
            if name in self.df.columns:
                valid = self.df[name].dropna()
                return len(valid) >= 2, f'{len(valid)} points'
            return False, 'No data'
        
        elif element == 'data_period':
            # df.attrsにlast_valid_datesがあるか
            if self.df.empty:
                return True, 'Data check skipped'
            if hasattr(self.df, 'attrs'):
                last_dates = self.df.attrs.get('last_valid_dates', {})
                if name in last_dates:
                    return True, str(last_dates[name])
            # dfのインデックスから推定可能
            if name in self.df.columns:
                return True, 'From index'
            return False, 'Not available'
        
        elif element == 'release_date':
            # FREDの場合はrelease_date、YAHOOの場合はlast_valid_date
            if self.df.empty:
                return True, 'Data check skipped'
            source = config.get('source', '')
            if source == 'FRED':
                if hasattr(self.df, 'attrs'):
                    release_dates = self.df.attrs.get('fred_release_dates', {})
                    if name in release_dates:
                        return True, str(release_dates[name])
            # YAHOOはlast_valid_dateをfallbackとして使用
            return True, f'Source: {source}'
        
        elif element == 'notes':
            # config['notes']があるか
            notes = config.get('notes', '')
            return bool(notes), notes[:30] if notes else 'No notes'
        
        elif element == 'sparkline_60d':
            # 60日分のデータがあるか
            if self.df.empty:
                return True, 'Data check skipped'
            if name in self.df.columns:
                valid = self.df[name].dropna().tail(60)
                return len(valid) >= 10, f'{len(valid)} points'
            return False, 'No data'
        
        elif element in ['chart_2y', 'chart_yoy', 'chart_level']:
            # 長期データがあるか
            if self.df.empty:
                return True, 'Data check skipped'
            if name in self.df.columns:
                valid = self.df[name].dropna()
                return len(valid) >= 30, f'{len(valid)} points'
            return False, 'No data'
        
        elif element in ['mom_box', 'yoy_box']:
            # MoM/YoYパターン用
            if self.df.empty:
                return True, 'Data check skipped'
            if name in self.df.columns:
                valid = self.df[name].dropna()
                if element == 'yoy_box':
                    return len(valid) >= 13, f'{len(valid)} points (need 13 for YoY)'
                return len(valid) >= 2, f'{len(valid)} points'
            return False, 'No data'
        
        else:
            return True, f'Unknown element: {element}'
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー統計を取得"""
        total = len(self.results)
        ok_count = sum(1 for r in self.results.values() if r['status'] == 'OK')
        warn_count = sum(1 for r in self.results.values() if r['status'] == 'WARN')
        fail_count = sum(1 for r in self.results.values() if r['status'] == 'FAIL')
        unknown_count = sum(1 for r in self.results.values() if r['status'] == 'UNKNOWN')
        
        # パターン別集計
        by_pattern = {}
        for name, result in self.results.items():
            pattern = result['pattern']
            if pattern not in by_pattern:
                by_pattern[pattern] = {'total': 0, 'ok': 0, 'warn': 0, 'fail': 0}
            by_pattern[pattern]['total'] += 1
            if result['status'] == 'OK':
                by_pattern[pattern]['ok'] += 1
            elif result['status'] == 'WARN':
                by_pattern[pattern]['warn'] += 1
            elif result['status'] == 'FAIL':
                by_pattern[pattern]['fail'] += 1
        
        return {
            'total': total,
            'ok': ok_count,
            'warn': warn_count,
            'fail': fail_count,
            'unknown': unknown_count,
            'score': f'{ok_count}/{total}',
            'by_pattern': by_pattern,
        }
    
    def get_problem_indicators(self) -> List[Tuple[str, Dict]]:
        """問題のある指標を取得（FAIL + WARN）"""
        problems = []
        for name, result in self.results.items():
            if result['status'] in ['FAIL', 'WARN']:
                problems.append((name, result))
        return sorted(problems, key=lambda x: (x[1]['status'] != 'FAIL', x[0]))


# =============================================================================
# 便利関数
# =============================================================================

def run_element_gap_check(df: pd.DataFrame = None) -> ElementGapChecker:
    """
    構成要素ギャップチェックを実行
    
    Args:
        df: メインDataFrame（Noneの場合は静的チェックのみ）
    
    Returns:
        ElementGapChecker インスタンス
    """
    checker = ElementGapChecker(df)
    checker.check_all()
    return checker


def print_gap_report(checker: ElementGapChecker):
    """ギャップレポートを出力"""
    summary = checker.get_summary()
    
    print("=" * 70)
    print("📊 構成要素ギャップチェック")
    print("=" * 70)
    print(f"\nスコア: {summary['score']}")
    print(f"  ✅ OK: {summary['ok']}")
    print(f"  ⚠️ WARN: {summary['warn']}")
    print(f"  ❌ FAIL: {summary['fail']}")
    print(f"  ❓ UNKNOWN: {summary['unknown']}")
    
    print("\n--- パターン別 ---")
    for pattern, stats in summary['by_pattern'].items():
        print(f"  {pattern}: {stats['ok']}/{stats['total']} OK")
    
    problems = checker.get_problem_indicators()
    if problems:
        print("\n" + "=" * 70)
        print("問題のある指標")
        print("=" * 70)
        for name, result in problems:
            status_icon = '❌' if result['status'] == 'FAIL' else '⚠️'
            print(f"\n{status_icon} {name} ({result['pattern']})")
            print(f"   要素: {result['present']}/{result['expected']}")
            if result['missing_mandatory']:
                print(f"   必須欠落: {', '.join(result['missing_mandatory'])}")
            if result['missing_optional']:
                print(f"   オプション欠落: {', '.join(result['missing_optional'])}")


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    print("構成要素ギャップチェッカー（静的モード）")
    print()
    
    # 分類結果を表示
    classification = classify_all_indicators()
    print("=== パターン分類 ===")
    for pattern, indicators in classification.items():
        pattern_name = ELEMENT_PATTERNS.get(pattern, {}).get('name', pattern)
        print(f"\n{pattern_name}: {len(indicators)}項目")
        for name in sorted(indicators)[:5]:  # 最初の5つだけ表示
            print(f"  - {name}")
        if len(indicators) > 5:
            print(f"  ... and {len(indicators) - 5} more")
    
    print()
    
    # ギャップチェック
    checker = run_element_gap_check()
    print_gap_report(checker)
