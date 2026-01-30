# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 9: Banking Sector
銀行セクター（H.8週次データ、SLOOS四半期調査）
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import uuid
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    t,
    show_metric_with_sparkline,
    styled_line_chart,
    EXPLANATIONS,
    DATA_FREQUENCY,
)

# Get data from session state
df = st.session_state.get('df')
df_original = st.session_state.get('df_original')

if df is None:
    st.error(t('error_data_not_loaded'))
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader(t('banking_title'))
st.caption(t('bank_subtitle'))

# === H.8 Weekly Data ===
with st.expander(t('bank_h8_section'), expanded=True):
    st.caption(t('bank_h8_desc'))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"#### {t('bank_cash')}")
        show_metric_with_sparkline("Bank Cash", df.get('Bank_Cash'), 'Bank_Cash', "B", "Bank_Cash", notes=t('bank_cash_notes'))
        if 'Bank_Cash' in df.columns and not df.get('Bank_Cash', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['Bank_Cash']], height=200)

    with col2:
        st.markdown(f"#### {t('bank_ci_loans')}")
        show_metric_with_sparkline("C&I Loans", df.get('CI_Loans'), 'CI_Loans', "B", "CI_Loans", notes=t('bank_ci_loans_notes'))
        if 'CI_Loans' in df.columns and not df.get('CI_Loans', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['CI_Loans']], height=200)

    with col3:
        st.markdown(f"#### {t('bank_cre_loans')}")
        show_metric_with_sparkline("CRE Loans", df.get('CRE_Loans'), 'CRE_Loans', "B", "CRE_Loans", notes=t('bank_cre_loans_notes'))
        if 'CRE_Loans' in df.columns and not df.get('CRE_Loans', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['CRE_Loans']], height=200)

# Additional H.8 Data row
st.markdown("---")
with st.expander(t('bank_h8_consumer'), expanded=True):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"#### {t('bank_credit_card')}")
        show_metric_with_sparkline("Credit Card", df.get('Credit_Card_Loans'), 'Credit_Card_Loans', "B", "Credit_Card_Loans", notes=t('bank_credit_card_notes'))
        if 'Credit_Card_Loans' in df.columns and not df.get('Credit_Card_Loans', pd.Series()).isna().all():
            styled_line_chart(df[['Credit_Card_Loans']], height=150)

    with col2:
        st.markdown(f"#### {t('bank_consumer_loans')}")
        show_metric_with_sparkline("Consumer", df.get('Consumer_Loans'), 'Consumer_Loans', "B", "Consumer_Loans", notes=t('bank_consumer_loans_notes'))
        if 'Consumer_Loans' in df.columns and not df.get('Consumer_Loans', pd.Series()).isna().all():
            styled_line_chart(df[['Consumer_Loans']], height=150)

    with col3:
        st.markdown(f"#### {t('bank_securities')}")
        show_metric_with_sparkline("Securities", df.get('Bank_Securities'), 'Bank_Securities', "B", "Bank_Securities", notes=t('bank_securities_notes'))
        if 'Bank_Securities' in df.columns and not df.get('Bank_Securities', pd.Series()).isna().all():
            styled_line_chart(df[['Bank_Securities']], height=150)

    with col4:
        st.markdown(f"#### {t('bank_deposits_title')}")
        show_metric_with_sparkline("Deposits", df.get('Bank_Deposits'), 'Bank_Deposits', "B", "Bank_Deposits", notes=t('bank_deposits_notes'))
        if 'Bank_Deposits' in df.columns and not df.get('Bank_Deposits', pd.Series()).isna().all():
            styled_line_chart(df[['Bank_Deposits']], height=150)

# === Financial Stress Indicators ===
st.markdown("---")
with st.expander(t('bank_stress_section'), expanded=True):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"#### {t('bank_move')}")
        st.caption(t('bank_move_desc'))
        show_metric_with_sparkline("MOVE", df.get('MOVE'), 'MOVE', "pt", "MOVE", notes=t('bank_move_notes'))
        if 'MOVE' in df.columns and not df.get('MOVE', pd.Series()).isna().all():
            styled_line_chart(df[['MOVE']], height=150)

    with col2:
        st.markdown(f"#### {t('bank_small_deposits')}")
        st.caption(t('bank_small_deposits_desc'))
        show_metric_with_sparkline("Small Banks", df.get('Small_Bank_Deposits'), 'Small_Bank_Deposits', "B", "Small_Bank_Deposits", notes=t('bank_small_deposits_notes'))
        if 'Small_Bank_Deposits' in df.columns and not df.get('Small_Bank_Deposits', pd.Series()).isna().all():
            styled_line_chart(df[['Small_Bank_Deposits']], height=150)

    with col3:
        st.markdown(f"#### {t('bank_nfci')}")
        st.caption(t('bank_nfci_desc'))
        show_metric_with_sparkline("NFCI", df.get('NFCI'), 'NFCI', "", "NFCI", notes=t('bank_nfci_notes'))
        if 'NFCI' in df.columns and not df.get('NFCI', pd.Series()).isna().all():
            styled_line_chart(df[['NFCI']], height=150)

    with col4:
        st.markdown(f"#### {t('bank_cc_delinquency')}")
        st.caption(t('bank_cc_delinquency_desc'))
        show_metric_with_sparkline("Delinquency", df.get('CC_Delinquency'), 'CC_Delinquency', "%", "CC_Delinquency", notes=t('bank_cc_delinquency_notes'))
        if 'CC_Delinquency' in df.columns and not df.get('CC_Delinquency', pd.Series()).isna().all():
            styled_line_chart(df[['CC_Delinquency']], height=150)

    # Row 2: More stress indicators
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"#### {t('bank_breakeven')}")
        st.caption(t('bank_breakeven_desc'))
        show_metric_with_sparkline("Breakeven", df.get('Breakeven_10Y'), 'Breakeven_10Y', "%", "Breakeven_10Y", notes=t('bank_breakeven_notes'))
        if 'Breakeven_10Y' in df.columns and not df.get('Breakeven_10Y', pd.Series()).isna().all():
            styled_line_chart(df[['Breakeven_10Y']], height=150)

    with col2:
        st.markdown(f"#### {t('bank_cp_spread')}")
        st.caption(t('bank_cp_spread_desc'))
        show_metric_with_sparkline("CP-FF", df.get('CP_Spread'), 'CP_Spread', "%", "CP_Spread", notes=t('bank_cp_spread_notes'))
        if 'CP_Spread' in df.columns and not df.get('CP_Spread', pd.Series()).isna().all():
            styled_line_chart(df[['CP_Spread']], height=150)

    with col3:
        st.markdown(f"#### {t('bank_total_loans')}")
        st.caption(t('bank_total_loans_desc'))
        show_metric_with_sparkline("Loans", df.get('Total_Loans'), 'Total_Loans', "B", "Total_Loans", notes=t('bank_total_loans_notes'))
        if 'Total_Loans' in df.columns and not df.get('Total_Loans', pd.Series()).isna().all():
            styled_line_chart(df[['Total_Loans']], height=150)

    with col4:
        st.markdown(f"#### {t('bank_copper_gold')}")
        st.caption(t('bank_copper_gold_desc'))
        if 'Copper' in df.columns and 'Gold' in df.columns:
            copper = df.get('Copper')
            gold = df.get('Gold')
            if copper is not None and gold is not None:
                ratio_series = (copper / gold) * 1000
                latest_val = ratio_series.dropna().iloc[-1] if not ratio_series.dropna().empty else 0
                st.metric(t('bank_cu_au_ratio'), f"{latest_val:.2f}", help=t('bank_cu_au_help'))
                
                # 日付情報を表示
                if hasattr(df, 'attrs'):
                    copper_date = df.attrs.get('last_valid_dates', {}).get('Copper')
                    if copper_date:
                        st.caption(f"📅 {t('data_period')}: {copper_date} ({t('freq_daily')})")
                        st.caption(f"🔄 {t('source_update')}: {copper_date}")  # yFinanceはlast_valid_datesを使用
                    st.caption(t('bank_cu_au_notes'))  # Rise=Risk-on, Fall=Risk-off
                
                # 60日推移（スパークライン）
                if not ratio_series.dropna().empty:
                    recent_60 = ratio_series.tail(60)
                    st.caption(f"📊 {t('sparkline_label')}")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=recent_60.index,
                        y=recent_60.values,
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
                        hovermode=False
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False},
                                   key=f"spark_cu_au_{uuid.uuid4().hex[:8]}")
                    
                    # 長期推移
                    st.markdown(f"###### {t('long_term_trend')}")
                    styled_line_chart(ratio_series, height=150)

st.markdown("---")

# === SLOOS C&I Section ===
with st.expander(f"💰 C&I Lending - {t('bank_sloos_section')}", expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {t('bank_ci_tightening')}")
        st.caption(t('bank_ci_tightening_notes'))
        show_metric_with_sparkline("Large/Mid Firms", df.get('CI_Std_Large'), 'CI_Std_Large', "pts", "CI_Std_Large", notes=t('bank_ci_tightening_indicator_notes'))
        if 'CI_Std_Large' in df.columns and not df.get('CI_Std_Large', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['CI_Std_Large']], height=200)

    with col2:
        st.markdown(f"#### {t('bank_ci_std_small')}")
        show_metric_with_sparkline("Small Firms", df.get('CI_Std_Small'), 'CI_Std_Small', "pts", "CI_Std_Small", notes=t('bank_ci_std_small_notes'))
        if 'CI_Std_Small' in df.columns and not df.get('CI_Std_Small', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['CI_Std_Small']], height=200)
        
        st.markdown("---")
        
        st.markdown(f"#### {t('bank_ci_demand')}")
        st.caption(t('bank_ci_demand_notes'))
        show_metric_with_sparkline("Demand", df.get('CI_Demand'), 'CI_Demand', "pts", "CI_Demand", notes=t('bank_ci_demand_indicator_notes'))
        if 'CI_Demand' in df.columns and not df.get('CI_Demand', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['CI_Demand']], height=200)

st.markdown("---")

# === SLOOS CRE Section ===
with st.expander(t('bank_cre_section'), expanded=True):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### {t('bank_cre_construction')}")
        show_metric_with_sparkline("Construction", df.get('CRE_Std_Construction'), 'CRE_Std_Construction', "pts", "CRE_Std_Construction", notes=t('bank_cre_construction_notes'))
        if 'CRE_Std_Construction' in df.columns and not df.get('CRE_Std_Construction', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['CRE_Std_Construction']], height=200)
        
        st.markdown("---")
        
        st.markdown(f"#### {t('bank_cre_multifamily')}")
        show_metric_with_sparkline("Multifamily", df.get('CRE_Std_Multifamily'), 'CRE_Std_Multifamily', "pts", "CRE_Std_Multifamily", notes=t('bank_cre_multifamily_notes'))
        if 'CRE_Std_Multifamily' in df.columns and not df.get('CRE_Std_Multifamily', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['CRE_Std_Multifamily']], height=200)

    with col2:
        st.markdown(f"#### {t('bank_cre_office')}")
        show_metric_with_sparkline("Office/NonRes", df.get('CRE_Std_Office'), 'CRE_Std_Office', "pts", "CRE_Std_Office", notes=t('bank_cre_office_notes'))
        if 'CRE_Std_Office' in df.columns and not df.get('CRE_Std_Office', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['CRE_Std_Office']], height=200)
        
        st.markdown("---")
        
        st.markdown(f"#### {t('bank_cre_demand')}")
        st.caption(t('bank_cre_demand_notes'))
        show_metric_with_sparkline("CRE Demand", df.get('CRE_Demand'), 'CRE_Demand', "pts", "CRE_Demand", notes=t('bank_cre_demand_indicator_notes'))
        if 'CRE_Demand' in df.columns and not df.get('CRE_Demand', pd.Series()).isna().all():
            st.markdown(f"###### {t('long_term_trend')}")
            styled_line_chart(df[['CRE_Demand']], height=200)

# === Loan Comparison Chart ===
st.markdown("---")
with st.expander(t('bank_loan_comparison'), expanded=True):
    loan_cols = [c for c in ['CI_Loans', 'CRE_Loans'] if c in df.columns and not df[c].isna().all()]
    if loan_cols:
        styled_line_chart(df[loan_cols].tail(520), height=250)
