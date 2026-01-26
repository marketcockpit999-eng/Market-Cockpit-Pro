# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Auto Render System
================================================================================
自動レンダリングシステム - indicators.pyの定義から指標を自動表示

設計思想：
  - indicators.pyに定義があれば、自動的に表示される
  - 「消えない構造」= 表示コードを個別に書かない
  - display_patternに基づいて適切な表示関数を呼び出す

Usage:
    from utils.auto_render import render_indicator, render_indicators_for_page
    
    # 個別指標を表示
    render_indicator(df, 'ON_RRP')
    
    # ページの全指標を表示
    render_indicators_for_page(df, '01_liquidity')
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import uuid

from .indicators import INDICATORS, get_indicators_for_page
from .i18n import t
from .config import DATA_FREQUENCY
from .data_processor import get_freshness_badge, get_mom_yoy
from .charts import show_metric_with_sparkline, display_macro_card, styled_line_chart


# =============================================================================
# CORE RENDER FUNCTIONS
# =============================================================================

def render_indicator(df, key: str, config: dict = None, show_chart: bool = True):
    """
    単一指標をレンダリング
    
    Args:
        df: データフレーム
        key: 指標キー (例: 'ON_RRP')
        config: 指標設定 (Noneの場合はINDICATORSから取得)
        show_chart: 長期チャートを表示するか
    
    Returns:
        bool: レンダリング成功したかどうか
    """
    if config is None:
        config = INDICATORS.get(key)
    
    if config is None:
        st.warning(f"⚠️ Unknown indicator: {key}")
        return False
    
    pattern = config.get('display_pattern', 'standard')
    
    # パターン別のレンダリング
    if pattern == 'standard':
        return _render_standard(df, key, config, show_chart)
    elif pattern == 'mom_yoy':
        return _render_mom_yoy(df, key, config, show_chart)
    elif pattern == 'manual_calc':
        return _render_manual_calc(df, key, config, show_chart)
    elif pattern == 'api':
        return _render_api(df, key, config)
    elif pattern == 'web_scrape':
        return _render_web_scrape(df, key, config)
    elif pattern == 'calculated':
        return _render_calculated(df, key, config, show_chart)
    else:
        # Unknown pattern - fallback to standard
        st.warning(f"⚠️ Unknown display_pattern '{pattern}' for {key}, using standard")
        return _render_standard(df, key, config, show_chart)


def render_indicators_for_page(df, page_name: str, section: str = None):
    """
    ページの全指標を自動レンダリング
    
    Args:
        df: データフレーム
        page_name: ページ名 (例: '01_liquidity')
        section: 特定セクションのみ表示 (Noneで全セクション)
    
    Returns:
        dict: {key: success} のレンダリング結果
    """
    indicators = get_indicators_for_page(page_name)
    
    if not indicators:
        st.info(f"No indicators defined for page: {page_name}")
        return {}
    
    results = {}
    for key, config in indicators.items():
        # セクションフィルタ（将来実装用）
        if section and config.get('ui_section') != section:
            continue
        
        results[key] = render_indicator(df, key, config)
    
    return results


def get_render_stats(page_name: str = None):
    """
    レンダリング統計を取得
    
    Args:
        page_name: ページ名 (Noneで全ページ)
    
    Returns:
        dict: 統計情報
    """
    if page_name:
        indicators = get_indicators_for_page(page_name)
    else:
        indicators = INDICATORS
    
    stats = {
        'total': len(indicators),
        'by_pattern': {},
        'by_source': {},
    }
    
    for key, config in indicators.items():
        pattern = config.get('display_pattern', 'standard')
        source = config.get('source', 'UNKNOWN')
        
        stats['by_pattern'][pattern] = stats['by_pattern'].get(pattern, 0) + 1
        stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
    
    return stats


# =============================================================================
# PATTERN-SPECIFIC RENDERERS
# =============================================================================

def _render_standard(df, key: str, config: dict, show_chart: bool = True) -> bool:
    """
    標準パターン: show_metric_with_sparkline + optional long-term chart
    
    対象: ON_RRP, Reserves, TGA, SOMA系, 金利系, VIX, Gold, BTC, etc.
    構成要素:
      1. メトリック（値、変化）
      2. 日付情報
      3. スパークライン (daily/weekly)
      4. 長期チャート (optional)
    """
    series = df.get(key) if df is not None else None
    
    if series is None or (hasattr(series, 'isna') and series.isna().all()):
        st.metric(t(f'indicator_{key}', key), "N/A")
        return False
    
    # 基本設定
    unit = config.get('unit', '')
    notes = config.get('notes', '')
    decimal_places = 2 if unit == '%' else 1
    
    # Alert function based on validation range
    alert_func = None
    validation = config.get('validation')
    if validation:
        min_val, max_val = validation
        # Alert if value is near the extremes (within 10%)
        range_size = max_val - min_val
        alert_func = lambda x: x > (max_val - range_size * 0.1) or x < (min_val + range_size * 0.1)
    
    # Render with sparkline
    label = t(f'indicator_{key}', key)
    show_metric_with_sparkline(
        label=label,
        series=series,
        df_column=key,
        unit=unit,
        explanation_key=key,
        notes=notes,
        alert_func=alert_func,
        decimal_places=decimal_places
    )
    
    # Long-term chart (optional)
    if show_chart and key in df.columns and not df[key].isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[[key]], height=200)
    
    return True


def _render_mom_yoy(df, key: str, config: dict, show_chart: bool = True) -> bool:
    """
    前月比・前年比パターン: display_macro_card
    
    対象: CPI, CPICore, PPI, CorePCE, RetailSales, ConsumerSent
    構成要素:
      1. MoM% / YoY%
      2. 水準値
      3. YoY%トレンドチャート
      4. 長期水準チャート
    """
    df_original = st.session_state.get('df_original')
    series = df.get(key) if df is not None else None
    
    if series is None or (hasattr(series, 'isna') and series.isna().all()):
        st.metric(t(f'indicator_{key}', key), "N/A")
        return False
    
    unit = config.get('unit', '')
    notes = config.get('notes', '')
    freq = config.get('frequency', 'monthly')
    freq_code = 'M' if freq == 'monthly' else 'Q' if freq == 'quarterly' else 'D'
    
    label = t(f'indicator_{key}', key)
    display_macro_card(
        title=label,
        series=series,
        df_column=key,
        df_original=df_original,
        unit=unit,
        notes=notes,
        freq=freq_code,
        show_level=True
    )
    
    return True


def _render_manual_calc(df, key: str, config: dict, show_chart: bool = True) -> bool:
    """
    手動計算パターン: 特殊な計算が必要な指標
    
    対象: UNRATE, NFP, ADP, AvgHourlyEarnings, ICSA, RealGDP
    
    Note: これらは個別の計算ロジックが必要なため、
          現時点ではstandardにフォールバック。
          将来的に各指標の計算ロジックを追加。
    """
    # TODO: 個別の計算ロジックを実装
    # 現時点ではstandardにフォールバック
    return _render_standard(df, key, config, show_chart)


def _render_api(df, key: str, config: dict) -> bool:
    """
    APIパターン: 別APIから取得する指標
    
    対象: SP500_PE, NASDAQ_PE, BTC_Funding_Rate, Stablecoin_Total, etc.
    
    Note: これらはdf_storedがFalseで、別途API呼び出しが必要。
          各ページで個別に実装されているため、ここではスキップ。
    """
    # API指標は各ページで個別処理
    # ここでは情報のみ表示
    st.caption(f"⚡ {key}: {config.get('notes', 'API indicator')}")
    return True


def _render_web_scrape(df, key: str, config: dict) -> bool:
    """
    Webスクレイピングパターン
    
    対象: Richmond_Fed_Mfg, Richmond_Fed_Services
    
    Note: 現時点では実装されていないため、プレースホルダー表示。
    """
    st.caption(f"🌐 {key}: {config.get('notes', 'Web scrape indicator')} - Not implemented")
    return False


def _render_calculated(df, key: str, config: dict, show_chart: bool = True) -> bool:
    """
    計算値パターン: 複数指標から計算される値
    
    対象: Global_Liquidity_Proxy
    """
    # 計算値はstandardと同様に表示
    return _render_standard(df, key, config, show_chart)


# =============================================================================
# LAYOUT HELPERS
# =============================================================================

def render_in_columns(df, keys: list, num_cols: int = 2, show_charts: bool = True):
    """
    複数指標をカラムレイアウトで表示
    
    Args:
        df: データフレーム
        keys: 指標キーのリスト
        num_cols: カラム数
        show_charts: チャートを表示するか
    """
    cols = st.columns(num_cols)
    
    for i, key in enumerate(keys):
        with cols[i % num_cols]:
            render_indicator(df, key, show_chart=show_charts)


def render_section(df, title: str, keys: list, num_cols: int = 2):
    """
    セクション（タイトル + 指標群）を表示
    
    Args:
        df: データフレーム
        title: セクションタイトル
        keys: 指標キーのリスト
        num_cols: カラム数
    """
    st.markdown(f"### {title}")
    render_in_columns(df, keys, num_cols)


# =============================================================================
# DEBUG / DEVELOPMENT HELPERS
# =============================================================================

def show_render_debug(page_name: str = None):
    """
    デバッグ情報を表示（開発用）
    """
    stats = get_render_stats(page_name)
    
    with st.expander("🔧 Render Debug Info"):
        st.write(f"**Total indicators:** {stats['total']}")
        
        st.write("**By pattern:**")
        for pattern, count in sorted(stats['by_pattern'].items()):
            st.write(f"  - {pattern}: {count}")
        
        st.write("**By source:**")
        for source, count in sorted(stats['by_source'].items()):
            st.write(f"  - {source}: {count}")


if __name__ == '__main__':
    # Quick test
    print("Auto Render System")
    print("=" * 40)
    
    stats = get_render_stats()
    print(f"Total indicators: {stats['total']}")
    print(f"By pattern: {stats['by_pattern']}")
    print(f"By source: {stats['by_source']}")
    
    print("\nPage breakdown:")
    for page in ['01_liquidity', '02_global_money', '03_us_economic', '04_crypto', '09_banking']:
        page_stats = get_render_stats(page)
        print(f"  {page}: {page_stats['total']} indicators")
