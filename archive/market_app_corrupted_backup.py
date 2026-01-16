import streamlit as st
import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
import datetime
import os
import warnings
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import feedparser

warnings.simplefilter('ignore')

# --- 1. 設宁E& 定数 ---
PAGE_TITLE = "Market Cockpit Pro"

# FRED持EE(Restored & Complete)
FRED_INDICATORS = {
    # Plumbing
    'ON_RRP': 'RRPONTSYD',         
    'Reserves': 'WRESBAL',         
    'TGA': 'WTREGEN',              
    'Fed_Assets': 'WALCL',         
    'SOMA_Bills': 'WSHOBL',        
    'SOMA_Total': 'WALCL',       
    'SRF': 'WORAL',              
    'FIMA': 'H41RESPPALGTRFNWW',            
    'Primary_Credit': 'WLCFLPCL',  
    'Total_Loans': 'H41RESPALDKNWW',
    'EFFR': 'EFFR',                
    'IORB': 'IORB',                
    'SOFR': 'SOFR',
    
    # Banking Sector Behavior
    'Bank_Cash': 'CASACBW027SBOG',  # Cash Assets, All Commercial Banks (Weekly)
    'Lending_Standards': 'DRTSCILM',  # Net % tightening C&I loans to large/mid firms
    
    # Rates & Bonds
    'Credit_Spread': 'BAMLH0A0HYM2', 
    'Breakeven_10Y': 'T10YIE',       
    'US_TNX': 'DGS10',               

    # Macro
    'Unemployment': 'UNRATE',       
    'NonFarm_Payroll': 'PAYEMS',    
    'Initial_Claims': 'ICSA',       
    'CPI': 'CPIAUCSL',              
    'Housing_Starts': 'HOUST',      
    'Mortgage_30Y': 'MORTGAGE30US', 

    # Global Liquidity
    'US_M2': 'M2SL',                'US_CPI': 'CPIAUCSL',
    'CN_M2': 'MYAGM2CNM189N',       'CN_CPI': 'CHNCPIALLMINMEI',
    'EU_M2': 'MABMM301EZM189S',     'EU_CPI': 'CP0000EZ19M086NEST',
    'JP_M2': 'MANMM101JPM189S',     'JP_CPI': 'JPNCPIALLMINMEI'
}

# Yahoo Indicators
YAHOO_INDICATORS = {
    'HYG': 'HYG', 'US10Y': '^TNX', 
    'WTI': 'CL=F', 'Gold': 'GC=F', 'Silver': 'SI=F', 
    'Bitcoin': 'BTC-USD', 'Ethereum': 'ETH-USD',
    'DXY': 'DX-Y.NYB', 'VIX': '^VIX',
    'USDJPY': 'JPY=X', 'USDCNY': 'CNY=X',
    'SP500': '^GSPC', 'Nasdaq': '^IXIC' 
}

# 解説チEスチE(初忁EEけ辞書)
EXPLANATIONS = {
    # Plumbing
    "Net_Liquidity": "【ネチEリクイチEチE】\n市場に出回る「真の賁E量」、EFRB総賁E - TGA - RRP) で計算されます、Enこれが株価めE号賁Eの本源的な燁Eです、E,
    "Reserves": "【銀行準備預 (Reserves)】\n民間銀行がFRBに預けてぁEお、Enこれが減りすぎると銀行シスチEが不安定になり、ショチEが起きやすくなります、E,
    "TGA": "【TGA (財務省一般口座)】\n政府E銀行口座、Enここにおが増えると市場から賁Eが吸ぁEげられ(株安要因)、減ると市場に放出されまぁE株高要因)、E,
    "ON_RRP": "【ON RRP (翌日物リバEスレチE】\nMMFなどがFRBにおを預ける場所、Enこれが高いE市場に投賁EEがなく、余剰賁Eが滞留してぁEことを示します、E,
    "SomaBillsRatio": "【この持EE意味】\nこE比率が上がってぁEE総賁Eに占める短期国債の割合が増える）ことは、FRBがいつでも市場に現金を放出しやすい『機動皁EポEトフォリオ』に変えてぁEことを意味します。これE、準備預の枯渁E防ぐためE『実質皁E緩和準備EEMPE準備金管琁EEための購入E』と捉えることができます、E,
    "SOMA_Total": "【SOMA (公開市場操作用賁E)】\nFRBが保有する国債やMBSの総額、Enこれが増える＝量皁E咁EQE)、減るE量皁Eき締めEQT)です、E,
    "RMP": "【SOMA Bills (短期国債)】\nFRBが保有する「短期」国債、En通常、ここが増えると隠れQEE賁E供給EE疑いがあります、E,
    "SRF": "【SRF (常設レポファシリチE)】\n国債を担保に現金を借りる窓口。通常の市場操作に近いため『不名誉（スチEグマ）』が低く、E利高騰を抑える役割を持ちます、E,
    "FIMA": "【FIMA Repo Facility】\n海外中銀向け。米国債をドルに交換し、世界皁Eドル不足Eドル・ショート）を解消するためEバックストップです、E,
    "Window": "【Total Loans】\nFRBによる金融機関への貸出総額。市場の「緊急事E」を測る総合持Eです、E,
    "Primary": "【Primary Credit (窓口貸出)】\n健全行向けE緊急融賁ESRFより幁EE拁E（ローン等）が可能ですが、利用が目立ちめEく『不名誉（スチEグマ）』が強ぁE向があります、E,
    "EFFR_IORB": "【EFFR - IORB 乖離】\n実効連邦基金利と準備預付利の差、E%に近づく、またEプラスになると、E行E余剰賁Eが枯渁EてぁEシグナルです、E,
    "SOFR": "【SOFR (拁E付翌日物調達利)】\n国債を担保にした賁E調達コスト。急騰は「担保Eあるが現金がなぁE状態を示します、E,
    
    # Banking Sector
    "Bank_Cash": "【銀行E現金保有】\n全米の銀行が保有する現金賁Eの推移。準備預が十刁Eも、E行が不安を感じて現金を抱え込み始めると市場の流動性が低下します。『銀行E警戒忁Eを測る指標です、E,
    "Lending_Standards": "【貸出基準E厳格化】\n銀行が企業に融賁Eる際の態度の厳しさ。数値が上EEEラスEすると、E行が審査を厳しくしてぁE『信用収縮』を意味し、実体経済E冷え込みを予測する先行指標になります、E,
    "US_M2_Liquidity": "【通貨供給釁EM2】\n世E中に流EしてぁEマネーE現金E預等）E総量、ERBの賁E削減！ETEが進んでぁEも、このM2が維持されてぁEば民間部門の購買力E維持されてぁEと判断できます、E,
    "Banking_Trends": "【長期トレンドE見方】\n3本のラインが同時に動くか、バラバラに動くかが重要です。例えば『M2は横ばぁEのに、E行E現金だけ急増＋貸出基準が厳しくなる』とぁE絁E合わせE、『銀行がリスクを取らなくなってぁEE信用収縮の予EE』を示します、E,

    # Macro & Rates
    "Real_Yield": "【実質金利】\n(名目金利 - 期征Eンフレ玁E、Enこれが高いと、E利のつかなぁEEEEold, BTCEやハイチE株には重石となります、E,
    "Breakeven": "【期征Eンフレ玁E(BEI)】\n市場が予想する封Eのインフレ玁EEnこれが上がるとFRBは利下げしにくくなります、E,
    "Credit_Spread": "【クレジチEスプレチE】\n「ジャンク債」と「安Eな国債」E利回り差、En不況が近づくと企業倒産リスクで拡大します、E,
    "VIX": "【VIX持E】\n投賁Eの恐怖忁EEn20を趁Eると警戒、E0を趁EるとパニチE相場です、E,
    "Yield_10Y": "【米10年債利回り】\n世界のおのコスト、Enこれが上がると住宁EーンめE業借Eコストが上がり、景気を冷めEます、E,

    # Global
    "M2_Real": "【実質マネーサプライ】\nおの釁EM2)を物価(CPI)で割ったもの、En「実質皁E購買力」を示します。これが伸びてぁE国の株は上がりやすいです、E,
    "M2_Nominal": "【名目マネーサプライ】\n市場に流EしてぁE現金E総量、En中央銀行がどれだけお金を刷ったかの目安、E,
    "FX": "【為替レート】\nドル冁Eドル允Eど、En自国通貨安E輸出に有利ですが、輸入インフレを招きます、E,

    # Econ
    "Initial_Claims": "【新規失業保険申請件数】\n「E週、何人がクビになったか」、En最も早く景気悪化を察知できる雁E持Eです、E,
    "Unemployment": "【失業玁E\n労働力人口に対する失業老EE割合、En景気後退の決定的な証拠となります、E,
    "Housing": "【住宁E工件数】\n家がどれだけ建ち始めたか、En住宁EE家具家電への波及効果が大きいため、景気E先行指標です、E,
    "Mortgage": "、E0年住宁Eーン金利】\n米国の一般皁E住宁Eーン金利、En7%を趁Eると住宁E場が凍りつきます、E,
    "CPI": "【CPI (消費老E価持E)】\nインフレ玁EEnFRBが一番気にしてぁE数字です、E,

    # Crypto
    "ETH_BTC": "【ETH/BTC レシオ】\nビットコインに対してイーサリアムが強ぁE、En上がると「アルトコイン相場EリスクオンE」、下がると「BTC独歩高（質への送EE」、E,
    "Asset": "【賁E価格】\nゴールドE安E賁E、ビチEコインはチEタルゴールドとしての性質を持ちます、E
}

# --- 2. チEEタ取征E(Robust) ---
@st.cache_data(ttl=3600)
def get_market_data():
    # API Key setup
    os.environ["FRED_API_KEY"] = "4e9f89c09658e42a4362d1251d9a3d05"
    
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=730)
    
    # 1. FRED Data
    fred_series = []
    # Fallback mappings for critical IDs
    fallbacks = {
        'Total_Loans': 'WLCFLL',
        'SOMA_Bills': 'WSHOBL'
    }
    for name, ticker in FRED_INDICATORS.items():
        try:
            s = web.DataReader(ticker, 'fred', start, end)
            if s.empty and name in fallbacks:
                 s = web.DataReader(fallbacks[name], 'fred', start, end)
            s.columns = [name]
            fred_series.append(s)
        except:
            # Try fallback on error too
            if name in fallbacks:
                try:
                    s = web.DataReader(fallbacks[name], 'fred', start, end)
                    s.columns = [name]
                    fred_series.append(s)
                except:
                    pass
    
    # 2. Yahoo Data
    try:
        y_tickers = list(YAHOO_INDICATORS.values())
        y_data = yf.download(y_tickers, start=start, progress=False)['Close']
        if isinstance(y_data, pd.Series):
            y_data = y_data.to_frame()
        # Rename columns back to our keys
        inv_yahoo = {v: k for k, v in YAHOO_INDICATORS.items()}
        y_data = y_data.rename(columns=inv_yahoo)
    except:
        y_data = pd.DataFrame()

    # Join All
    df = pd.concat(fred_series + ([y_data] if not y_data.empty else []), axis=1).sort_index()

    # --- Unit Normalization (Million to Billion) as per PROJECT_RULES.md ---
    mil_to_bil = ['Fed_Assets', 'TGA', 'Reserves', 'SOMA_Total', 'SOMA_Bills', 'Primary_Credit', 'Total_Loans', 'SRF', 'FIMA', 'Bank_Cash']
    for col in mil_to_bil:
        if col in df.columns:
            df[col] = df[col] / 1000

    # Derived Metrics (Surgical Calculation)
    # Note: We do NOT ffill here to ensure show_metric can identify the actual update date.
    if all(k in df.columns for k in ['Fed_Assets', 'TGA', 'ON_RRP']):
        df['Net_Liquidity'] = df['Fed_Assets'] - df['TGA'] - df['ON_RRP']

    if 'US_TNX' in df.columns and 'Breakeven_10Y' in df.columns:
        df['Real_Yield'] = df['US_TNX'] - df['Breakeven_10Y']

    # Ratio calculation (independent of Reserves)
    if all(k in df.columns for k in ['SOMA_Bills', 'SOMA_Total']):
        df['SomaBillsRatio'] = (df['SOMA_Bills'] / df['SOMA_Total']) * 100

    # RMP (Reserve Management Purchases) Logic - Enhanced
    if all(k in df.columns for k in ['SomaBillsRatio', 'Reserves', 'SOMA_Bills']):
        # Trends for Alert (Last 4 weekly points approx)
        res_valid = df.get('Reserves', pd.Series()).dropna()
        ratio_valid = df.get('SomaBillsRatio', pd.Series()).dropna()
        bills_valid = df.get('SOMA_Bills', pd.Series()).dropna()
        
        if len(res_valid) >= 5 and len(ratio_valid) >= 3:
            # 1. Reserves down (Current < avg of previous 3)
            res_down = res_valid.iloc[-1] < res_valid.iloc[-4:-1].mean()
            # 2. Ratio up (2 weeks) OR Bills up
            ratio_up_2w = ratio_valid.iloc[-1] > ratio_valid.iloc[-2] > ratio_valid.iloc[-3]
            bills_up = len(bills_valid) >= 2 and bills_valid.iloc[-1] > bills_valid.iloc[-2]
            
            df['RMP_Alert_Active'] = res_down and (ratio_up_2w or bills_up)
            # Use a single value for the status text
            status_val = "隠れ緩和！EMPEE允Eを検知EFRBが短期国債の比率を高め、市場への流動性供給を準備してぁE可能性があります、E if df['RMP_Alert_Active'].iloc[-1] else "現在、Eれ緩和！EMPEE明確な允EE検知されてぁEせんE準備預および短期国債比率は安定）、E
            df['RMP_Status_Text'] = status_val
    
    # Real M2 Indices
    m2_pairs = [('US', 'US_M2', 'US_CPI'), ('CN', 'CN_M2', 'CN_CPI'), 
                ('EU', 'EU_M2', 'EU_CPI'), ('JP', 'JP_M2', 'JP_CPI')]
    for code, m2, cpi in m2_pairs:
        if m2 in df.columns and cpi in df.columns:
            # ffill cpi as it's monthly
            df[f'{code}_Real_M2_Index'] = (df[m2] / df[cpi].ffill()) * 100

    if 'Ethereum' in df.columns and 'Bitcoin' in df.columns:
        df['ETH_BTC_Ratio'] = df['Ethereum'] / df['Bitcoin']

    return df

def show_metric(label, series, unit="", help_key=None, alert_func=None, notes=None):
    if series is None:
        st.metric(label, "N/A", help=EXPLANATIONS.get(help_key, ""))
        if notes: st.caption(notes)
        return

    # Extract Value and Date
    if isinstance(series, (int, float)):
        val = series
        date_str = "Calc"
    else:
        # We use dropna() to find the LAST ACTUAL DATA POINT date.
        # This prevents "today's date" from showing up for monthly data.
        valid = series.dropna()
        if valid.empty:
            st.metric(label, "N/A", help=EXPLANATIONS.get(help_key, ""))
            if notes: st.caption(notes)
            return
        val = valid.iloc[-1]
        date = valid.index[-1]
        # Check if date is a datetime object to prevent crash with integer indices
        date_str = date.strftime("%m/%d") if hasattr(date, "strftime") else "N/A"
    
    # Format
    val_str = f"{val:,.2f}"
    if unit == "B":
        val_str = f"{val:,.1f} B"
    elif unit == "%": val_str = f"{val:,.2f} %"
    elif unit == "$": val_str = f"${val:,.2f}"
    elif unit == "pt": val_str = f"{val:,.2f}"
    elif unit in ["JPY", "CNY"]: val_str = f"¥{val:,.2f}"
    
    display_label = label
    if alert_func and alert_func(val):
        display_label = "⚠EE" + label

    st.metric(
        label=display_label, 
        value=val_str, 
        delta=f"📅 {date_str}", 
        delta_color="off", 
        help=EXPLANATIONS.get(help_key, "")
    )
    if notes: st.caption(notes)

def  plot_dual_axis(df, col1, col2, name1, name2, title=None):
    if col1 not in df.columns or col2 not in df.columns:
        st.warning(f"Chart data missing for {name1} or {name2}")
        return
        
    # Check if data is all NaN
    if df.get(col1, pd.Series()).isna().all() or df.get(col2, pd.Series()).isna().all():
        return

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df.index, y=df[col1], name=name1, line=dict(color='#00CC96', width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df.index, y=df[col2], name=name2, line=dict(color='#EF553B', width=2)), secondary_y=True)
    
    fig.update_layout(
        title=title if title else f"{name1} vs {name2}",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor='center')
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_soma_composition(df):
    if 'SOMA_Total' not in df.columns or 'SomaBillsRatio' not in df.columns:
        return
        
    # Resample to Weekly to clean up the chart (Many FRB data are weekly)
    d_plot = df[['SOMA_Total', 'SomaBillsRatio']].resample('W-WED').last().dropna()
    if d_plot.empty: d_plot = df[['SOMA_Total', 'SomaBillsRatio']].dropna()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Trace 1: SOMA Total (Bar)
    fig.add_trace(
        go.Bar(x=d_plot.index, y=d_plot['SOMA_Total'], name="SOMA Total (L)", marker_color='#636EFA', opacity=0.5),
        secondary_y=False,
    )
    
    # Trace 2: SomaBillsRatio (Line)
    fig.add_trace(
        go.Scatter(x=d_plot.index, y=d_plot['SomaBillsRatio'], name="Bills Ratio (R)", 
                   line=dict(color='#00CC96', width=4, shape='hv')), # hv for stepped look to emphasize weekly changes
        secondary_y=True,
    )
    
    fig.update_layout(
        title="FRB賁E構E (SOMA Total vs Bills比率)",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor='center'),
        hovermode="x unified"
    )
    
    fig.update_yaxes(title_text="Total (Billion $)", secondary_y=False)
    
    # Safety for range - ensure 1% changes are visible
    max_ratio = d_plot['SomaBillsRatio'].max()
    min_ratio = d_plot['SomaBillsRatio'].min()
    padding = (max_ratio - min_ratio) * 0.2 if max_ratio > min_ratio else 1.0
    y2_min = max(0, min_ratio - padding)
    y2_max = max_ratio + padding
    
    fig.update_yaxes(title_text="Bills Ratio (%)", secondary_y=True, range=[y2_min, y2_max], tickformat=".1f")
    
    st.plotly_chart(fig, use_container_width=True)

def fetch_rss_news():
    items = []
    try:
        feed = feedparser.parse("https://www.federalreserve.gov/feeds/press_all.xml")
        for e in feed.entries[:5]:
            items.append({"title": e.title, "link": e.link, "date": e.get('published', '')[:16]})
    except: pass
    return items

# --- 4. Main App ---
st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon="🚁", initial_sidebar_state="expanded")
st.title(f"🚁 {PAGE_TITLE}")
st.markdown("Global Macro, Liquidity & Crypto Intelligence Terminal")

df = get_market_data()

with st.sidebar:
    st.header("⚙︁EControl")
    if st.button("🔄 Force Update"):
        get_market_data.clear()
        st.rerun()
    
    # Data Health check
    if not df.empty:
        missing = [k for k in FRED_INDICATORS.keys() if k not in df.columns]
        if missing:
            with st.expander("🛠EEData Health"):
                st.caption(f"Waiting for/Missing: {', '.join(missing)}")
    
    st.markdown("---")
    try:
        csv = df.to_csv().encode('utf-8')
        st.download_button("📥 Download CSV", csv, "market_data.csv", "text/csv")
    except: pass

if df.empty:
    st.error("Severe Error: Could not fetch any market data.")
    st.stop()

# Tabs
tabs = st.tabs(["📊 Liquidity & Rates", "🌏 Global Money & FX", "EE US Economy", "🪁ECrypto & Assets", "📰 News"])

# Tab 1: Liquidity
with tabs[0]:
    st.subheader("🏦 Liquidity & The Fed")
    c1, c2, c3, c4 = st.columns(4)
    with c1: show_metric("Net Liquidity", df.get('Net_Liquidity'), "B", "Net_Liquidity", notes="市場の真E燁E")
    with c2: show_metric("ON RRP", df.get('ON_RRP'), "B", "ON_RRP", notes="余剰賁E (MMF)", alert_func=lambda x: x<200)
    with c3: show_metric("Reserves", df.get('Reserves'), "B", "Reserves", notes="銀行準備預")
    with c4: show_metric("TGA", df.get('TGA'), "B", "TGA", notes="政府口座")

    st.markdown("##### 🔗 Net Liquidity vs S&P 500")
    plot_dual_axis(df.assign(Net_Liquidity=df.get('Net_Liquidity', pd.Series()).ffill()), 'Net_Liquidity', 'SP500', 'Net Liquidity (L)', 'S&P 500 (R)')
    
    # Expandable Trend Charts (individual metrics only)
    with st.expander("📈 View Individual Trends (過去2年閁E", expanded=True):
        if 'Reserves' in df.columns and not df.get('Reserves', pd.Series()).isna().all():
            st.markdown("###### Reserves (Billions)")
            reserve_data = df[['Reserves']].dropna()
            if len(reserve_data) > 0:
                st.line_chart(reserve_data)
            else:
                st.info("No Reserves data available")
        
        if 'TGA' in df.columns and not df.get('TGA', pd.Series()).isna().all():
            st.markdown("###### TGA (Billions)")
            tga_data = df[['TGA']].dropna()
            if len(tga_data) > 0:
                st.line_chart(tga_data)
            else:
                st.info("No TGA data available")
        
        if 'ON_RRP' in df.columns and not df.get('ON_RRP', pd.Series()).isna().all():
            st.markdown("###### ON RRP (Billions)")
            rrp_data = df[['ON_RRP']].dropna()
            if len(rrp_data) > 0:
                st.line_chart(rrp_data)
            else:
                st.info("No ON RRP data available")
    
    st.markdown("---")
    st.subheader("🔧 Market Plumbing (Repo & Liquidity)")
    c1, c2, c3, c4 = st.columns(4)
    with c1: show_metric("Standing Repo (SRF)", df.get('SRF'), "B", "SRF", notes="国冁Eポ市場")
    with c2: show_metric("FIMA Repo", df.get('FIMA'), "B", "FIMA", notes="海外ドル流動性")
    with c3: show_metric("SOFR", df.get('SOFR'), "%", "SOFR", alert_func=lambda x: x>5.5, notes="拁E付翌日物金利")
    with c4: 
        diff = None
        if 'EFFR' in df.columns and 'IORB' in df.columns:
            diff = df['EFFR'] - df['IORB']
        show_metric("EFFR - IORB", diff, "%", "EFFR_IORB", notes="連銀準備金状況E, alert_func=lambda x: x>0.05)

    # Expandable Trend Charts (split by unit)
    with st.expander("📈 View Individual Trends (過去2年閁E", expanded=True):
        st.markdown("###### Repo Facilities (Billions)")
        repo_cols = ['SRF', 'FIMA']
        valid_repo = [c for c in repo_cols if c in df.columns and not df.get(c, pd.Series()).isna().all()]
        if valid_repo:
            st.line_chart(df[valid_repo])
        else:
            st.info("Loading repo data...")
        
        st.markdown("###### Interest Rates (%)")
        rate_cols = ['SOFR', 'EFFR', 'IORB']
        valid_rates = [c for c in rate_cols if c in df.columns and not df.get(c, pd.Series()).isna().all()]
        if valid_rates:
            st.line_chart(df[valid_rates])
        else:
            st.info("Loading rate data...")

    st.markdown("---")
    st.subheader("🚨 Emergency Loans (Discount Window)")
    c1, c2 = st.columns(2)
    with c1: show_metric("Total Loans", df.get('Total_Loans'), "B", "Window", notes="緊急貸出総顁E)
    with c2: show_metric("Primary Credit", df.get('Primary_Credit'), "B", "Primary", notes="健全行向け窓口貸出", alert_func=lambda x: x>1) 

    # Expandable Trend Charts
    with st.expander("📈 View Individual Trends (過去2年閁E", expanded=True):
        loan_cols = ['Total_Loans', 'Primary_Credit']
        valid_loans = [c for c in loan_cols if c in df.columns and not df.get(c, pd.Series()).isna().all()]
        if valid_loans:
            st.line_chart(df[valid_loans])
        else:
            st.info("Loading loan data...")

    st.markdown("---")
    st.subheader("🏛EEFed Balance Sheet (SOMA)")
    
    # Persistent RMP Status Display
    # Ensure we only get the LAST string value, not the whole series
    rmp_status_series = df.get('RMP_Status_Text')
    rmp_status = rmp_status_series.iloc[-1] if hasattr(rmp_status_series, 'iloc') else "チEEタ収集中..."
    
    rmp_active_series = df.get('RMP_Alert_Active', pd.Series([False]))
    rmp_active = rmp_active_series.iloc[-1] if hasattr(rmp_active_series, 'iloc') else False
    
    if rmp_active:
        st.error(f"🚨 **RMP允EアラーチE*: {rmp_status}")
    else:
        st.success(f"ℹEE**RMP允EスチEEタス**: {rmp_status}")

    c1, c2, c3 = st.columns(3)
    with c1: show_metric("SOMA Total", df.get('SOMA_Total'), "B", "SOMA_Total", notes="保有賁E総顁E(QE/QT)")
    with c2: show_metric("RMP (短期国債)", df.get('SOMA_Bills'), "B", "RMP", notes="SOMA Bills保有髁E)
    with c3: show_metric("SOMA Bills Ratio", df.get('SomaBillsRatio'), "%", "SomaBillsRatio", notes="短期国債の構E比率")
    
    # New SOMA Composition Chart
    plot_soma_composition(df)
    
    # Expandable Individual Metric Trends
    with st.expander("📈 View Individual Metrics (過去2年閁E", expanded=True):
        soma_cols = ['SOMA_Total', 'SOMA_Bills', 'SomaBillsRatio']
        valid_soma = [c for c in soma_cols if c in df.columns and not df.get(c, pd.Series()).isna().all()]
        if valid_soma:
            st.line_chart(df[valid_soma])
        else:
            st.info("Loading SOMA data...")
    
    st.markdown("---")
    st.subheader("🏦 Private Banking Sector (FRB vs Market Gap)")
    st.caption("💡 FRBの政策と銀行E実際の行動のギャチEEを監要E, help=EXPLANATIONS.get("Banking_Trends", ""))
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: show_metric("Bank Cash Holdings", df.get('Bank_Cash'), "B", "Bank_Cash", notes="銀行E現金退蔵")
    with c2: show_metric("Lending Standards", df.get('Lending_Standards'), "%", "Lending_Standards", notes="信用収縮の先行指樁E)
    with c3: show_metric("M2 (Nominal)", df.get('US_M2'), "B", "US_M2_Liquidity", notes="名目通貨供給釁E)
    with c4: show_metric("M2 (Real)", df.get('US_Real_M2_Index'), "pt", "M2_Real", notes="実質購買力指数")
    
    # Long-term Trend Charts (Separated for clarity)
    st.markdown("##### 📈 Long-term Banking Sector Trends")
    
    # Chart 1: Bank Cash Holdings
    if 'Bank_Cash' in df.columns and not df.get('Bank_Cash', pd.Series()).isna().all():
        st.markdown("###### 💰 Bank Cash Holdings (Billions)")
        st.line_chart(df[['Bank_Cash']].dropna())
    
    # Chart 2: Lending Standards
    if 'Lending_Standards' in df.columns and not df.get('Lending_Standards', pd.Series()).isna().all():
        st.markdown("###### 📊 Lending Standards (% Net Tightening)")
        st.line_chart(df[['Lending_Standards']].dropna())
    
    # Chart 3: M2 Nominal
    if 'US_M2' in df.columns and not df.get('US_M2', pd.Series()).isna().all():
        st.markdown("###### 💵 Money Supply - Nominal M2 (Billions)")
        st.line_chart(df[['US_M2']].dropna())
    
    # Chart 4: M2 Real (Indexed)
    if 'US_Real_M2_Index' in df.columns and not df.get('US_Real_M2_Index', pd.Series()).isna().all():
        st.markdown("###### 💵 Money Supply - Real M2 Index (Inflation-Adjusted)")
        # Show as indexed for comparability
        m2_real_series = df['US_Real_M2_Index'].dropna()
        if len(m2_real_series) > 0:
            first_val = m2_real_series.iloc[0]
            if first_val != 0:
                indexed = (df[['US_Real_M2_Index']] / first_val) * 100
                st.line_chart(indexed.dropna())
    
    st.markdown("---")
    st.subheader("⚠EERisk & Bonds")
    c1, c2, c3, c4 = st.columns(4)
    with c1: show_metric("VIX Index", df.get('VIX'), "pt", "VIX", alert_func=lambda x: x>20, notes="恐怖指数")
    with c2: show_metric("Credit Spread", df.get('Credit_Spread'), "%", "Credit_Spread", alert_func=lambda x: x>5.0, notes="ジャンク債スプレチE")
    with c3: show_metric("US 10Y Yield", df.get('US_TNX'), "%", "Yield_10Y", notes="長期利")
    with c4: show_metric("HYG", df.get('HYG'), "$", "Asset", notes="ジャンク債ETF")

    # Expandable Trend Charts (split by type)
    with st.expander("📈 View Individual Trends (過去2年閁E", expanded=True):
        st.markdown("###### Market Risk Indicators")
        risk_cols = ['VIX', 'Credit_Spread']
        valid_risk = [c for c in risk_cols if c in df.columns and not df.get(c, pd.Series()).isna().all()]
        if valid_risk:
            st.line_chart(df[valid_risk])
        else:
            st.info("Loading risk data...")
        
        st.markdown("###### Yield & Bond ETF")
        bond_cols = ['US_TNX', 'HYG']
        valid_bonds = [c for c in bond_cols if c in df.columns and not df.get(c, pd.Series()).isna().all()]
        if valid_bonds:
            st.line_chart(df[valid_bonds])
        else:
            st.info("Loading bond data...")

# Tab 2: Global
with tabs[1]:
    st.subheader("🌏 Global Real Money (Purchasing Power)")
    # Real M2
    c1, c2, c3, c4 = st.columns(4)
    with c1: show_metric("EE US Real M2", df.get('US_Real_M2_Index'), "pt", help_key="M2_Real")
    with c2: show_metric("EE CN Real M2", df.get('CN_Real_M2_Index'), "pt", help_key="M2_Real")
    with c3: show_metric("EE EU Real M2", df.get('EU_Real_M2_Index'), "pt", help_key="M2_Real")
    with c4: show_metric("EE JP Real M2", df.get('JP_Real_M2_Index'), "pt", help_key="M2_Real")
    
    # Nominal M2 (New Row)
    st.caption("名目マネーサプライ (Nominal M2)")
    c1, c2, c3, c4 = st.columns(4)
    with c1: show_metric("US M2 (Nominal)", df.get('US_M2'), "B", "M2_Nominal")
    with c2: show_metric("CN M2 (Nominal)", df.get('CN_M2'), "CNY", "M2_Nominal", notes="中国允E)
    with c3: show_metric("EU M2 (Nominal)", df.get('EU_M2'), "B", "M2_Nominal", notes="ユーロ")
    with c4: show_metric("JP M2 (Nominal)", df.get('JP_M2'), "JPY", "M2_Nominal", notes="日本冁E)

    st.markdown("##### 📈 Global Real Liquidity Trends")
    m2_cols = ['US_Real_M2_Index', 'CN_Real_M2_Index', 'EU_Real_M2_Index', 'JP_Real_M2_Index']
    valid_m2 = [c for c in m2_cols if c in df.columns and not df[c].isna().all()]
    if valid_m2:
        st.line_chart(df[valid_m2].dropna())
    else:
        st.info("No Global M2 data available.")

    st.markdown("---")
    st.subheader("💱 FX & Commodities")
    c1, c2, c3, c4 = st.columns(4)
    with c1: show_metric("USD/JPY", df.get('USDJPY'), "JPY", notes="ドル冁E)
    with c2: show_metric("USD/CNY", df.get('USDCNY'), "CNY", notes="人民E")
    with c3: show_metric("WTI Crude", df.get('WTI'), "$", notes="原油")
    with c4: show_metric("DXY", df.get('DXY'), "pt", notes="ドル持E")

# Tab 3: US Econ
with tabs[2]:
    st.subheader("EE US Economic Health")
    c1, c2, c3 = st.columns(3)
    with c1: show_metric("Unemployment", df.get('Unemployment'), "%")
    with c2: show_metric("Non-Farm Payrolls", df.get('NonFarm_Payroll'), "pt")
    with c3: show_metric("Initial Claims", df.get('Initial_Claims'), "", "Initial_Claims", alert_func=lambda x: x>300000, notes="リセチEョン先行指樁E)
    
    st.subheader("Inflation & Housing")
    c1, c2, c3 = st.columns(3)
    with c1: show_metric("CPI (YoY)", df.get('CPI'), "pt")
    with c2: show_metric("Housing Starts", df.get('Housing_Starts'), "pt", "Housing")
    with c3: show_metric("30Y Mortgage", df.get('Mortgage_30Y'), "%")
    
    plot_dual_axis(df, 'Mortgage_30Y', 'Housing_Starts', 'Mortgage Rate (L)', 'Housing Starts (R)')

# Tab 4: Crypto
with tabs[3]:
    st.subheader("🪁ECrypto & Assets")
    c1, c2, c3, c4 = st.columns(4)
    with c1: show_metric("Bitcoin", df.get('Bitcoin'), "$")
    with c2: show_metric("Ethereum", df.get('Ethereum'), "$")
    with c3: show_metric("Silver", df.get('Silver'), "$", notes="銀")
    with c4: show_metric("Gold", df.get('Gold'), "$", notes="釁E)
    
    st.caption("Ratios")
    c1, c2 = st.columns(2)
    with c1: show_metric("ETH/BTC Ratio", df.get('ETH_BTC_Ratio'), "", "ETH_BTC", notes="Risk On/Off")
    
    st.markdown("##### 🔗 Net Liquidity vs Bitcoin")
    plot_dual_axis(df.assign(Net_Liquidity=df.get('Net_Liquidity', pd.Series()).ffill()), 'Net_Liquidity', 'Bitcoin', 'Net Liquidity (L)', 'Bitcoin (R)')

# Tab 5: News
with tabs[4]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📰 Headlines")
        news = fetch_rss_news()
        for n in news:
            st.markdown(f"- [{n['title']}]({n['link']}) ({n['date']})")
    with c2:
        st.subheader("📅 Calendar")
        st.info("TradingView Widget Area")
