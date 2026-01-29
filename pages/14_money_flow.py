# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 14: Money Flow Visualization
お金の流れを可視化 - Fed → 銀行 → 市場 → 経済

Phase 1: Static Sankey diagram (完了)
Phase 2: Time-series animation with slider (現在)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os
import time as time_module

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import t

# Get data from session state
df = st.session_state.get('df')

if df is None:
    st.error(t('error_data_not_loaded'))
    st.stop()


def get_value_at_date(column_name, target_date, default=0):
    """Get value at specific date (or nearest available)"""
    if column_name not in df.columns:
        return default
    
    series = df[column_name].dropna()
    if len(series) == 0:
        return default
    
    # Find nearest date
    try:
        idx = series.index.get_indexer([target_date], method='nearest')[0]
        if idx >= 0 and idx < len(series):
            return series.iloc[idx]
    except:
        pass
    
    return series.iloc[-1] if len(series) > 0 else default


def get_latest_value(column_name, default=0):
    """Get latest non-null value from dataframe"""
    if column_name in df.columns:
        series = df[column_name].dropna()
        if len(series) > 0:
            return series.iloc[-1]
    return default


def format_value(value, unit='B', is_trillion=False):
    """Format value with appropriate suffix"""
    if pd.isna(value) or value == 0:
        return "N/A"
    if is_trillion:
        return f"${value:.2f}T"
    elif value >= 1000:
        return f"${value/1000:.2f}T"
    else:
        return f"${value:.0f}B"


def format_change(current, previous):
    """Format change percentage"""
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return ""
    change = ((current - previous) / previous) * 100
    if change > 0:
        return f"📈 +{change:.1f}%"
    elif change < 0:
        return f"📉 {change:.1f}%"
    else:
        return "→ 0%"


def get_data_at_date(target_date):
    """Get all money flow data at specific date"""
    data = {
        'soma_total': get_value_at_date('SOMA_Total', target_date, 6800),
        'soma_treasury': get_value_at_date('SOMA_Treasury', target_date, 4200),
        'soma_bills': get_value_at_date('SOMA_Bills', target_date, 195),
        'reserves': get_value_at_date('Reserves', target_date, 3200),
        'tga': get_value_at_date('TGA', target_date, 722),
        'on_rrp': get_value_at_date('ON_RRP', target_date, 98),
        'ci_loans': get_value_at_date('CI_Loans', target_date, 2800),
        'cre_loans': get_value_at_date('CRE_Loans', target_date, 3000),
        'consumer_loans': get_value_at_date('Consumer_Loans', target_date, 500),
        'bank_securities': get_value_at_date('Bank_Securities', target_date, 5500),
        'm2': get_value_at_date('M2SL', target_date, 21500),
    }
    data['net_liquidity'] = data['soma_total'] - data['tga'] - data['on_rrp']
    return data


def create_sankey_figure(data, show_changes=False, prev_data=None):
    """Create Sankey diagram with given data"""
    
    # Build labels with optional change indicators
    def label_with_change(name, value, prev_value=None, is_trillion=False):
        base = f"{name}\n{format_value(value, is_trillion=is_trillion)}"
        if show_changes and prev_value is not None:
            change = format_change(value, prev_value)
            if change:
                base += f"\n{change}"
        return base
    
    prev = prev_data or {}
    
    node_labels = [
        label_with_change("🏛️ Fed総資産", data['soma_total'], prev.get('soma_total')),
        label_with_change("📜 国債保有", data['soma_treasury'], prev.get('soma_treasury')),
        label_with_change("📄 T-Bills", data['soma_bills'], prev.get('soma_bills')),
        label_with_change("🏦 銀行準備金", data['reserves'], prev.get('reserves')),
        label_with_change("🏛️ 財務省(TGA)", data['tga'], prev.get('tga')),
        label_with_change("🔒 RRP(吸収)", data['on_rrp'], prev.get('on_rrp')),
        label_with_change("🏭 企業融資(C&I)", data['ci_loans'], prev.get('ci_loans')),
        label_with_change("🏢 不動産融資(CRE)", data['cre_loans'], prev.get('cre_loans')),
        label_with_change("🛒 消費者ローン", data['consumer_loans'], prev.get('consumer_loans')),
        label_with_change("📊 有価証券投資", data['bank_securities'], prev.get('bank_securities')),
        label_with_change("💰 M2マネー", data['m2'], prev.get('m2'), is_trillion=True),
        label_with_change("📈 金融市場", data['net_liquidity'], prev.get('net_liquidity')),
    ]
    
    node_colors = [
        "#3B82F6", "#60A5FA", "#93C5FD", "#8B5CF6", "#10B981", "#F59E0B",
        "#EC4899", "#F472B6", "#FB7185", "#A78BFA", "#06B6D4", "#EF4444",
    ]
    
    # Define links
    links_source = [0, 0, 1, 2, 3, 3, 3, 3, 3, 0, 4, 6, 7, 8, 9]
    links_target = [1, 2, 3, 3, 6, 7, 8, 9, 5, 4, 11, 10, 10, 10, 11]
    
    links_value = [
        data['soma_treasury'],
        data['soma_bills'],
        data['reserves'] * 0.7,
        data['soma_bills'] * 0.8,
        data['ci_loans'] * 0.3,
        data['cre_loans'] * 0.3,
        data['consumer_loans'] * 0.5,
        data['bank_securities'] * 0.2,
        data['on_rrp'],
        data['tga'],
        data['tga'] * 0.8,
        data['ci_loans'] * 0.5,
        data['cre_loans'] * 0.4,
        data['consumer_loans'] * 0.8,
        data['bank_securities'] * 0.3,
    ]
    
    links_color = [
        "rgba(59, 130, 246, 0.4)", "rgba(59, 130, 246, 0.4)",
        "rgba(139, 92, 246, 0.4)", "rgba(139, 92, 246, 0.4)",
        "rgba(236, 72, 153, 0.4)", "rgba(244, 114, 182, 0.4)",
        "rgba(251, 113, 133, 0.4)", "rgba(167, 139, 250, 0.4)",
        "rgba(245, 158, 11, 0.5)", "rgba(16, 185, 129, 0.4)",
        "rgba(16, 185, 129, 0.4)", "rgba(6, 182, 212, 0.4)",
        "rgba(6, 182, 212, 0.4)", "rgba(6, 182, 212, 0.4)",
        "rgba(239, 68, 68, 0.4)",
    ]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors,
            hovertemplate='%{label}<extra></extra>',
        ),
        link=dict(
            source=links_source,
            target=links_target,
            value=links_value,
            color=links_color,
            hovertemplate='%{source.label} → %{target.label}<br>%{value:.0f}B<extra></extra>',
        ),
        textfont=dict(size=11, color='white'),
    )])
    
    fig.update_layout(
        font_size=12,
        height=650,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


# ========== PAGE CONTENT ==========
st.subheader(t('money_flow_title'))
st.caption(t('money_flow_desc'))

# ========== TAB SELECTION ==========
tab_current, tab_timeline = st.tabs([
    f"📊 {t('money_flow_tab_current')}",
    f"▶️ {t('money_flow_tab_timeline')}"
])

# ========== TAB 1: CURRENT DATA ==========
with tab_current:
    # Quick Guide (提案1対応)
    st.info(t('money_flow_quick_guide'))
    
    # Get current data
    current_data = {
        'soma_total': get_latest_value('SOMA_Total', 6800),
        'soma_treasury': get_latest_value('SOMA_Treasury', 4200),
        'soma_bills': get_latest_value('SOMA_Bills', 195),
        'reserves': get_latest_value('Reserves', 3200),
        'tga': get_latest_value('TGA', 722),
        'on_rrp': get_latest_value('ON_RRP', 98),
        'ci_loans': get_latest_value('CI_Loans', 2800),
        'cre_loans': get_latest_value('CRE_Loans', 3000),
        'consumer_loans': get_latest_value('Consumer_Loans', 500),
        'bank_securities': get_latest_value('Bank_Securities', 5500),
        'm2': get_latest_value('M2SL', 21500),
    }
    current_data['net_liquidity'] = current_data['soma_total'] - current_data['tga'] - current_data['on_rrp']
    
    st.markdown(f"### {t('money_flow_sankey_title')}")
    fig = create_sankey_figure(current_data)
    st.plotly_chart(fig, use_container_width=True)
    
    # Key Metrics
    st.markdown(f"### {t('money_flow_key_metrics')}")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(t('money_flow_fed_assets'), format_value(current_data['soma_total']),
                  help=t('money_flow_fed_assets_help'))
    with col2:
        st.metric(t('money_flow_net_liquidity'), format_value(current_data['net_liquidity']),
                  delta=f"TGA: -{format_value(current_data['tga'])}, RRP: -{format_value(current_data['on_rrp'])}",
                  help=t('money_flow_net_liquidity_help'))
    with col3:
        st.metric(t('money_flow_bank_reserves'), format_value(current_data['reserves']),
                  help=t('money_flow_bank_reserves_help'))
    with col4:
        st.metric(t('money_flow_m2'), format_value(current_data['m2'], is_trillion=True),
                  help=t('money_flow_m2_help'))

# ========== TAB 2: TIMELINE ANIMATION ==========
with tab_timeline:
    st.markdown(f"### {t('money_flow_timeline_title')}")
    st.info(t('money_flow_timeline_desc'))
    
    # Get available date range from data
    if 'SOMA_Total' in df.columns:
        available_dates = df['SOMA_Total'].dropna().index
        if len(available_dates) > 0:
            min_date = available_dates.min()
            max_date = available_dates.max()
            
            # Create monthly date options (last 24 months)
            date_range = pd.date_range(
                start=max(min_date, max_date - pd.DateOffset(months=24)),
                end=max_date,
                freq='ME'  # Month End
            )
            
            if len(date_range) > 1:
                # Compact Controls (提案3対応: YouTube風統合UI)
                col_play, col_date, col_slider, col_speed = st.columns([1, 2, 6, 1])
                
                with col_play:
                    play_button = st.button("▶️", use_container_width=True, help=t('money_flow_play'))
                
                with col_date:
                    # Large date display
                    selected_idx = st.session_state.get('timeline_slider', len(date_range) - 1)
                    if selected_idx >= len(date_range):
                        selected_idx = len(date_range) - 1
                    selected_date = date_range[selected_idx]
                    st.markdown(f"### 📅 {selected_date.strftime('%Y/%m')}")
                
                with col_slider:
                    selected_idx = st.slider(
                        t('money_flow_select_date'),
                        min_value=0,
                        max_value=len(date_range) - 1,
                        value=len(date_range) - 1,
                        format="%d",
                        key='timeline_slider',
                        label_visibility='collapsed'
                    )
                    selected_date = date_range[selected_idx]
                
                with col_speed:
                    speed = st.selectbox(
                        t('money_flow_speed'),
                        options=[0.5, 1.0, 2.0],
                        index=1,
                        format_func=lambda x: f"{x}x",
                        label_visibility='collapsed'
                    )
                
                # Auto-play functionality
                if play_button:
                    progress_bar = st.progress(0)
                    chart_placeholder = st.empty()
                    metrics_placeholder = st.empty()
                    
                    for i, date in enumerate(date_range):
                        # Get data for this date and previous date
                        data = get_data_at_date(date)
                        prev_date = date_range[i-1] if i > 0 else None
                        prev_data = get_data_at_date(prev_date) if prev_date is not None else None
                        
                        # Update chart
                        fig = create_sankey_figure(data, show_changes=True, prev_data=prev_data)
                        fig.update_layout(title=f"📅 {date.strftime('%Y年%m月')}")
                        chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"timeline_{i}")
                        
                        # Update metrics
                        with metrics_placeholder.container():
                            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                            with mcol1:
                                delta = format_change(data['soma_total'], prev_data['soma_total']) if prev_data else None
                                st.metric("Fed総資産", format_value(data['soma_total']), delta=delta)
                            with mcol2:
                                delta = format_change(data['net_liquidity'], prev_data['net_liquidity']) if prev_data else None
                                st.metric("純流動性", format_value(data['net_liquidity']), delta=delta)
                            with mcol3:
                                delta = format_change(data['on_rrp'], prev_data['on_rrp']) if prev_data else None
                                st.metric("RRP", format_value(data['on_rrp']), delta=delta)
                            with mcol4:
                                delta = format_change(data['tga'], prev_data['tga']) if prev_data else None
                                st.metric("TGA", format_value(data['tga']), delta=delta)
                        
                        # Update progress
                        progress_bar.progress((i + 1) / len(date_range))
                        
                        # Wait based on speed
                        time_module.sleep(1.0 / speed)
                    
                    st.success(t('money_flow_playback_complete'))
                
                else:
                    # Static view for selected date
                    data = get_data_at_date(selected_date)
                    prev_date = date_range[selected_idx - 1] if selected_idx > 0 else None
                    prev_data = get_data_at_date(prev_date) if prev_date is not None else None
                    
                    fig = create_sankey_figure(data, show_changes=True, prev_data=prev_data)
                    fig.update_layout(title=f"📅 {selected_date.strftime('%Y年%m月')}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Metrics with changes
                    st.markdown(f"### {t('money_flow_key_metrics')}")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        delta = format_change(data['soma_total'], prev_data['soma_total']) if prev_data else None
                        st.metric("Fed総資産", format_value(data['soma_total']), delta=delta)
                    with col2:
                        delta = format_change(data['net_liquidity'], prev_data['net_liquidity']) if prev_data else None
                        st.metric("純流動性", format_value(data['net_liquidity']), delta=delta)
                    with col3:
                        delta = format_change(data['on_rrp'], prev_data['on_rrp']) if prev_data else None
                        st.metric("RRP", format_value(data['on_rrp']), delta=delta)
                    with col4:
                        delta = format_change(data['tga'], prev_data['tga']) if prev_data else None
                        st.metric("TGA", format_value(data['tga']), delta=delta)
                
                # Historical comparison section
                st.markdown("---")
                st.markdown(f"### {t('money_flow_comparison_title')}")
                
                # Key events timeline
                col_ev1, col_ev2 = st.columns(2)
                
                with col_ev1:
                    st.markdown(f"**{t('money_flow_key_events')}**")
                    st.markdown(t('money_flow_events_list'))
                
                with col_ev2:
                    # Net Liquidity trend chart - simplified without vline
                    if 'SOMA_Total' in df.columns and 'TGA' in df.columns and 'ON_RRP' in df.columns:
                        # Calculate net liquidity history
                        net_liq = df['SOMA_Total'] - df['TGA'].fillna(0) - df['ON_RRP'].fillna(0)
                        net_liq = net_liq.dropna().tail(100)  # Last ~2 years
                        
                        if len(net_liq) > 10:
                            fig_trend = go.Figure()
                            fig_trend.add_trace(go.Scatter(
                                x=net_liq.index,
                                y=net_liq.values,
                                mode='lines',
                                name='Net Liquidity',
                                line=dict(color='#3B82F6', width=2),
                                fill='tozeroy',
                                fillcolor='rgba(59, 130, 246, 0.2)'
                            ))
                            
                            # Add selected date marker as a scatter point instead of vline
                            # Find the closest value for selected date
                            selected_val = get_value_at_date('SOMA_Total', selected_date, 0) - \
                                           get_value_at_date('TGA', selected_date, 0) - \
                                           get_value_at_date('ON_RRP', selected_date, 0)
                            
                            fig_trend.add_trace(go.Scatter(
                                x=[selected_date],
                                y=[selected_val],
                                mode='markers+text',
                                name='選択中',
                                marker=dict(color='red', size=12, symbol='diamond'),
                                text=['📍'],
                                textposition='top center',
                                showlegend=False
                            ))
                            
                            fig_trend.update_layout(
                                title=t('money_flow_net_liquidity_trend'),
                                height=250,
                                margin=dict(l=20, r=20, t=40, b=20),
                                showlegend=False,
                                yaxis_title="$B"
                            )
                            st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.warning(t('money_flow_insufficient_data'))
        else:
            st.warning(t('money_flow_no_data'))
    else:
        st.warning(t('money_flow_no_data'))

# ========== FLOW EXPLANATION (Common) ==========
st.markdown("---")
st.markdown(f"### {t('money_flow_explanation_title')}")

with st.expander(t('money_flow_explanation_expand'), expanded=False):
    st.markdown(f"""
**{t('money_flow_step1_title')}**
{t('money_flow_step1_desc')}

**{t('money_flow_step2_title')}**
{t('money_flow_step2_desc')}

**{t('money_flow_step3_title')}**
{t('money_flow_step3_desc')}

**{t('money_flow_step4_title')}**
{t('money_flow_step4_desc')}

---

**{t('money_flow_formula_title')}**
```
{t('money_flow_formula')}
```
""")

# ========== ABSORPTION ANALYSIS (Common) ==========
st.markdown(f"### {t('money_flow_absorption_title')}")

# Use current data for absorption analysis
current_data = get_data_at_date(df.index.max())
tga = current_data['tga']
on_rrp = current_data['on_rrp']
soma_total = current_data['soma_total']
net_liquidity = current_data['net_liquidity']

col_abs1, col_abs2 = st.columns(2)

with col_abs1:
    fig_absorption = go.Figure(data=[go.Pie(
        labels=[t('money_flow_tga_label'), t('money_flow_rrp_label'), t('money_flow_available_label')],
        values=[tga, on_rrp, net_liquidity],
        hole=0.5,
        marker_colors=['#10B981', '#F59E0B', '#3B82F6'],
        textinfo='label+percent',
        textposition='outside',
    )])
    
    fig_absorption.update_layout(
        title=t('money_flow_absorption_chart_title'),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
    )
    
    st.plotly_chart(fig_absorption, use_container_width=True)

with col_abs2:
    total_absorption = tga + on_rrp
    absorption_ratio = (total_absorption / soma_total) * 100 if soma_total > 0 else 0
    
    st.markdown(f"#### {t('money_flow_absorption_analysis')}")
    
    st.metric(
        t('money_flow_total_absorption'),
        format_value(total_absorption),
        delta=f"{absorption_ratio:.1f}% {t('money_flow_of_fed_assets')}"
    )
    
    st.progress(min(absorption_ratio / 30, 1.0))
    
    if absorption_ratio > 20:
        st.warning(t('money_flow_high_absorption_warning'))
    elif absorption_ratio > 10:
        st.info(t('money_flow_moderate_absorption_info'))
    else:
        st.success(t('money_flow_low_absorption_success'))

# Absorption Rate History Chart (提案5対応)
st.markdown(f"### {t('money_flow_absorption_trend')}")

# Calculate historical absorption ratio
if 'SOMA_Total' in df.columns and 'TGA' in df.columns and 'ON_RRP' in df.columns:
    soma_hist = df['SOMA_Total'].dropna()
    tga_hist = df['TGA'].reindex(soma_hist.index).fillna(0)
    rrp_hist = df['ON_RRP'].reindex(soma_hist.index).fillna(0)
    
    # Calculate absorption ratio history
    absorption_hist = ((tga_hist + rrp_hist) / soma_hist * 100).dropna().tail(100)  # Last ~2 years
    
    if len(absorption_hist) > 10:
        fig_absorption_hist = go.Figure()
        
        # Main line
        fig_absorption_hist.add_trace(go.Scatter(
            x=absorption_hist.index,
            y=absorption_hist.values,
            mode='lines',
            name=t('money_flow_absorption_history'),
            line=dict(color='#F59E0B', width=2),
            fill='tozeroy',
            fillcolor='rgba(245, 158, 11, 0.2)'
        ))
        
        # Add threshold lines
        fig_absorption_hist.add_hline(y=20, line_dash="dash", line_color="red", 
                                       annotation_text=t('money_flow_threshold_warning'), annotation_position="right")
        fig_absorption_hist.add_hline(y=10, line_dash="dash", line_color="green",
                                       annotation_text=t('money_flow_threshold_good'), annotation_position="right")
        
        # Mark current value
        fig_absorption_hist.add_trace(go.Scatter(
            x=[absorption_hist.index[-1]],
            y=[absorption_hist.values[-1]],
            mode='markers+text',
            name=t('money_flow_current_level'),
            marker=dict(color='red', size=12, symbol='diamond'),
            text=[f'{absorption_hist.values[-1]:.1f}%'],
            textposition='top center',
            showlegend=False
        ))
        
        fig_absorption_hist.update_layout(
            height=250,
            margin=dict(l=20, r=60, t=20, b=20),
            showlegend=False,
            yaxis_title="%",
            yaxis=dict(range=[0, max(30, absorption_hist.max() * 1.1)])
        )
        
        st.plotly_chart(fig_absorption_hist, use_container_width=True)

# ========== FOOTER ==========
st.markdown("---")
st.caption(t('money_flow_footer'))
