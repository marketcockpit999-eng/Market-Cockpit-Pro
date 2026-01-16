# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 6: Monte Carlo Simulation
AI Monte Carlo シミュレーション
"""

import streamlit as st
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import GEMINI_MODEL, CLAUDE_MODEL, get_market_summary, run_gemini_analysis, run_claude_analysis

# Get AI clients and data from session state
gemini_client = st.session_state.get('gemini_client')
claude_client = st.session_state.get('claude_client')
df = st.session_state.get('df')

if df is None:
    st.error("データが読み込まれていません。main.pyから起動してください。")
    st.stop()

# ========== PAGE CONTENT ==========
st.subheader("🎲 AI Monte Carlo Simulation")
st.caption("💡 Claude 4.5 Opusが戦略設計、Gemini 3 Flashが10万回シミュレーション実行")

# Check AI availability
mc_gemini_available = gemini_client is not None
mc_claude_available = claude_client is not None

if not mc_gemini_available or not mc_claude_available:
    st.error("⚠️ この機能には Gemini と Claude の両方のAPIキーが必要です。")
    if not mc_gemini_available:
        st.warning("❌ Gemini API未設定")
    if not mc_claude_available:
        st.warning("❌ Claude API未設定")
else:
    st.success("✅ AI準備完了（Claude 4.5 Opus + Gemini 3 Flash）")
    
    st.markdown("---")
    st.markdown("### 📝 資産状況の入力")
    
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        st.markdown("#### 現在の保有資産")
        mc_btc_amount = st.number_input("BTC保有量", min_value=0.0, max_value=100.0, value=0.8, step=0.1)
        mc_btc_price = st.number_input("BTC現在価格（万円）", min_value=100.0, max_value=10000.0, value=1400.0, step=50.0)
        mc_gold_amount = st.number_input("Gold保有量（万円）", min_value=0.0, max_value=100000.0, value=0.0, step=10.0)
        mc_stocks_amount = st.number_input("株式/ETF保有量（万円）", min_value=0.0, max_value=100000.0, value=0.0, step=50.0)
        mc_cash = st.number_input("現金（万円）", min_value=0.0, max_value=100000.0, value=500.0, step=50.0)
        mc_investment_trust = st.number_input("投資信託（万円）", min_value=0.0, max_value=100000.0, value=150.0, step=10.0)
    
    with col_input2:
        st.markdown("#### シミュレーション設定")
        mc_monthly_deposit = st.number_input("月間追加入金（万円）", min_value=0.0, max_value=1000.0, value=25.0, step=5.0)
        mc_survival_line = st.number_input("生存ライン（BTC円建て万円）", min_value=50.0, max_value=5000.0, value=300.0, step=50.0)
        mc_simulation_years = st.selectbox("シミュレーション期間", [5, 10, 15, 20], index=1)
        mc_num_trials = st.selectbox("試行回数", [1000, 10000, 100000], index=2)
        
        st.markdown("#### 🎯 Buy-the-Dip 戦略設定")
        mc_crash_threshold = st.slider("暴落トリガー（高値からの下落率 %）", min_value=-70, max_value=-10, value=-30, step=5)
        mc_cash_deploy_ratio = st.slider("1回あたり現金投入比率 (%)", min_value=10, max_value=100, value=30, step=5)
        mc_buy_btc_ratio = st.slider("BTC (%)", min_value=0, max_value=100, value=50, step=5)
        mc_buy_gold_ratio = st.slider("Gold (%)", min_value=0, max_value=100, value=50, step=5)
        
        total_ratio = mc_buy_btc_ratio + mc_buy_gold_ratio
        if total_ratio != 100:
            st.warning(f"⚠️ 配分合計が{total_ratio}%です（100%推奨）")
    
    # Asset Summary
    st.markdown("---")
    st.markdown("### 📊 現在の資産サマリー")
    
    mc_btc_value = mc_btc_amount * mc_btc_price
    mc_total_assets = mc_btc_value + mc_gold_amount + mc_stocks_amount + mc_cash + mc_investment_trust
    
    col_sum1, col_sum2, col_sum3 = st.columns(3)
    with col_sum1:
        st.metric("BTC評価額", f"¥{mc_btc_value:.0f}万")
        st.metric("Gold", f"¥{mc_gold_amount:.0f}万")
    with col_sum2:
        st.metric("株式/ETF", f"¥{mc_stocks_amount:.0f}万")
        st.metric("投資信託", f"¥{mc_investment_trust:.0f}万")
    with col_sum3:
        st.metric("現金", f"¥{mc_cash:.0f}万")
        st.metric("総資産", f"¥{mc_total_assets:.0f}万", delta=f"月+{mc_monthly_deposit}万")
    
    # Store parameters
    mc_params = {
        "btc_amount": mc_btc_amount,
        "btc_price": mc_btc_price * 10000,
        "gold_amount": mc_gold_amount * 10000,
        "stocks_amount": mc_stocks_amount * 10000,
        "cash": mc_cash * 10000,
        "investment_trust": mc_investment_trust * 10000,
        "monthly_deposit": mc_monthly_deposit * 10000,
        "survival_line": mc_survival_line * 10000,
        "years": mc_simulation_years,
        "trials": mc_num_trials,
        "buy_ratio": {"btc": mc_buy_btc_ratio / 100, "gold": mc_buy_gold_ratio / 100},
        "dip_settings": {"crash_threshold": mc_crash_threshold / 100, "cash_deploy_ratio": mc_cash_deploy_ratio / 100}
    }
    st.session_state['mc_params'] = mc_params
    
    st.markdown("---")
    st.markdown("### 🚀 シミュレーション実行")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🧠 Step 1: Claudeで戦略設計", type="primary", key="mc_claude"):
            market_summary = get_market_summary(df)
            
            claude_mc_prompt = f"""以下の市場状況と投資家の資産状況に基づいて、モンテカルロシミュレーション用のパラメータを設計してください。

【現在の市場状況】
{market_summary}

【投資家の資産状況】
- BTC保有: {mc_params['btc_amount']} BTC
- 現金: {mc_params['cash']:,.0f}円
- 月間追加入金: {mc_params['monthly_deposit']:,.0f}円

【シミュレーション要件】
- 期間: {mc_params['years']}年
- 試行回数: {mc_params['trials']:,}回
- 生存ライン: BTC円建て {mc_params['survival_line']:,.0f}円

【出力形式】
以下のJSON形式でパラメータを出力してください：
```json
{{
    "parameters": {{
        "btc": {{"expected_return": 0.XX, "volatility": 0.XX, "correlation_to_liquidity": 0.XX}},
        "gold": {{"expected_return": 0.XX, "volatility": 0.XX}},
        "cash_yield": 0.XX
    }},
    "crash_threshold": -0.XX,
    "buy_amount_ratio": 0.XX,
    "rebalance_frequency": "monthly/quarterly",
    "rationale": "パラメータ設定の根拠を日本語で説明"
}}
```"""
            
            with st.spinner("🧠 Claude Opus 4.5 が戦略を設計中..."):
                try:
                    claude_result = run_claude_analysis(claude_client, CLAUDE_MODEL, claude_mc_prompt)
                    st.markdown("### 🧠 Claude 戦略設計")
                    st.markdown(claude_result)
                    
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', claude_result, re.DOTALL)
                    if json_match:
                        try:
                            strategy_params = json.loads(json_match.group(1))
                            st.session_state['mc_strategy_params'] = strategy_params
                            st.success("✅ パラメータをパース完了。Step 2でシミュレーション実行可能です。")
                        except json.JSONDecodeError:
                            st.warning("⚠️ JSONパースに失敗。手動でパラメータを確認してください。")
                except Exception as e:
                    st.error(f"❌ Claude エラー: {str(e)}")
    
    with col_btn2:
        if st.button("⚡ Step 2: Geminiでシミュレーション実行", type="secondary", key="mc_gemini"):
            if 'mc_strategy_params' not in st.session_state:
                st.warning("⚠️ まずStep 1でClaudeによる戦略設計を実行してください。")
            else:
                strategy = st.session_state['mc_strategy_params']
                params = st.session_state.get('mc_params', mc_params)
                
                gemini_mc_prompt = f"""以下のパラメータでモンテカルロシミュレーションをPythonで実行し、結果を分析してください。

【シミュレーションパラメータ】
{json.dumps(strategy, indent=2, ensure_ascii=False)}

【初期資産】
- BTC: {params['btc_amount']} BTC
- 現金: {params['cash']:,.0f}円
- 月間追加入金: {params['monthly_deposit']:,.0f}円

【シミュレーション条件】
- 期間: {params['years']}年（{params['years'] * 12}ヶ月）
- 試行回数: {params['trials']:,}回
- 生存ライン: {params['survival_line']:,.0f}円

【出力要求】
1. 資産予測サマリー（中央値、上位10%、下位10%）
2. リスク分析（生存ライン下回る確率、最大ドローダウン）
3. Buy-the-Dipの効果分析
4. 結論と推奨アクション"""
                
                with st.spinner(f"⚡ Gemini がシミュレーション中... ({params['trials']:,}回試行)"):
                    try:
                        gemini_result = run_gemini_analysis(gemini_client, GEMINI_MODEL, gemini_mc_prompt)
                        st.session_state['mc_gemini_result'] = gemini_result
                        st.session_state['mc_simulation_complete'] = True
                        st.success(f"✅ シミュレーション完了！")
                    except Exception as e:
                        st.error(f"❌ Gemini エラー: {str(e)}")
    
    # Results display
    st.markdown("---")
    st.markdown("### 📈 シミュレーション結果")
    
    if st.session_state.get('mc_simulation_complete') and 'mc_gemini_result' in st.session_state:
        st.markdown(st.session_state['mc_gemini_result'])
    else:
        st.caption("Step 1 と Step 2 を実行するとここに結果が表示されます")
    
    with st.expander("📋 入力パラメータ", expanded=False):
        st.json(mc_params)
