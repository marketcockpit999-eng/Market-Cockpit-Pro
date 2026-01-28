# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 14: Money Flow Visualization
お金の流れを可視化 - Fed → 銀行 → 市場 → 経済
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import t

# Get data from session state
df = st.session_state.get('df')

if df is None:
    st.error(t('error_data_not_loaded'))
    st.stop()


def get_latest_value(column_name, default=0):
    """Get latest non-null value from dataframe"""
    if column_name in df.columns:
        series = df[column_name].dropna()
        if len(series) > 0:
            return series.iloc[-1]
    return default


def format_value(value, unit='B'):
    """Format value with appropriate suffix"""
    if value >= 1000:
        return f"${value/1000:.2f}T"
    else:
        return f"${value:.0f}B"


# ========== PAGE CONTENT ==========
st.subheader(t('money_flow_title'))
st.caption(t('money_flow_desc'))

# ========== GET REAL DATA ==========
# Fed Balance Sheet (資産側)
soma_total = get_latest_value('SOMA_Total', 6800)      # Fed総資産
soma_treasury = get_latest_value('SOMA_Treasury', 4200)  # 国債保有
soma_bills = get_latest_value('SOMA_Bills', 195)       # 短期国債(T-Bills)

# Fed Liabilities & Absorption (負債側・吸収)
reserves = get_latest_value('Reserves', 3200)          # 銀行準備金
tga = get_latest_value('TGA', 722)                     # 財務省口座
on_rrp = get_latest_value('ON_RRP', 98)                # リバースレポ

# Banking Sector (H.8)
ci_loans = get_latest_value('CI_Loans', 2800)          # 企業融資
cre_loans = get_latest_value('CRE_Loans', 3000)        # 不動産融資
consumer_loans = get_latest_value('Consumer_Loans', 500)  # 消費者ローン
bank_securities = get_latest_value('Bank_Securities', 5500)  # 銀行保有有価証券
bank_deposits = get_latest_value('Bank_Deposits', 17500)  # 預金

# Money Supply
m2 = get_latest_value('M2SL', 21500)                   # M2マネーサプライ

# Calculate Net Liquidity
net_liquidity = soma_total - tga - on_rrp

# ========== SANKEY DIAGRAM ==========
st.markdown(f"### {t('money_flow_sankey_title')}")

# Define nodes (ノード定義)
# 順番が重要: インデックスで参照する
node_labels = [
    # Layer 0: Fed (Source)
    f"🏛️ Fed総資産\n{format_value(soma_total)}",           # 0
    
    # Layer 1: Fed Components
    f"📜 国債保有\n{format_value(soma_treasury)}",          # 1
    f"📄 T-Bills\n{format_value(soma_bills)}",             # 2
    
    # Layer 2: Distribution
    f"🏦 銀行準備金\n{format_value(reserves)}",             # 3
    f"🏛️ 財務省(TGA)\n{format_value(tga)}",                # 4
    f"🔒 RRP(吸収)\n{format_value(on_rrp)}",               # 5
    
    # Layer 3: Banking Activity
    f"🏭 企業融資(C&I)\n{format_value(ci_loans)}",          # 6
    f"🏢 不動産融資(CRE)\n{format_value(cre_loans)}",       # 7
    f"🛒 消費者ローン\n{format_value(consumer_loans)}",     # 8
    f"📊 有価証券投資\n{format_value(bank_securities)}",    # 9
    
    # Layer 4: Economy
    f"💰 M2マネー\n{format_value(m2)}",                    # 10
    f"📈 金融市場\n{format_value(net_liquidity)}",         # 11
]

# Node colors
node_colors = [
    "#3B82F6",  # Fed - Blue
    "#60A5FA",  # Treasury Holdings - Light Blue
    "#93C5FD",  # T-Bills - Lighter Blue
    "#8B5CF6",  # Reserves - Purple
    "#10B981",  # TGA - Green
    "#F59E0B",  # RRP - Orange (absorption)
    "#EC4899",  # C&I Loans - Pink
    "#F472B6",  # CRE Loans - Light Pink
    "#FB7185",  # Consumer Loans - Rose
    "#A78BFA",  # Securities - Light Purple
    "#06B6D4",  # M2 - Cyan
    "#EF4444",  # Markets - Red
]

# Define links (フロー定義)
# source -> target, value
links_source = []
links_target = []
links_value = []
links_color = []

# Fed総資産 → 国債保有
links_source.append(0)
links_target.append(1)
links_value.append(soma_treasury)
links_color.append("rgba(59, 130, 246, 0.4)")

# Fed総資産 → T-Bills
links_source.append(0)
links_target.append(2)
links_value.append(soma_bills)
links_color.append("rgba(59, 130, 246, 0.4)")

# 国債保有 → 銀行準備金 (QEの効果)
links_source.append(1)
links_target.append(3)
links_value.append(reserves * 0.7)  # 準備金の大部分は国債購入由来
links_color.append("rgba(139, 92, 246, 0.4)")

# T-Bills → 銀行準備金
links_source.append(2)
links_target.append(3)
links_value.append(soma_bills * 0.8)
links_color.append("rgba(139, 92, 246, 0.4)")

# 銀行準備金 → 各種融資
links_source.append(3)
links_target.append(6)
links_value.append(ci_loans * 0.3)
links_color.append("rgba(236, 72, 153, 0.4)")

links_source.append(3)
links_target.append(7)
links_value.append(cre_loans * 0.3)
links_color.append("rgba(244, 114, 182, 0.4)")

links_source.append(3)
links_target.append(8)
links_value.append(consumer_loans * 0.5)
links_color.append("rgba(251, 113, 133, 0.4)")

links_source.append(3)
links_target.append(9)
links_value.append(bank_securities * 0.2)
links_color.append("rgba(167, 139, 250, 0.4)")

# 銀行準備金 → RRP (余剰資金の駐車)
links_source.append(3)
links_target.append(5)
links_value.append(on_rrp)
links_color.append("rgba(245, 158, 11, 0.5)")

# 財務省(TGA) ← Fed (国債発行収入)
links_source.append(0)
links_target.append(4)
links_value.append(tga)
links_color.append("rgba(16, 185, 129, 0.4)")

# TGA → 市場 (財政支出)
links_source.append(4)
links_target.append(11)
links_value.append(tga * 0.8)
links_color.append("rgba(16, 185, 129, 0.4)")

# 融資 → M2 (信用創造)
links_source.append(6)
links_target.append(10)
links_value.append(ci_loans * 0.5)
links_color.append("rgba(6, 182, 212, 0.4)")

links_source.append(7)
links_target.append(10)
links_value.append(cre_loans * 0.4)
links_color.append("rgba(6, 182, 212, 0.4)")

links_source.append(8)
links_target.append(10)
links_value.append(consumer_loans * 0.8)
links_color.append("rgba(6, 182, 212, 0.4)")

# 有価証券 → 市場
links_source.append(9)
links_target.append(11)
links_value.append(bank_securities * 0.3)
links_color.append("rgba(239, 68, 68, 0.4)")

# Create Sankey diagram
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

st.plotly_chart(fig, use_container_width=True)

# ========== KEY METRICS SUMMARY ==========
st.markdown(f"### {t('money_flow_key_metrics')}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        t('money_flow_fed_assets'),
        format_value(soma_total),
        help=t('money_flow_fed_assets_help')
    )

with col2:
    st.metric(
        t('money_flow_net_liquidity'),
        format_value(net_liquidity),
        delta=f"TGA: -{format_value(tga)}, RRP: -{format_value(on_rrp)}",
        help=t('money_flow_net_liquidity_help')
    )

with col3:
    st.metric(
        t('money_flow_bank_reserves'),
        format_value(reserves),
        help=t('money_flow_bank_reserves_help')
    )

with col4:
    st.metric(
        t('money_flow_m2'),
        format_value(m2),
        help=t('money_flow_m2_help')
    )

# ========== FLOW EXPLANATION ==========
st.markdown(f"### {t('money_flow_explanation_title')}")

with st.expander(t('money_flow_explanation_expand'), expanded=True):
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
= {format_value(soma_total)} - {format_value(tga)} - {format_value(on_rrp)}
= {format_value(net_liquidity)}
```
""")

# ========== ABSORPTION ANALYSIS ==========
st.markdown(f"### {t('money_flow_absorption_title')}")

# RRP vs TGA pie chart
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
    # Absorption ratio analysis
    total_absorption = tga + on_rrp
    absorption_ratio = (total_absorption / soma_total) * 100
    
    st.markdown(f"#### {t('money_flow_absorption_analysis')}")
    
    st.metric(
        t('money_flow_total_absorption'),
        format_value(total_absorption),
        delta=f"{absorption_ratio:.1f}% {t('money_flow_of_fed_assets')}"
    )
    
    st.progress(min(absorption_ratio / 30, 1.0))  # 30%を上限として表示
    
    if absorption_ratio > 20:
        st.warning(t('money_flow_high_absorption_warning'))
    elif absorption_ratio > 10:
        st.info(t('money_flow_moderate_absorption_info'))
    else:
        st.success(t('money_flow_low_absorption_success'))

# ========== FOOTER ==========
st.markdown("---")
st.caption(t('money_flow_footer'))
