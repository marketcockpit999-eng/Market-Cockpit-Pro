# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Charts
チャート描画ヘルパー関数を管理
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import uuid

from .config import EXPLANATIONS, DATA_FREQUENCY
from .data_processor import get_freshness_badge, get_mom_yoy


def show_metric(label, series, unit="", explanation_key="", notes="", alert_func=None):
    """メトリック表示ヘルパー（更新マーク対応）"""
    df = st.session_state.get('df')
    
    if series is None or (hasattr(series, 'isna') and series.isna().all()):
        val = None
        delta = None
        latest_date = None
        release_date = None
    else:
        val = series.iloc[-1] if hasattr(series, 'iloc') else series
        if hasattr(series, 'iloc') and len(series) > 1:
            delta = val - series.iloc[-2]
        else:
            delta = None
        
        latest_date = None
        release_date = None
        if df is not None and hasattr(df, 'attrs'):
            col_name = series.name if hasattr(series, 'name') else explanation_key
            if 'last_valid_dates' in df.attrs and col_name in df.attrs['last_valid_dates']:
                latest_date = df.attrs['last_valid_dates'][col_name]
            if 'fred_release_dates' in df.attrs and col_name in df.attrs['fred_release_dates']:
                release_date = df.attrs['fred_release_dates'][col_name]
    
    help_text = EXPLANATIONS.get(explanation_key, "")
    
    freshness_badge = get_freshness_badge(release_date or latest_date) if (release_date or latest_date) else ""
    display_label = f"{freshness_badge} {label}" if freshness_badge else label
    
    if alert_func and val is not None and alert_func(val):
        st.metric(display_label, f"{val:.1f} {unit}" if val is not None else "N/A", 
                 delta=f"{delta:+.1f}" if delta is not None else None,
                 help=help_text, delta_color="inverse")
    else:
        st.metric(display_label, f"{val:.1f} {unit}" if val is not None else "N/A",
                 delta=f"{delta:+.1f}" if delta is not None else None,
                 help=help_text)
    
    if latest_date:
        freq_label = DATA_FREQUENCY.get(explanation_key, '')
        st.caption(f"📅 対象期間: {latest_date} ({freq_label})" if freq_label else f"📅 対象日: {latest_date}")
    
    if release_date:
        st.caption(f"🔄 提供元更新日: {release_date}")
    
    if notes:
        st.caption(notes)


def show_metric_with_sparkline(label, series, df_column, unit="", explanation_key="", notes="", alert_func=None, decimal_places=1):
    """メトリック + スパークライン（ミニトレンドチャート）を表示"""
    df = st.session_state.get('df')

    if series is None or (hasattr(series, 'isna') and series.isna().all()):
        val = None
        delta = None
        latest_date = None
        release_date = None
    else:
        val = series.iloc[-1] if hasattr(series, 'iloc') else series
        if hasattr(series, 'iloc') and len(series) > 1:
            delta = val - series.iloc[-2]
        else:
            delta = None
        
        latest_date = None
        release_date = None
        if df is not None and hasattr(df, 'attrs'):
            if 'last_valid_dates' in df.attrs and df_column in df.attrs['last_valid_dates']:
                latest_date = df.attrs['last_valid_dates'][df_column]
            if 'fred_release_dates' in df.attrs and df_column in df.attrs['fred_release_dates']:
                release_date = df.attrs['fred_release_dates'][df_column]
    
    help_text = EXPLANATIONS.get(explanation_key, "")
    
    freshness_badge = get_freshness_badge(release_date or latest_date) if (release_date or latest_date) else ""
    display_label = f"{freshness_badge} {label}" if freshness_badge else label
    
    val_format = f"{{:.{decimal_places}f}}"
    delta_format = f"{{:+.{decimal_places}f}}"
    
    if alert_func and val is not None and alert_func(val):
        st.metric(display_label, f"{val_format.format(val)} {unit}" if val is not None else "N/A", 
                 delta=delta_format.format(delta) if delta is not None else None,
                 help=help_text, delta_color="inverse")
    else:
        st.metric(display_label, f"{val_format.format(val)} {unit}" if val is not None else "N/A",
                 delta=delta_format.format(delta) if delta is not None else None,
                 help=help_text)
    
    if latest_date:
        freq_label = DATA_FREQUENCY.get(df_column, '')
        st.caption(f"📅 対象期間: {latest_date} ({freq_label})" if freq_label else f"📅 対象日: {latest_date}")
    
    if release_date:
        st.caption(f"🔄 提供元更新日: {release_date}")
    
    if notes:
        st.caption(notes)
    
    # スパークライン
    if df is not None and df_column in df.columns and not df.get(df_column, pd.Series()).isna().all():
        recent_data = df[df_column].tail(60)
        
        st.caption("📊 過去60日間のトレンド")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=recent_data.index,
            y=recent_data.values,
            mode='lines',
            line=dict(color='cyan', width=1),
            fill='tozeroy',
            fillcolor='rgba(0,255,255,0.1)',
            showlegend=False
        ))
        
        fig.update_layout(
            height=100,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode=False
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, 
                       key=f"spark_{uuid.uuid4().hex[:8]}")


def plot_dual_axis(df, left_col, right_col, left_name, right_name):
    """2軸チャート"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if left_col in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df[left_col], name=left_name, line=dict(color='cyan')),
            secondary_y=False
        )
    
    if right_col in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df[right_col], name=right_name, line=dict(color='orange')),
            secondary_y=True
        )
    
    fig.update_layout(
        template='plotly_dark',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    fig.update_yaxes(title_text=left_name, secondary_y=False)
    fig.update_yaxes(title_text=right_name, secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True, key=f"dual_{uuid.uuid4().hex[:8]}")


def plot_soma_composition(df):
    """SOMA構成チャート（SOMA Total + Bills Ratio）"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    if 'SOMA_Total' in df.columns:
        soma_resampled = df['SOMA_Total'].resample('W').last()
        fig.add_trace(
            go.Bar(x=soma_resampled.index, y=soma_resampled, name='SOMA Total (Billions)', marker_color='steelblue'),
            secondary_y=False
        )
    
    if 'SomaBillsRatio' in df.columns:
        ratio_resampled = df['SomaBillsRatio'].resample('W').last()
        fig.add_trace(
            go.Scatter(x=ratio_resampled.index, y=ratio_resampled, name='Bills Ratio (%)', 
                      line=dict(color='orange', width=2)),
            secondary_y=True
        )
    
    fig.update_layout(
        template='plotly_dark',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    fig.update_yaxes(title_text="SOMA Total (B)", secondary_y=False)
    fig.update_yaxes(title_text="Bills Ratio (%)", secondary_y=True, tickformat='.1f')
    
    st.plotly_chart(fig, use_container_width=True, key=f"soma_{uuid.uuid4().hex[:8]}")


def display_macro_card(title, series, df_column, df_original=None, unit="", notes="", freq='M', show_level=True):
    """マクロ指標カード（MoM, YoY, sparkline, long-term chart）"""
    
    # Get df_original from session state if not provided
    if df_original is None:
        df_original = st.session_state.get('df_original', {})
    
    st.markdown(f"#### {title}")
    
    # Calculate MoM and YoY
    mom, yoy = get_mom_yoy(df_column, df_original, freq=freq)
    
    # Metrics Row
    m_col1, m_col2 = st.columns(2)
    if mom is not None:
        m_col1.metric("前月比", f"{mom:+.1f}%")
    if yoy is not None:
        m_col2.metric("前年比", f"{yoy:+.1f}%")
    
    # Main Metric with Sparkline
    if show_level:
        show_metric_with_sparkline(title, series, df_column, unit, notes=notes)
    
    # YoY% Trend Chart
    original_series = df_original.get(df_column) if isinstance(df_original, dict) else (
        df_original[df_column] if df_column in df_original.columns else None
    )
    
    if original_series is not None and len(original_series.dropna()) > 12:
        data = original_series.dropna()
        yoy_series = (data / data.shift(12) - 1) * 100
        yoy_series = yoy_series.dropna()
        if len(yoy_series) > 0:
            st.markdown(f"###### {title} YoY% (前年比変化率)")
            st.line_chart(yoy_series, height=120)
    
    # Long-term Chart (Level)
    if series is not None and not series.isna().all():
        st.markdown(f"###### {title} Long-term Trend (Level)")
        st.line_chart(series.dropna(), height=150)
