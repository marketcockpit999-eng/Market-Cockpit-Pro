import streamlit as st
import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
import datetime
import requests
import re
import os
import pickle
import time
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import StringIO
from .constants import (
    FRED_API_KEY, FRED_INDICATORS, YAHOO_INDICATORS, 
    FRED_UNITS, VALIDATION_RANGES, DATA_FRESHNESS_RULES, 
    MANUAL_DATA_FILE
)
from .config import MANUAL_GLOBAL_M2

# Disk cache settings
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.market_data_cache.pkl')
CACHE_TTL_SECONDS = 600  # 10 minutes

# ========== PARALLEL FETCHING HELPERS ==========

def _fetch_single_fred(name: str, ticker: str, start, end) -> tuple:
    """Fetch single FRED indicator (for parallel execution)"""
    try:
        s = web.DataReader(ticker, 'fred', start, end, api_key=FRED_API_KEY)
        s.columns = [name]
        if name in FRED_UNITS:
            unit_info = FRED_UNITS[name]
            if unit_info.get('divisor'):
                s[name] = s[name] / unit_info['divisor']
        return (name, s, None)
    except Exception as e:
        return (name, None, str(e))

def _fetch_fred_parallel(indicators: dict, start, end, max_workers=15) -> list:
    """Fetch FRED indicators in parallel"""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_fetch_single_fred, name, ticker, start, end): name
            for name, ticker in indicators.items()
            if name != 'CN_Credit_Stock'  # Special handling separately
        }
        for future in as_completed(futures):
            name, data, error = future.result()
            if data is not None:
                results.append(data)
    return results

def _fetch_yahoo_data(tickers: dict, start, end) -> pd.DataFrame:
    """Fetch Yahoo Finance data (for parallel execution)"""
    try:
        y_tickers = list(tickers.values())
        y_data = yf.download(y_tickers, start=start, end=end, progress=False)['Close']
        inv_yahoo = {v: k for k, v in tickers.items()}
        return y_data.rename(columns=inv_yahoo)
    except:
        return pd.DataFrame()

def _load_from_disk_cache():
    """Load cached data from disk if fresh enough"""
    try:
        if os.path.exists(CACHE_FILE):
            cache_age = time.time() - os.path.getmtime(CACHE_FILE)
            if cache_age < CACHE_TTL_SECONDS:
                with open(CACHE_FILE, 'rb') as f:
                    data = pickle.load(f)
                    return data.get('df'), data.get('df_original')
    except Exception:
        pass
    return None, None

def _save_to_disk_cache(df, df_original):
    """Save data to disk cache"""
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump({'df': df, 'df_original': df_original, 'timestamp': time.time()}, f)
    except Exception:
        pass

@st.cache_data(ttl=3600, show_spinner=False)
def get_fred_release_dates(fred_ids: list) -> dict:
    """Fetch actual release dates from FRED API - Parallel Version"""
    release_dates = {}
    
    def fetch_single_release(series_id):
        try:
            url = f"https://api.stlouisfed.org/fred/series?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'seriess' in data and len(data['seriess']) > 0:
                    date_part = data['seriess'][0].get('last_updated', '').split(' ')[0]
                    return (series_id, date_part)
        except:
            pass
        return (series_id, None)
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(fetch_single_release, fred_ids))
        for series_id, date in results:
            if date:
                release_dates[series_id] = date
    
    return release_dates

def get_data_freshness_status(last_valid_dates: dict, release_dates: dict = None) -> dict:
    """
    Check data freshness for all 66 indicators defined in DATA_FRESHNESS_RULES.
    Only counts items explicitly defined in rules - ignores extra DataFrame columns.
    """
    from datetime import datetime
    today = datetime.now().date()
    results = {'fresh': [], 'stale': [], 'critical': [], 'missing': [], 'details': {}}
    
    # Build complete list of 66 defined indicators with their categories
    defined_indicators = {}  # indicator -> category
    for category, config in DATA_FRESHNESS_RULES.items():
        for ind in config['indicators']:
            defined_indicators[ind] = category
    
    # Iterate over DEFINED indicators only (not all DataFrame columns)
    for indicator, category in defined_indicators.items():
        rules = DATA_FRESHNESS_RULES[category]
        
        if indicator in last_valid_dates:
            try:
                date_str = last_valid_dates[indicator]
                check_date_str = release_dates.get(indicator, date_str) if release_dates else date_str
                last_date = datetime.strptime(check_date_str, '%Y-%m-%d').date()
                days_old = (today - last_date).days
                
                if days_old <= rules['fresh']: status = 'fresh'
                elif days_old <= rules['stale']: status = 'stale'
                else: status = 'critical'
                
                results[status].append(indicator)
                results['details'][indicator] = {'status': status, 'days_old': days_old, 'category': category}
            except:
                results['missing'].append(indicator)
                results['details'][indicator] = {'status': 'missing', 'category': category}
        else:
            # Indicator defined in rules but not in DataFrame
            results['missing'].append(indicator)
            results['details'][indicator] = {'status': 'missing', 'category': category}
    
    total = len(defined_indicators)  # Always 66
    results['summary'] = {
        'total': total,
        'fresh_count': len(results['fresh']),
        'stale_count': len(results['stale']),
        'critical_count': len(results['critical']),
        'missing_count': len(results['missing']),
        'health_score': round(len(results['fresh']) / max(total, 1) * 100, 1)
    }
    return results

def validate_data_ranges(df):
    """Validate data values fall within expected ranges"""
    issues = {}
    for indicator, (min_val, max_val) in VALIDATION_RANGES.items():
        if indicator in df.columns:
            series = df[indicator].dropna()
            if not series.empty:
                latest = series.iloc[-1]
                if latest < min_val or latest > max_val:
                    issues[indicator] = {'value': latest, 'range': (min_val, max_val)}
    return issues

@st.cache_data(ttl=600, show_spinner=False)
def get_market_data(_csv_mtime=None, _force_refresh=False):
    """The main data aggregation function - Parallel Version"""
    if not _force_refresh:
        cached_df, cached_original = _load_from_disk_cache()
        if cached_df is not None: return cached_df, cached_original
    
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=730)
    credit_stock_data = None
    
    # ========== PARALLEL PHASE: FRED + Yahoo simultaneous ==========
    with ThreadPoolExecutor(max_workers=2) as executor:
        # FRED fetch (internally parallelized with 15 workers)
        fred_future = executor.submit(_fetch_fred_parallel, FRED_INDICATORS, start, end, 15)
        # Yahoo fetch
        yahoo_future = executor.submit(_fetch_yahoo_data, YAHOO_INDICATORS, start, end)
        
        fred_series = fred_future.result()
        y_data = yahoo_future.result()
    
    # ========== CN_Credit_Stock (special: 5 years) ==========
    try:
        credit_start = end - datetime.timedelta(days=365*5)
        credit_stock_data = web.DataReader(
            FRED_INDICATORS.get('CN_Credit_Stock'), 'fred', 
            credit_start, end, api_key=FRED_API_KEY
        )
        credit_stock_data.columns = ['CN_Credit_Stock']
    except:
        pass
    
    # Join All Data
    df = pd.concat(fred_series + ([y_data] if not y_data.empty else []), axis=1).sort_index()
    
    # Manual Data Injection (Override/Append for CN/JP/EU M2 when FRED is stale)
    if MANUAL_GLOBAL_M2:
        for key, data in MANUAL_GLOBAL_M2.items():
            try:
                date_str = data.get('date')
                val = data.get('value')
                cpi_val = data.get('cpi')
                
                if date_str and val is not None:
                    dt = pd.to_datetime(date_str)
                    dt = dt.replace(day=1)
                    
                    if key not in df.columns:
                        df[key] = np.nan
                    
                    df.loc[dt, key] = val
                    
                    region = key.split('_')[0]
                    cpi_col = f"{region}_CPI"
                    if cpi_val is not None:
                        if cpi_col not in df.columns:
                            df[cpi_col] = np.nan
                        df.loc[dt, cpi_col] = cpi_val
            except Exception as e:
                pass
    
    df = df.sort_index()
    
    # Calculate Real M2 for Global data (using CPI from FRED or Manual)
    for region in ['CN', 'JP', 'EU']:
        m2_col = f'{region}_M2'
        cpi_col = f'{region}_CPI'
        real_col = f'{region}_M2_Real'
        
        if m2_col in df.columns and cpi_col in df.columns:
            cpi_latest = df[cpi_col].dropna().iloc[-1] if not df[cpi_col].dropna().empty else 0
            df[real_col] = df[m2_col] / (1 + cpi_latest / 100)
    
    # Calculations
    if all(c in df.columns for c in ['Fed_Assets', 'TGA', 'ON_RRP', 'SRF', 'FIMA']):
        df['Net_Liquidity'] = df['Fed_Assets'] - df['TGA'] - df['ON_RRP'] - df['SRF'] - df['FIMA']
    elif all(c in df.columns for c in ['Fed_Assets', 'TGA', 'ON_RRP']):
        # Fallback without SRF/FIMA (usually near zero)
        df['Net_Liquidity'] = df['Fed_Assets'] - df['TGA'] - df['ON_RRP']
    
    if all(c in df.columns for c in ['M2SL', 'CPI']):
        cpi_filled = df['CPI'].ffill()
        cpi_base = cpi_filled.dropna().iloc[0] if not cpi_filled.dropna().empty else 1
        df['US_Real_M2_Index'] = (df['M2SL'] / cpi_filled) * cpi_base

    if all(c in df.columns for c in ['SOMA_Bills', 'SOMA_Total']):
        df['SomaBillsRatio'] = (df['SOMA_Bills'] / df['SOMA_Total']) * 100
    
    # Global M2 (USD converted) - BTC相関で有名な指標
    # US M2 (Trillions) + CN M2 / USDCNY + JP M2 / USDJPY + EU M2 * EURUSD
    try:
        required_m2 = ['M2SL', 'CN_M2', 'JP_M2', 'EU_M2']
        required_fx = ['USDCNY', 'USDJPY', 'EURUSD']
        if all(c in df.columns for c in required_m2) and all(c in df.columns for c in required_fx):
            # M2SL is already in Billions, others are in local currency Billions
            us_m2 = df['M2SL'].ffill()  # Billions USD
            cn_m2_usd = df['CN_M2'].ffill() / df['USDCNY'].ffill()  # CNY to USD
            jp_m2_usd = df['JP_M2'].ffill() / df['USDJPY'].ffill()  # JPY to USD (in 100M, so /100)
            eu_m2_usd = df['EU_M2'].ffill() * df['EURUSD'].ffill()  # EUR to USD
            df['Global_M2'] = (us_m2 + cn_m2_usd + jp_m2_usd / 1000 + eu_m2_usd) / 1000  # Trillions
    except:
        pass
    # RMP Detection Logic (Matches market_app.py)
    if 'SOMA_Bills' in df.columns:
        df['RMP_Alert_Active'] = False
        df['RMP_Status_Text'] = "📊 RMP監視中（2025年12月12日開始）"
        bills_recent = df['SOMA_Bills'].tail(30)
        if len(bills_recent) >= 7:
            bills_7d_ago = bills_recent.iloc[-7]
            bills_now = bills_recent.iloc[-1]
            weekly_change = bills_now - bills_7d_ago
            if weekly_change >= 4.5:
                df.loc[df.index[-1], 'RMP_Alert_Active'] = True
                if weekly_change <= 15.0:
                    df.loc[df.index[-1], 'RMP_Status_Text'] = f"✅ RMP実行中: +${weekly_change:.1f}B/週（目標ペース）"
                else:
                    df.loc[df.index[-1], 'RMP_Status_Text'] = f"⚠️ RMP加速: +${weekly_change:.1f}B/週（通常ペース超過！）"
            elif weekly_change >= 0:
                df.loc[df.index[-1], 'RMP_Status_Text'] = f"🔄 RMP縮小: +${weekly_change:.1f}B/週（ペース減速）"
            else:
                df.loc[df.index[-1], 'RMP_Status_Text'] = f"⛔ Bills売却: ${weekly_change:.1f}B/週（RMP停止？）"

    # China Credit Impulse Proxy (Matches market_app.py)
    if credit_stock_data is not None and len(credit_stock_data) >= 5:
        try:
            credit = credit_stock_data['CN_Credit_Stock'].dropna()
            credit_flow = credit.diff()
            credit_flow_change = credit_flow - credit_flow.shift(4)
            df['CN_Credit_Impulse'] = (credit_flow_change / (136000 / 4)) * 100
        except: pass

    last_valid_dates = {col: df[col].dropna().index[-1].strftime('%Y-%m-%d') 
                       for col in df.columns if not df[col].dropna().empty}
    
    fred_ids = list(set(FRED_INDICATORS.values()))
    release_info = get_fred_release_dates(fred_ids)
    col_release = {ind: release_info[sid] for ind, sid in FRED_INDICATORS.items() if sid in release_info}
    
    df_original = df.copy()
    df = df.ffill()
    df.attrs = {'last_valid_dates': last_valid_dates, 'fred_release_dates': col_release}
    df_original.attrs = df.attrs.copy()
    
    _save_to_disk_cache(df, df_original)
    return df, df_original

def get_mom_yoy(df_column, df_original, freq='M'):
    """Calculate MoM% and YoY% using ORIGINAL (pre-ffill) data for accuracy"""
    series = df_original.get(df_column)
    if series is None or len(series.dropna()) < 2:
        return None, None
    s = series.dropna()
    curr = s.iloc[-1]
    prev = s.iloc[-2]
    mom = (curr / prev - 1) * 100 if prev != 0 else 0
    
    # YoY: Monthly=12, Quarterly=4
    offset = 12 if freq == 'M' else 4
    yoy = None
    if len(s) > offset:
        prev_yr = s.iloc[-(offset+1)]
        yoy = (curr / prev_yr - 1) * 100 if prev_yr != 0 else 0
    return mom, yoy

@st.cache_data(ttl=3600, show_spinner=False)
def get_pe_ratios():
    """Fetch P/E ratios from scraping and YahooFinance"""
    try:
        res = {'sp500_pe': None, 'sp500_pe_avg': 19.5, 'nasdaq_pe': None}
        try:
            h = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get("https://www.multpl.com/s-p-500-pe-ratio", headers=h, timeout=10)
            if r.status_code == 200:
                m = re.search(r'Current S&P 500 PE Ratio is\s*([\d.]+)', r.text)
                if m: res['sp500_pe'] = float(m.group(1))
        except: pass
        try:
            q = yf.Ticker("QQQ")
            res['nasdaq_pe'] = q.info.get('trailingPE')
        except: pass
        return res
    except: return None

@st.cache_data(ttl=300, show_spinner=False)
def get_crypto_leverage_data():
    """Fetch crypto leverage indicators from various APIs with multi-source fallback"""
    try:
        res = {
            'btc_funding_rate': None, 'eth_funding_rate': None, 
            'btc_open_interest': None, 'eth_open_interest': None,
            'btc_oi_history': None, 'eth_oi_history': None,
            'btc_oi_avg_30d': None, 'btc_oi_ath': None, 'btc_oi_atl': None,
            'eth_oi_avg_30d': None, 'eth_oi_ath': None, 'eth_oi_atl': None,
            'btc_long_short_ratio': None,
            'timestamp': datetime.datetime.now().isoformat()
        }
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # 1. Try CoinGlass for funding rates
        try:
            r = requests.get("https://open-api.coinglass.com/public/v2/funding", headers=headers, timeout=10)
            if r.status_code == 200 and r.json().get('success'):
                for item in r.json()['data']:
                    if item.get('symbol') == 'BTC': res['btc_funding_rate'] = item.get('uMarginRateAvg')
                    elif item.get('symbol') == 'ETH': res['eth_funding_rate'] = item.get('uMarginRateAvg')
        except: pass

        # 2. Fallback to Binance for funding rates
        if res['btc_funding_rate'] is None:
            try:
                r = requests.get("https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1", timeout=5)
                if r.status_code == 200: res['btc_funding_rate'] = float(r.json()[0]['fundingRate']) * 100
            except: pass
        if res['eth_funding_rate'] is None:
            try:
                r = requests.get("https://fapi.binance.com/fapi/v1/fundingRate?symbol=ETHUSDT&limit=1", timeout=5)
                if r.status_code == 200: res['eth_funding_rate'] = float(r.json()[0]['fundingRate']) * 100
            except: pass
            
        # 3. Open Interest (Current)
        try:
            r = requests.get("https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT", timeout=5)
            if r.status_code == 200: res['btc_open_interest'] = float(r.json()['openInterest'])
            r = requests.get("https://fapi.binance.com/fapi/v1/openInterest?symbol=ETHUSDT", timeout=5)
            if r.status_code == 200: res['eth_open_interest'] = float(r.json()['openInterest'])
        except: pass

        # 4. OI History (30 days, 4h limit=180)
        for sym in ['BTC', 'ETH']:
            try:
                r = requests.get(f"https://fapi.binance.com/futures/data/openInterestHist?symbol={sym}USDT&period=4h&limit=180", timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    vals = [float(d['sumOpenInterest']) for d in data]
                    res[f'{sym.lower()}_oi_history'] = {'values': vals, 'timestamps': [datetime.datetime.fromtimestamp(d['timestamp']/1000) for d in data]}
                    res[f'{sym.lower()}_oi_avg_30d'] = sum(vals)/len(vals) if vals else None
                    res[f'{sym.lower()}_oi_ath'] = max(vals) if vals else None
                    res[f'{sym.lower()}_oi_atl'] = min(vals) if vals else None
            except: pass
                
        # 5. Long/Short Ratio
        try:
            r = requests.get("https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=1h&limit=1", timeout=5)
            if r.status_code == 200: res['btc_long_short_ratio'] = float(r.json()[0]['longShortRatio'])
        except: pass
        
        return res
    except: return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_stablecoin_data():
    """Fetch stablecoin supply data from DeFiLlama"""
    try:
        r = requests.get("https://stablecoins.llama.fi/stablecoins?includePrices=true", timeout=15)
        if r.status_code == 200:
            data = r.json().get('peggedAssets', [])
            top = []
            total = 0
            for c in data:
                if c.get('pegType') == 'peggedUSD':
                    circ = c.get('circulating', {}).get('peggedUSD', 0)
                    if circ > 1e6:
                        total += circ
                        top.append({'name': c['name'], 'symbol': c['symbol'], 'circulating': circ/1e9})
            top.sort(key=lambda x: x['circulating'], reverse=True)
            return {'total_supply': total/1e9, 'top_coins': top[:15]}
    except: pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_stablecoin_historical():
    """Fetch historical stablecoin supply from DeFiLlama"""
    try:
        r = requests.get("https://stablecoins.llama.fi/stablecoincharts/all?stablecoin=1", timeout=15)
        if r.status_code == 200:
            records = [{'date': datetime.datetime.fromtimestamp(int(p['date'])), 
                       'Total': p.get('totalCirculating', {}).get('peggedUSD', 0)/1e9} 
                      for p in r.json() if 'date' in p]
            df = pd.DataFrame(records)
            if not df.empty: return df.set_index('date').sort_index()
    except: pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_tokenized_treasury_data():
    """Fetch tokenized RWA data from DeFiLlama with comprehensive categorization"""
    try:
        r = requests.get("https://api.llama.fi/protocols", timeout=15)
        if r.status_code == 200:
            prots = r.json()
            treasury_data, gold_data, other_rwa_data = [], [], []
            t_tvl, g_tvl, o_tvl = 0, 0, 0
            # Keywords from market_app.py
            t_kw = ['treasury', 'tbill', 't-bill', 'buidl', 'usdy', 'usdm', 'usyc', 'ondo', 'openeden', 'hashnote', 'mountain', 'backed']
            g_kw = ['gold', 'xaut', 'paxg', 'gld', 'xau']
            for p in prots:
                category = p.get('category', '').lower()
                is_rwa = 'rwa' in category or 'real world' in category
                if not is_rwa: continue
                tvl = p.get('tvl', 0)
                if tvl < 1e6: continue
                info = {
                    'name': p['name'], 'symbol': p.get('symbol', '-'), 'tvl': tvl/1e9, 
                    'slug': p.get('slug', ''), 'change_1d': p.get('change_1d', 0)
                }
                name_low = p['name'].lower()
                slug_low = p.get('slug', '').lower()
                symbol_low = p.get('symbol', '').lower()
                
                if any(kw in name_low or kw in slug_low or kw in symbol_low for kw in g_kw):
                    gold_data.append(info); g_tvl += tvl
                elif any(kw in name_low or kw in slug_low or kw in symbol_low for kw in t_kw):
                    treasury_data.append(info); t_tvl += tvl
                else:
                    other_rwa_data.append(info); o_tvl += tvl
            return {
                'treasury': {'total_tvl': t_tvl/1e9, 'protocols': sorted(treasury_data, key=lambda x: x['tvl'], reverse=True)[:10]},
                'gold': {'total_tvl': g_tvl/1e9, 'protocols': sorted(gold_data, key=lambda x: x['tvl'], reverse=True)[:5]},
                'other_rwa': {'total_tvl': o_tvl/1e9, 'protocols': sorted(other_rwa_data, key=lambda x: x['tvl'], reverse=True)[:10]},
                'total_rwa_tvl': (t_tvl + g_tvl + o_tvl) / 1e9,
                'timestamp': datetime.datetime.now().isoformat()
            }
    except: pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_protocol_historical(slug: str):
    """Fetch historical TVL for a protocol"""
    try:
        r = requests.get(f"https://api.llama.fi/protocol/{slug}", timeout=15)
        if r.status_code == 200:
            hist = r.json().get('tvl', [])
            records = [{'date': datetime.datetime.fromtimestamp(p['date']), 'TVL': p['totalLiquidityUSD']/1e9} for p in hist]
            df = pd.DataFrame(records)
            if not df.empty: return df.set_index('date').sort_index()
    except: pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_crypto_fear_greed():
    """Fetch Crypto F\u0026G"""
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=30", timeout=10)
        if r.status_code == 200:
            data = r.json().get('data', [])
            if not data: return None
            history = [{'date': datetime.datetime.fromtimestamp(int(p['timestamp'])), 'value': int(p['value'])} for p in data]
            return {
                'current': int(data[0]['value']),
                'classification': data[0]['value_classification'],
                'history': pd.DataFrame(history).set_index('date').sort_index()
            }
    except: pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_cnn_fear_greed():
    """Fetch CNN F\u0026G"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            fg = data.get('fear_and_greed', {})
            hist = [{'date': datetime.datetime.fromtimestamp(p['x']/1000), 'value': p['y']} 
                    for p in data.get('fear_and_greed_historical', {}).get('data', [])]
            return {
                'current': fg.get('score'),
                'classification': fg.get('rating'),
                'history': pd.DataFrame(hist).set_index('date').sort_index()
            }
    except: pass
    return None

@st.cache_data(ttl=86400, show_spinner=False)
def get_aaii_sentiment():
    """Placeholder for AAII"""
    return {'bullish': 38.5, 'neutral': 31.2, 'bearish': 30.3, 'date': datetime.date.today().isoformat()}

@st.cache_data(ttl=86400, show_spinner=False)
def get_fomc_sep_projections():
    """Fetch FOMC SEP from FRED"""
    try:
        sep_map = {'ff_rate': 'FEDTARMD', 'gdp_growth': 'GDPC1CTM', 'unemployment': 'UNRATECTM', 'core_pce': 'PCECTPICTM'}
        projections = {}
        for key, sid in sep_map.items():
            try:
                d = web.DataReader(sid, 'fred', datetime.datetime.now()-datetime.timedelta(days=730), datetime.datetime.now(), api_key=FRED_API_KEY)
                if not d.empty:
                    projections[key] = {'latest': d.iloc[-1].values[0], 'date': d.index[-1].strftime('%Y-%m-%d')}
            except: projections[key] = None
        return projections
    except: return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_cme_fedwatch():
    """Placeholder for CME FedWatch"""
    return {'next_meeting': '2026-01-29', 'probabilities': {'cut_25bp': 65.0, 'hold': 35.0}}

@st.cache_data(ttl=3600, show_spinner=False)
def get_put_call_ratio():
    """
    Fetch Equity Put/Call Ratio from CBOE.
    Scrapes the daily market statistics page.
    """
    try:
        url = "https://www.cboe.com/us/options/market_statistics/daily/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            import re
            content = response.text
            # Use regex to find Equity Put/Call Ratio
            matches = re.findall(r'EQUITY.*?(\d\.\d{2})', content, re.IGNORECASE | re.DOTALL)
            if matches:
                return float(matches[0])
            pcr_match = re.search(r'Equity\s+Put/Call\s+Ratio.*?([\d\.]+)', content, re.IGNORECASE | re.DOTALL)
            if pcr_match:
                return float(pcr_match.group(1))
    except: pass
    return None
