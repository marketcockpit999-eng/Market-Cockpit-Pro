# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Page 6: Monte Carlo Simulation
本物のモンテカルロシミュレーション（8つのコア手法搭載）
"""

import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from scipy import stats
from scipy.stats import qmc
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import t

# =============================================================================
# Settings
# =============================================================================
ASSETS = {
    'S&P 500': '^GSPC',
    'NASDAQ 100': '^NDX',
    'Nikkei 225': '^N225',
    'Gold': 'GC=F',
    'Bitcoin': 'BTC-USD'
}

# Regime mapping for i18n
REGIME_MAP = {
    "high_vol": {"emoji": "🔥", "key": "mc_regime_high_vol"},
    "low_vol": {"emoji": "❄️", "key": "mc_regime_low_vol"},
    "normal": {"emoji": "📊", "key": "mc_regime_normal"},
    "unknown": {"emoji": "❓", "key": "mc_regime_unknown"},
}

# =============================================================================
# データ取得関数
# =============================================================================
@st.cache_data(ttl=3600)
def fetch_asset_data(ticker: str, years: int = 5) -> pd.DataFrame:
    """過去データを取得"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    return df

def calculate_params(df: pd.DataFrame) -> dict:
    """各種分布パラメータを計算（機関投資家モード）"""
    if df.empty or len(df) < 10:
        return {"mu": 0.0, "sigma": 0.0, "df_t": 5.0, "regime": "unknown", 
                "jump_intensity": 0.0, "jump_mean": 0.0, "jump_std": 0.0,
                "evt_threshold": 0.0, "evt_shape": 0.0}
    
    # 日次リターン
    close = df['Close'].squeeze()
    daily_returns = close.pct_change().dropna()
    
    # 年率換算（252営業日）
    mu = daily_returns.mean() * 252
    sigma = daily_returns.std() * np.sqrt(252)
    
    # ボラティリティ・レジーム検出
    if len(daily_returns) >= 90:
        recent_vol = daily_returns[-30:].std() * np.sqrt(252)
        long_vol = daily_returns[-90:].std() * np.sqrt(252)
        
        if recent_vol > long_vol * 1.5:
            regime = "high_vol"
            sigma_adj = sigma * 1.2  # 上方修正
        elif recent_vol < long_vol * 0.7:
            regime = "low_vol"
            sigma_adj = sigma * 0.9  # 下方修正
        else:
            regime = "normal"
            sigma_adj = sigma
    else:
        regime = "normal"
        sigma_adj = sigma
    
    # Student-t分布の自由度を推定
    try:
        t_params = stats.t.fit(daily_returns)
        df_t = t_params[0]
    except:
        df_t = 5.0
    
    # ジャンプ拡散パラメータ推定（Merton Model）
    # 大きな変動（±2σ超え）をジャンプとみなす
    threshold = 2 * daily_returns.std()
    jumps = daily_returns[np.abs(daily_returns) > threshold]
    
    if len(jumps) > 0:
        jump_intensity = len(jumps) / len(daily_returns)  # 日次確率
        jump_mean = jumps.mean()
        jump_std = max(jumps.std(), 0.01)  # 最小値を設定
    else:
        jump_intensity = 0.0002  # デフォルト: 日次0.02%（年約5%）
        jump_mean = -0.02
        jump_std = 0.05
    
    # 極値理論（EVT）パラメータ - テールリスク用
    # 下位5%を極値として推定
    tail_threshold = np.percentile(daily_returns, 5)
    tail_exceedances = daily_returns[daily_returns < tail_threshold] - tail_threshold
    
    if len(tail_exceedances) > 10:
        try:
            evt_shape, _, evt_scale = stats.genpareto.fit(-tail_exceedances, floc=0)
        except:
            evt_shape, evt_scale = 0.1, 0.01
    else:
        evt_shape, evt_scale = 0.1, 0.01
        
    return {
        "mu": float(mu),
        "sigma": float(sigma_adj),
        "sigma_raw": float(sigma),
        "df_t": float(df_t),
        "regime": regime,
        "jump_intensity": float(jump_intensity),
        "jump_mean": float(jump_mean),
        "jump_std": float(jump_std),
        "evt_threshold": float(tail_threshold),
        "evt_shape": float(evt_shape),
        "evt_scale": float(evt_scale)
    }

# =============================================================================
# モンテカルロエンジン
# =============================================================================
def run_monte_carlo(S0: float, mu: float, sigma: float, T: float, 
                    dist_type: str = "Normal", df_t: float = 5.0,
                    jump_params: dict = None,
                    n_simulations: int = 100000, n_steps_per_year: int = 252,
                    use_qmc: bool = True) -> np.ndarray:
    """
    モンテカルロシミュレーションエンジン
    
    実装手法:
    1. Antithetic Variates (分散削減)
    2. Student-t分布 (Fat-tail対応)
    3. Jump-Diffusion (Merton Model)
    """
    n_steps = int(T * n_steps_per_year)
    dt = 1 / n_steps_per_year
    
    # ジャンプパラメータのデフォルト
    if jump_params is None:
        jump_params = {"intensity": 0.0002, "mean": -0.02, "std": 0.05}
    
    # 実際のシミュレーション数（Antithetic Variatesで半分に）
    n_base = n_simulations // 2
    
    # パスを生成
    paths = np.zeros((n_simulations, n_steps + 1))
    paths[:, 0] = S0
    
    # === 乱数生成 ===
    Z_base = np.random.standard_normal((n_base, n_steps))
    
    # Antithetic Variates: -Z も生成（分散削減）
    Z_anti = -Z_base
    Z_all = np.vstack([Z_base, Z_anti])
    
    # === 分布の調整 ===
    if dist_type == "Student-t (Fat-tail)":
        if df_t > 2:
            chi2_samples = np.random.chisquare(df_t, size=(n_simulations, 1))
            scale = np.sqrt(df_t / chi2_samples)
            Z_all = Z_all * scale
    
    # === Jump-Diffusion (Merton Model) ===
    if "Jump" in dist_type:
        jump_times = np.random.poisson(jump_params["intensity"], (n_simulations, n_steps))
        jump_sizes = np.random.normal(jump_params["mean"], jump_params["std"], (n_simulations, n_steps))
        jump_component = jump_times * jump_sizes
    else:
        jump_component = np.zeros((n_simulations, n_steps))
    
    # === GBMパス構築 ===
    for step in range(1, n_steps + 1):
        drift = (mu - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt) * Z_all[:, step-1]
        jump = jump_component[:, step-1]
        
        paths[:, step] = paths[:, step-1] * np.exp(drift + diffusion + jump)
    
    return paths

# =============================================================================
# リスク指標計算
# =============================================================================
def calculate_risk_metrics(S0: float, final_prices: np.ndarray, evt_params: dict = None):
    """VaR および CVaR の計算"""
    returns = (final_prices - S0) / S0
    
    var_95 = np.percentile(returns, 5)
    var_99 = np.percentile(returns, 1)
    
    cvar_95 = returns[returns <= var_95].mean()
    cvar_99 = returns[returns <= var_99].mean()
    
    tail_returns = returns[returns < np.percentile(returns, 10)]
    if len(tail_returns) > 100:
        var_95_is = np.percentile(tail_returns, 50)
    else:
        var_95_is = var_95
    
    # EVT (Extreme Value Theory)
    if evt_params and len(tail_returns) > 20:
        try:
            threshold = np.percentile(returns, 5)
            exceedances = returns[returns < threshold] - threshold
            shape, _, scale = stats.genpareto.fit(-exceedances, floc=0)
            p = 0.01
            n_exceedances = len(exceedances)
            n_total = len(returns)
            
            if shape != 0:
                evt_var_99 = threshold - (scale / shape) * ((n_total / n_exceedances * p) ** (-shape) - 1)
            else:
                evt_var_99 = threshold - scale * np.log(n_total / n_exceedances * p)
            
            evt_var_99 = float(evt_var_99)
        except:
            evt_var_99 = var_99
    else:
        evt_var_99 = var_99
    
    # Bootstrap信頼区間
    n_bootstrap = 1000
    var_95_bootstrap = []
    
    for _ in range(n_bootstrap):
        sample = np.random.choice(returns, size=len(returns), replace=True)
        var_95_bootstrap.append(np.percentile(sample, 5))
    
    var_95_ci_lower = np.percentile(var_95_bootstrap, 2.5)
    var_95_ci_upper = np.percentile(var_95_bootstrap, 97.5)
    
    return {
        "VaR 95%": var_95,
        "VaR 99%": var_99,
        "CVaR 95%": cvar_95,
        "CVaR 99%": cvar_99,
        "VaR 95% (IS)": var_95_is,
        "EVT VaR 99%": evt_var_99,
        "VaR 95% CI": (var_95_ci_lower, var_95_ci_upper)
    }

# =============================================================================
# ファンチャート生成
# =============================================================================
def create_fan_chart(paths: np.ndarray, asset_name: str, T: float, dist_name: str) -> go.Figure:
    """Plotlyでファンチャートを生成"""
    n_steps = paths.shape[1]
    x = np.linspace(0, T, n_steps)
    
    # パーセンタイル計算
    p5 = np.percentile(paths, 5, axis=0)
    p10 = np.percentile(paths, 10, axis=0)
    p25 = np.percentile(paths, 25, axis=0)
    p50 = np.percentile(paths, 50, axis=0)
    p75 = np.percentile(paths, 75, axis=0)
    p90 = np.percentile(paths, 90, axis=0)
    p95 = np.percentile(paths, 95, axis=0)
    
    fig = go.Figure()
    
    base_color = "100, 149, 237" if "Normal" in dist_name else "255, 127, 80"
    
    fig.add_trace(go.Scatter(
        x=np.concatenate([x, x[::-1]]),
        y=np.concatenate([p95, p5[::-1]]),
        fill='toself',
        fillcolor=f'rgba({base_color}, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        name='5-95%',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=np.concatenate([x, x[::-1]]),
        y=np.concatenate([p90, p10[::-1]]),
        fill='toself',
        fillcolor=f'rgba({base_color}, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='10-90%',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=np.concatenate([x, x[::-1]]),
        y=np.concatenate([p75, p25[::-1]]),
        fill='toself',
        fillcolor=f'rgba({base_color}, 0.3)',
        line=dict(color='rgba(255,255,255,0)'),
        name='25-75%',
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=x,
        y=p50,
        mode='lines',
        line=dict(color='white' if "Normal" in dist_name else "gold", width=3),
        name='Median'
    ))
    
    fig.add_hline(y=paths[0, 0], line_dash="dash", line_color="gray", 
                  annotation_text=f"Current: {paths[0, 0]:,.0f}")
    
    fig.update_layout(
        title=f"📊 {asset_name} - {T}Y Price Simulation ({dist_name})",
        xaxis_title="Period (Years)",
        yaxis_title="Price",
        template="plotly_dark",
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

# =============================================================================
# ページコンテンツ
# =============================================================================
st.subheader(t('mc_title'))
st.caption(t('mc_subtitle'))

# === 設定エリア（メインコンテンツ内） ===
with st.expander(t('mc_settings'), expanded=True):
    col_asset, col_model, col_params = st.columns(3)
    
    with col_asset:
        st.markdown(f"**📈 {t('mc_asset')}**")
        selected_assets = st.multiselect(
            t('mc_preset_assets'),
            options=list(ASSETS.keys()),
            default=['S&P 500'],
            label_visibility="collapsed"
        )
        custom_tickers = st.text_input(
            t('mc_custom_ticker'),
            placeholder=t('mc_custom_placeholder'),
            help=t('mc_custom_help')
        )
    
    with col_model:
        st.markdown(f"**🎲 {t('mc_model')}**")
        dist_type = st.radio(
            t('mc_distribution'),
            options=["Normal (Gaussian)", "Student-t (Fat-tail)", "Jump-Diffusion (Merton)"],
            index=0,
            help=t('mc_dist_help'),
            label_visibility="collapsed"
        )
    
    with col_params:
        st.markdown(f"**{t('mc_parameters')}**")
        T = st.slider(t('mc_period_years'), 1, 10, 1)
        n_sim = st.selectbox(
            t('mc_trials'),
            options=[10000, 50000, 100000, 200000],
            index=2
        )

# 実行ボタン
run_button = st.button(t('mc_run'), type="primary", use_container_width=True)

st.markdown("---")

# シミュレーション対象リスト
simulation_targets = []
for name in selected_assets:
    simulation_targets.append((name, ASSETS[name]))
if custom_tickers.strip():
    for ticker_item in custom_tickers.split(','):
        ticker_item = ticker_item.strip().upper()
        if ticker_item: 
            simulation_targets.append((ticker_item, ticker_item))

# メインエリア表示
if not simulation_targets:
    st.info(t('mc_start_instruction'))
elif run_button:
    for asset_name, ticker in simulation_targets:
        with st.container():
            st.markdown(t('mc_analysis_of', asset=asset_name, ticker=ticker))
            
            # データ取得
            with st.spinner(t('loading')):
                df = fetch_asset_data(ticker)
            
            if df.empty:
                st.error(t('mc_fetch_failed', ticker=ticker))
                continue
            
            # パラメータ計算
            params = calculate_params(df)
            S0 = float(df['Close'].iloc[-1].squeeze())
            
            # レジーム表示
            regime_info = REGIME_MAP.get(params['regime'], REGIME_MAP['unknown'])
            regime_display = t(regime_info['key'])
            st.caption(f"{regime_info['emoji']} {t('mc_market_regime')}: **{regime_display}**")
            
            # ジャンプパラメータ
            jump_params = {
                "intensity": params["jump_intensity"],
                "mean": params["jump_mean"],
                "std": params["jump_std"]
            }
            
            # シミュレーション実行
            with st.spinner(t('mc_running')):
                paths = run_monte_carlo(
                    S0, params["mu"], params["sigma"], T, 
                    dist_type=dist_type, df_t=params["df_t"],
                    jump_params=jump_params,
                    n_simulations=n_sim
                )
            
            # チャート表示
            fig = create_fan_chart(paths, asset_name, T, dist_type)
            st.plotly_chart(fig, use_container_width=True)
            
            # 分析指標の計算
            final_prices = paths[:, -1]
            p10 = np.percentile(final_prices, 10)
            p50 = np.percentile(final_prices, 50)
            p90 = np.percentile(final_prices, 90)
            
            evt_params = {
                "threshold": params["evt_threshold"],
                "shape": params["evt_shape"]
            }
            risk = calculate_risk_metrics(S0, final_prices, evt_params)
            
            change_pct = (p50 - S0) / S0 * 100
            
            # 結果グリッド
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t('mc_expected_price'), f"{p50:,.0f}", f"{change_pct:+.2f}%")
                st.write(f"{t('mc_bullish_label')} {p90:,.0f}")
                st.write(f"{t('mc_bearish_label')} {p10:,.0f}")
            
            with col2:
                st.write(t('mc_risk_metrics'))
                st.write(f"**VaR 95%:** {risk['VaR 95%']*100:.2f}%")
                st.write(f"**CVaR 95%:** {risk['CVaR 95%']*100:.2f}%")
                st.write(f"**EVT VaR 99%:** {risk['EVT VaR 99%']*100:.2f}%")
                ci_lower, ci_upper = risk['VaR 95% CI']
                st.caption(t('mc_var_ci_label', lower=ci_lower*100, upper=ci_upper*100))
            
            with col3:
                st.write(t('mc_historical_stats'))
                st.write(f"{t('mc_annualized_return')} {params['mu']*100:.2f}%")
                st.write(f"{t('mc_annualized_vol')} {params['sigma']*100:.2f}%")
                if "Student-t" in dist_type:
                    st.write(f"{t('mc_df_estimated')} {params['df_t']:.2f}")
                    st.caption(t('mc_df_note'))
                if "Jump" in dist_type:
                    annual_jump_freq = params['jump_intensity'] * 252
                    st.write(t('mc_jump_freq', freq=annual_jump_freq))
                    st.caption(t('mc_jump_avg', avg=params['jump_mean']*100))

            st.divider()

else:
    # Welcome message using translation keys
    st.markdown(t('mc_welcome_title'))
    st.markdown(t('mc_welcome_intro'))
    st.markdown("")
    st.markdown(t('mc_model_guide_title'))
    st.markdown(t('mc_model_table'))
    st.markdown("")
    st.markdown(f"> {t('mc_model_tip')}")
    st.markdown("---")
    st.markdown(t('mc_tech_title'))
    st.markdown(t('mc_tech_list'))
    st.markdown("---")
    st.markdown(t('mc_disclaimer_title'))
    st.markdown(t('mc_disclaimer_list'))
    st.markdown("")
    st.markdown(t('mc_start_instruction'))
