# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Auto Render System v2
================================================================================
自動レンダリングシステム - 完全自動化版

page_layouts.pyの定義に基づいて、ページ全体を自動レンダリング。
「消えない構造」= indicators.py + page_layouts.py に定義があれば自動表示。

Usage:
    from utils.auto_render import render_page
    
    # ページ全体を自動レンダリング
    render_page(df, '01_liquidity')
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import uuid

from .indicators import INDICATORS, get_indicators_for_page
from .page_layouts import PAGE_LAYOUTS, get_page_layout
from .i18n import t
from .config import DATA_FREQUENCY
from .data_processor import get_freshness_badge, get_mom_yoy
from .charts import (
    show_metric_with_sparkline, 
    display_macro_card, 
    styled_line_chart,
    show_metric,
    plot_dual_axis,
    plot_soma_composition,
)


# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================

def render_page(df, page_name: str, show_debug: bool = False):
    """
    ページ全体を自動レンダリング
    
    Args:
        df: データフレーム
        page_name: ページ名 (例: '01_liquidity')
        show_debug: デバッグ情報を表示
    
    Returns:
        dict: レンダリング結果統計
    """
    layout = get_page_layout(page_name)
    
    if not layout:
        st.error(f"No layout defined for page: {page_name}")
        return {'success': False, 'error': 'No layout'}
    
    # Page title
    title_key = layout.get('title_key', page_name)
    st.subheader(t(title_key))
    
    stats = {
        'sections_rendered': 0,
        'indicators_rendered': 0,
        'errors': [],
    }
    
    # Render each section
    for section in layout.get('sections', []):
        try:
            rendered = _render_section(df, section)
            stats['sections_rendered'] += 1
            stats['indicators_rendered'] += rendered
        except Exception as e:
            stats['errors'].append(f"{section['id']}: {str(e)}")
            if show_debug:
                st.error(f"Error rendering section {section['id']}: {e}")
    
    if show_debug:
        show_render_debug(page_name)
    
    return stats


def _render_section(df, section: dict) -> int:
    """
    セクションをレンダリング
    
    Returns:
        int: レンダリングした指標数
    """
    section_type = section.get('type', 'standard')
    title_key = section.get('title_key')
    description_key = section.get('description_key')
    indicators = section.get('indicators', [])
    cols = section.get('cols', 2)
    show_charts = section.get('show_charts', True)
    
    # Section divider
    st.markdown("---")
    
    # Section title
    if title_key:
        st.markdown(f"#### {t(title_key)}")
    
    # Section description
    if description_key:
        st.caption(t(description_key))
    
    # Dispatch to type-specific renderer
    if section_type == 'standard':
        return _render_standard_section(df, indicators, cols, show_charts)
    elif section_type == 'api':
        return _render_api_section(df, section)
    elif section_type == 'mom_yoy':
        return _render_mom_yoy_section(df, indicators, cols)
    elif section_type == 'dual_chart':
        return _render_dual_chart_section(df, section)
    elif section_type == 'spread':
        return _render_spread_section(df, section)
    elif section_type == 'soma':
        return _render_soma_section(df, section)
    elif section_type == 'employment':
        return _render_employment_section(df, indicators, cols)
    else:
        # Fallback to standard
        return _render_standard_section(df, indicators, cols, show_charts)


# =============================================================================
# SECTION TYPE RENDERERS
# =============================================================================

def _render_standard_section(df, indicators: list, cols: int, show_charts: bool) -> int:
    """標準セクション: カラムレイアウトで指標を表示"""
    if not indicators:
        return 0
    
    rendered = 0
    columns = st.columns(cols)
    
    for i, key in enumerate(indicators):
        with columns[i % cols]:
            config = INDICATORS.get(key, {})
            if _render_indicator_standard(df, key, config, show_charts):
                rendered += 1
    
    return rendered


def _render_api_section(df, section: dict) -> int:
    """APIセクション: 外部API指標を表示"""
    indicators = section.get('indicators', [])
    cols = section.get('cols', 2)
    
    # API指標は各ページで既に実装されている特殊ロジックが必要
    # ここではプレースホルダーを表示
    columns = st.columns(cols)
    
    for i, key in enumerate(indicators):
        with columns[i % cols]:
            config = INDICATORS.get(key, {})
            notes = config.get('notes', key)
            st.caption(f"⚡ {t(f'indicator_{key}', key)}: {notes}")
    
    st.info(f"💡 API indicators ({len(indicators)}) require special handling")
    return len(indicators)


def _render_mom_yoy_section(df, indicators: list, cols: int) -> int:
    """MoM/YoYセクション: 前月比・前年比を表示"""
    if not indicators:
        return 0
    
    df_original = st.session_state.get('df_original')
    rendered = 0
    columns = st.columns(cols)
    
    for i, key in enumerate(indicators):
        with columns[i % cols]:
            config = INDICATORS.get(key, {})
            series = df.get(key) if df is not None else None
            
            if series is None or (hasattr(series, 'isna') and series.isna().all()):
                st.metric(t(f'indicator_{key}', key), "N/A")
                continue
            
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
            rendered += 1
    
    return rendered


def _render_dual_chart_section(df, section: dict) -> int:
    """2軸チャートセクション: Net Liquidity + S&P500等"""
    indicators = section.get('indicators', [])
    chart_pair = section.get('chart_pair')
    
    if not indicators:
        return 0
    
    main_key = indicators[0]
    series = df.get(main_key) if df is not None else None
    
    if series is None:
        st.metric(t(f'indicator_{main_key}', main_key), "N/A")
        return 0
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        config = INDICATORS.get(main_key, {})
        show_metric_with_sparkline(
            t(f'indicator_{main_key}', main_key),
            series,
            main_key,
            config.get('unit', 'B'),
            main_key,
            notes=config.get('notes', '')
        )
    
    with col2:
        if chart_pair and chart_pair in df.columns:
            st.markdown(f"##### {t('net_liquidity_chart_title', f'{main_key} vs {chart_pair}')}")
            plot_dual_axis(df, main_key, chart_pair, f'{main_key} (L)', f'{chart_pair} (R)')
    
    return 1


def _render_spread_section(df, section: dict) -> int:
    """スプレッドセクション: EFFR-IORB等の計算スプレッド"""
    indicators = section.get('indicators', [])
    spread_name = section.get('spread_name', 'Spread')
    spread_multiplier = section.get('spread_multiplier', 1)
    spread_unit = section.get('spread_unit', '')
    
    if len(indicators) < 2:
        return 0
    
    key1, key2 = indicators[0], indicators[1]
    
    if key1 not in df.columns or key2 not in df.columns:
        st.metric(spread_name, "N/A")
        return 0
    
    # Calculate spread
    spread = (df[key1] - df[key2]) * spread_multiplier
    spread.name = spread_name
    
    col1, col2 = st.columns(2)
    
    with col1:
        show_metric(
            t(f'indicator_{spread_name}', spread_name),
            spread,
            spread_unit,
            explanation_key=spread_name,
            notes=t(f'{spread_name.lower()}_notes', f'{key1} - {key2}')
        )
        
        # Sparkline for spread
        if not spread.isna().all():
            recent = spread.tail(60)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=recent.index,
                y=recent.values,
                mode='lines',
                line=dict(color='#FF9F43', width=2),
                fill='tozeroy',
                fillcolor='rgba(255, 159, 67, 0.3)',
                showlegend=False
            ))
            fig.update_layout(
                height=100,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False},
                           key=f"spark_{spread_name}_{uuid.uuid4().hex[:8]}")
    
    with col2:
        # Show individual rates
        valid_cols = [c for c in indicators if c in df.columns]
        if valid_cols:
            st.markdown(f"###### {t('component_rates', 'Component Rates')}")
            styled_line_chart(df[valid_cols], height=200)
    
    return 1


def _render_soma_section(df, section: dict) -> int:
    """SOMAセクション: SOMA構成 + RMPステータス"""
    indicators = section.get('indicators', [])
    cols = section.get('cols', 3)
    show_soma_chart = section.get('show_soma_chart', True)
    show_rmp_status = section.get('show_rmp_status', True)
    
    # RMP Status
    if show_rmp_status:
        _render_rmp_status(df)
    
    # SOMA Composition Chart
    if show_soma_chart:
        st.markdown(f"##### {t('soma_composition')}")
        plot_soma_composition(df)
    
    # Individual SOMA metrics
    columns = st.columns(cols)
    rendered = 0
    
    for i, key in enumerate(indicators):
        with columns[i % cols]:
            config = INDICATORS.get(key, {})
            if _render_indicator_standard(df, key, config, show_charts=True):
                rendered += 1
    
    return rendered


def _render_employment_section(df, indicators: list, cols: int) -> int:
    """雇用セクション: 特殊計算が必要な雇用指標"""
    # Employment indicators have special calculations
    # For now, render as standard with notes
    return _render_standard_section(df, indicators, cols, show_charts=True)


def _render_rmp_status(df):
    """RMPステータスを表示"""
    rmp_status_type_series = df.get('RMP_Status_Type')
    rmp_status_type = rmp_status_type_series.iloc[-1] if hasattr(rmp_status_type_series, 'iloc') and len(rmp_status_type_series) > 0 else 'monitoring'
    rmp_weekly_change_series = df.get('RMP_Weekly_Change')
    rmp_weekly_change = rmp_weekly_change_series.iloc[-1] if hasattr(rmp_weekly_change_series, 'iloc') and len(rmp_weekly_change_series) > 0 else None
    rmp_active_series = df.get('RMP_Alert_Active', pd.Series([False]))
    rmp_active = rmp_active_series.iloc[-1] if hasattr(rmp_active_series, 'iloc') and len(rmp_active_series) > 0 else False
    
    # Build translated RMP status text
    if rmp_status_type == 'monitoring' or rmp_weekly_change is None:
        rmp_status = t('rmp_monitoring')
    elif rmp_status_type == 'active':
        rmp_status = t('rmp_active').replace('${value}', f'{rmp_weekly_change:.1f}')
    elif rmp_status_type == 'accelerating':
        rmp_status = t('rmp_accelerating').replace('${value}', f'{rmp_weekly_change:.1f}')
    elif rmp_status_type == 'slowing':
        rmp_status = t('rmp_slowing').replace('${value}', f'{rmp_weekly_change:.1f}')
    elif rmp_status_type == 'selling':
        rmp_status = t('rmp_selling').replace('${value}', f'{rmp_weekly_change:.1f}')
    else:
        rmp_status = t('rmp_monitoring')
    
    if rmp_active:
        st.info(f"{t('rmp_status')}: {rmp_status}")
    else:
        st.warning(f"ℹ️ {t('rmp_status')}: {rmp_status}")


# =============================================================================
# INDICATOR RENDERERS
# =============================================================================

def _render_indicator_standard(df, key: str, config: dict, show_charts: bool = True) -> bool:
    """標準指標をレンダリング"""
    series = df.get(key) if df is not None else None
    
    if series is None or (hasattr(series, 'isna') and series.isna().all()):
        st.metric(t(f'indicator_{key}', key), "N/A")
        return False
    
    unit = config.get('unit', '')
    notes = config.get('notes', '')
    decimal_places = 2 if unit == '%' else 1
    
    # Alert function based on validation range
    alert_func = None
    validation = config.get('validation')
    if validation:
        min_val, max_val = validation
        range_size = max_val - min_val
        alert_func = lambda x: x > (max_val - range_size * 0.1) or x < (min_val + range_size * 0.1)
    
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
    
    # Long-term chart
    if show_charts and key in df.columns and not df[key].isna().all():
        st.markdown(f"###### {t('long_term_trend')}")
        styled_line_chart(df[[key]], height=200)
    
    return True


# =============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# =============================================================================

def render_indicator(df, key: str, config: dict = None, show_chart: bool = True):
    """単一指標をレンダリング（後方互換性）"""
    if config is None:
        config = INDICATORS.get(key, {})
    return _render_indicator_standard(df, key, config, show_chart)


def render_indicators_for_page(df, page_name: str, section: str = None):
    """ページの指標をレンダリング（後方互換性）"""
    indicators = get_indicators_for_page(page_name)
    results = {}
    for key, config in indicators.items():
        results[key] = render_indicator(df, key, config)
    return results


def render_in_columns(df, keys: list, num_cols: int = 2, show_charts: bool = True):
    """カラムレイアウトでレンダリング（後方互換性）"""
    return _render_standard_section(df, keys, num_cols, show_charts)


def render_section(df, title: str, keys: list, num_cols: int = 2):
    """セクションをレンダリング（後方互換性）"""
    st.markdown(f"### {title}")
    return _render_standard_section(df, keys, num_cols, show_charts=True)


# =============================================================================
# DEBUG / STATS
# =============================================================================

def get_render_stats(page_name: str = None):
    """レンダリング統計を取得"""
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


def show_render_debug(page_name: str = None):
    """デバッグ情報を表示"""
    stats = get_render_stats(page_name)
    
    with st.expander("🔧 Render Debug Info"):
        st.write(f"**Total indicators:** {stats['total']}")
        
        st.write("**By pattern:**")
        for pattern, count in sorted(stats['by_pattern'].items()):
            st.write(f"  - {pattern}: {count}")
        
        st.write("**By source:**")
        for source, count in sorted(stats['by_source'].items()):
            st.write(f"  - {source}: {count}")
        
        # Layout info
        if page_name:
            layout = get_page_layout(page_name)
            if layout:
                st.write(f"\n**Layout sections:** {len(layout.get('sections', []))}")
                for section in layout.get('sections', []):
                    st.write(f"  - {section['id']}: {len(section.get('indicators', []))} indicators ({section.get('type', 'standard')})")
