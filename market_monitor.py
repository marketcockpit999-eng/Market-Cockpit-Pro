import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
import datetime
import warnings
import os

# ==========================================
# 0. 基本設定 & APIキー
# ==========================================
warnings.simplefilter('ignore')

# ★画像で確認したAPIキーをセット済みです
FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"
os.environ["FRED_API_KEY"] = FRED_API_KEY

LOG_FILE = "market_monitor_log.csv"

# 期間設定
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=500)

print(f"起動中... (基準日: {end_date.strftime('%Y-%m-%d')})")
print("データ収集中... (解説・日付・実質値を計算中)")

# ==========================================
# 1. FRED データ取得設定
# ==========================================
fred_tickers = {
    # --- A. 流動性・配管 ---
    'ON_RRP': 'RRPONTSYD',         # ON RRP
    'Reserves': 'WRESBAL',         # 準備預金
    'TGA': 'WTREGEN',              # TGA
    'Fed_Assets': 'WALCL',         # Fed資産合計 (ネット流動性計算用)
    
    # SOMA詳細
    'SOMA_Total': 'WSHOSHO',       # SOMA保有総額
    'SOMA_Bills': 'WSHOBL',        # SOMA短期国債 (隠れQE)
    
    # 緊急融資 & 銀行
    'Primary_Credit': 'WLCFLPCL',  # 窓口貸出 (Discount Window)
    'Total_Loans': 'WLCFLL',       # 連銀貸出総額
    'BTFP': 'H41RESPALGTRRBW',     # BTFP残高
    
    # 金利
    'EFFR': 'EFFR',
    'IORB': 'IORB',
    
    # --- B. 債券・クレジット ---
    'Credit_Spread': 'BAMLH0A0HYM2', 
    'Breakeven_10Y': 'T10YIE',       # 期待インフレ率
    
    # --- D. グローバルマネー (名目 & 実質計算用) ---
    'US_M2': 'M2SL',               # 米国M2 (名目)
    'US_CPI': 'CPIAUCSL',          # 米国CPI (実質計算用)
    
    'China_M2': 'MYAGM2CNM189N',
    'China_CPI': 'CHNCPIALLMINMEI', # 中国CPI
    
    'Euro_M2': 'MANMM101EZM189S',
    'Euro_CPI': 'CP0000EZ19M086NEST', # 欧州CPI
    
    'Japan_M2': 'MANMM101JPM189S',
    'Japan_CPI': 'JPNCPIALLMINMEI'    # 日本CPI
}

fred_data = {}

for key, ticker in fred_tickers.items():
    try:
        df = web.DataReader(ticker, 'fred', start_date, end_date)
        valid_data = df.dropna()
        if not valid_data.empty:
            val = valid_data.iloc[-1].iloc[0]
            date = valid_data.index[-1]
            
            # 単位調整 (Million -> Billion)
            # 金利(%)や指数(CPI)以外はBillion単位に
            if "CPI" not in key and key not in ['EFFR', 'IORB', 'Credit_Spread', 'Breakeven_10Y']:
                if val > 1000: val /= 1000
            
            fred_data[key] = {'val': val, 'date': date}
    except Exception:
        pass

# ==========================================
# 2. Yahoo Finance データ取得設定
# ==========================================
yahoo_tickers = {
    'HYG': 'HYG', 'US10Y': '^TNX', 
    'WTI': 'CL=F', 'Gold': 'GC=F', 'Silver': 'SI=F', 
    'Bitcoin': 'BTC-USD', 'DXY': 'DX-Y.NYB',
    'VIX': '^VIX',
    'USDJPY': 'JPY=X',
    'USDCNY': 'CNY=X' # ★中国為替復活
}

yahoo_data = {}

try:
    yf_df = yf.download(list(yahoo_tickers.values()), start=start_date, progress=False)['Close']
    if isinstance(yf_df.columns, pd.MultiIndex):
        yf_df.columns = yf_df.columns.get_level_values(0)
    for key, ticker in yahoo_tickers.items():
        if ticker in yf_df.columns:
            valid_d = yf_df[ticker].dropna()
            if not valid_d.empty:
                yahoo_data[key] = {'val': valid_d.iloc[-1], 'date': valid_d.index[-1]}
except Exception:
    pass

# ==========================================
# 3. 計算ロジック (Derived Metrics)
# ==========================================
# (1) ネット流動性
net_liquidity = None
if all(k in fred_data for k in ['Fed_Assets', 'TGA', 'ON_RRP']):
    net_liquidity = fred_data['Fed_Assets']['val'] - fred_data['TGA']['val'] - fred_data['ON_RRP']['val']

# (2) 実質金利
real_yield = None
if 'US10Y' in yahoo_data and 'Breakeven_10Y' in fred_data:
    real_yield = yahoo_data['US10Y']['val'] - fred_data['Breakeven_10Y']['val']

# (3) 実質M2の簡易計算 (名目 / CPI * 100)
# ※CPIの更新は遅いため、最新M2と最新CPIの日付がズレることがありますが、直近値で計算します
def calc_real_m2(m2_key, cpi_key):
    if m2_key in fred_data and cpi_key in fred_data:
        nominal = fred_data[m2_key]['val']
        cpi = fred_data[cpi_key]['val']
        # 基準年をまたぐため厳密ではありませんが、トレンド把握用の簡易実質値
        return (nominal / cpi) * 100 
    return None

real_m2_us = calc_real_m2('US_M2', 'US_CPI')
real_m2_cn = calc_real_m2('China_M2', 'China_CPI')
real_m2_eu = calc_real_m2('Euro_M2', 'Euro_CPI')
real_m2_jp = calc_real_m2('Japan_M2', 'Japan_CPI')

# ==========================================
# 4. データ保存 (CSV)
# ==========================================
today_record = {'Date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
for d in [fred_data, yahoo_data]:
    for k, v in d.items():
        today_record[k] = v['val']
if net_liquidity: today_record['Net_Liquidity'] = net_liquidity

try:
    new_row = pd.DataFrame([today_record])
    if os.path.exists(LOG_FILE):
        pd.concat([pd.read_csv(LOG_FILE), new_row], ignore_index=True).to_csv(LOG_FILE, index=False)
    else:
        new_row.to_csv(LOG_FILE, index=False)
    save_status = "✅ データベース保存成功"
except Exception:
    save_status = "⚠️ 保存失敗"

# ==========================================
# 5. 表示フォーマット関数 (日付つき)
# ==========================================
def fmt(val_obj, unit, warning_func=None):
    if not val_obj: return "N/A"
    
    # 辞書型(fred/yahoo)か、単なる数値(計算値)かで分岐
    if isinstance(val_obj, dict):
        val = val_obj['val']
        date_str = val_obj['date'].strftime('%Y-%m-%d')
    else:
        val = val_obj
        date_str = "Calc"

    val_str = ""
    if unit == "$": val_str = f"{val:,.2f} $"
    elif unit == "B": val_str = f"{val:,.2f} Billion $"
    elif unit == "%": val_str = f"{val:,.2f} %"
    elif unit == "pt": val_str = f"{val:,.2f} Point"
    else: val_str = f"{val:,.2f} {unit}"
    
    # 警告判定
    alert = ""
    if warning_func and warning_func(val):
        alert = " ⚠️[ALERT]"
        
    return f"{val_str:<18} (日付: {date_str}){alert}"

# 単純な数値用フォーマッタ
def fmt_calc(val, unit):
    if val is None: return "N/A"
    return f"{val:,.2f} {unit}"

# ==========================================
# 6. メイン表示 (Final Output)
# ==========================================
print("\n" + "="*80)
print(f"市場監視コックピット v4.0 (Full Spec) - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("="*80)

print("\n【S. スペシャル指標 (Advanced)】")
print(f"★ Net Liquidity (ネット流動性) : {fmt_calc(net_liquidity, 'Billion $')} (市場の真の燃料)")
print(f"★ Real Yield    (実質金利)     : {fmt_calc(real_yield, '%')} (プラス圏は株に重石)")
print(f"★ VIX Index     (恐怖指数)     : {fmt(yahoo_data.get('VIX'), 'pt', lambda x: x>20)}")

print("\n【A. 流動性・配管 (The Plumbing)】")
print(f"1. ON RRP (MMF/政府の余剰資金) : {fmt(fred_data.get('ON_RRP'), 'B', lambda x: x<200)}")
print(f"2. Reserves (銀行の余剰資金)   : {fmt(fred_data.get('Reserves'), 'B', lambda x: x<3000)}")
print(f"3. TGA (政府口座/資金吸収)     : {fmt(fred_data.get('TGA'), 'B')}")

print(f"4. SOMA Holdings (隠れ量的緩和の監視)")
print(f"   → [Total] 保有総額          : {fmt(fred_data.get('SOMA_Total'), 'B')}")
print(f"   → [RMP]   短期国債(Bills)   : {fmt(fred_data.get('SOMA_Bills'), 'B')} ★重要")

print(f"5. SRF & Loans (緊急貸出枠/Discount Window)")
print(f"   → [Window] 窓口貸出(Primary): {fmt(fred_data.get('Primary_Credit'), 'B', lambda x: x>5.0)} ★Check")
print(f"   → [Loans]  貸出残高(Total)  : {fmt(fred_data.get('Total_Loans'), 'B')}")
print(f"   → [BTFP]   救済P残高        : {fmt(fred_data.get('BTFP'), 'B')} (残存)")

print(f"6. EFFR vs IORB (金利発作)     : ", end="")
if 'EFFR' in fred_data and 'IORB' in fred_data:
    diff = fred_data['EFFR']['val'] - fred_data['IORB']['val']
    print(f"乖離 {diff:.2f}% (EFFR: {fred_data['EFFR']['val']}%) [正常]" if diff <= 0.05 else f"⚠️乖離 {diff:.2f}%")
else: print("N/A")

print("\n【B. 債券・クレジット (The Cracks)】")
print(f"7. HYG (Junk Bond ETF)         : {fmt(yahoo_data.get('HYG'), '$')}")
print(f"8. US 10Y Yield                : {fmt(yahoo_data.get('US10Y'), '%')}")
print(f"9. Credit Spread (OAS)         : {fmt(fred_data.get('Credit_Spread'), '%', lambda x: x>5.0)}")

print("\n【C. 実物資産・先行指標 (The Canary)】")
print(f"10. WTI Crude Oil              : {fmt(yahoo_data.get('WTI'), '$')}")
print(f"11. Gold                       : {fmt(yahoo_data.get('Gold'), '$')}")
print(f"12. Bitcoin                    : {fmt(yahoo_data.get('Bitcoin'), '$')}")
print(f"13. DXY (Dollar Index)         : {fmt(yahoo_data.get('DXY'), 'pt')}")

print("\n【D. グローバル・マネー (The Ocean)】")
print(f"14. US M2 (米)  [名目]         : {fmt(fred_data.get('US_M2'), 'B')}")
print(f"                [実質Index]    : {fmt_calc(real_m2_us, '')} (CPI調整後)")
print(f"15. China M2    [名目]         : {fmt(fred_data.get('China_M2'), 'CNY')}")
print(f"                [実質Index]    : {fmt_calc(real_m2_cn, '')}")
print(f"16. Euro M2     [名目]         : {fmt(fred_data.get('Euro_M2'), 'EUR')}")
print(f"                [実質Index]    : {fmt_calc(real_m2_eu, '')}")
print(f"17. Japan M2    [名目]         : {fmt(fred_data.get('Japan_M2'), 'JPY')}")
print(f"                [実質Index]    : {fmt_calc(real_m2_jp, '')}")

print("\n【E. アジアの為替 (Asian FX)】")
print(f"18. USD/JPY (円)               : {fmt(yahoo_data.get('USDJPY'), 'JPY')}")
print(f"19. USD/CNY (元)               : {fmt(yahoo_data.get('USDCNY'), 'CNY')} ★復活")

print("\n" + "-"*80)
print(f"{save_status} -> '{LOG_FILE}'")
print("="*80)