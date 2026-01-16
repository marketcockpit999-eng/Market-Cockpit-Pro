# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Data Fetcher
全てのデータ取得関数を管理

CACHING ARCHITECTURE:
1. Disk cache (.market_data_cache.pkl) - TTL: 10 min (set in config)
2. Streamlit @st.cache_data on get_market_data() - TTL: 1 hour
3. Streamlit @st.cache_data on get_crypto_leverage_data() - TTL: 5 min

To force refresh:
- UI: Click "Force Update" button
- CLI: get_market_data(_force_refresh=True)
- Nuclear: Delete .market_data_cache.pkl + restart app
"""

import streamlit as st
import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
import numpy as np
import datetime
import requests
import re
import os
import pickle
import time
from io import StringIO
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging for data fetcher
logger = logging.getLogger(__name__)

from .config import (
    FRED_API_KEY, FRED_INDICATORS, YAHOO_INDICATORS, 
    FRED_UNITS, MANUAL_DATA_FILE, MANUAL_GLOBAL_M2
)

# ========== CONFIGURATION ==========
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.market_data_cache.pkl')
CACHE_TTL_SECONDS = 21600  # 6 hours (matches scheduled update frequency)
MAX_WORKERS_FRED = 10    # Max parallel FRED API requests
MAX_WORKERS_YAHOO = 5    # Max parallel Yahoo API requests (yf.download handles batching)
FRED_REQUEST_TIMEOUT = 30  # Timeout for individual FRED requests (seconds)

# ========== DISK CACHE ==========

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

# ========== PARALLEL FRED FETCH HELPERS ==========

def _fetch_single_fred(name: str, ticker: str, start: datetime.datetime, end: datetime.datetime) -> tuple:
    """
    Fetch a single FRED series. Used by ThreadPoolExecutor.
    
    Returns:
        tuple: (name, DataFrame or None, error_message or None)
    """
    try:
        # Special handling for CN_Credit_Stock (needs longer history)
        if name == 'CN_Credit_Stock':
            credit_start = end - datetime.timedelta(days=365*5)
            s = web.DataReader(ticker, 'fred', credit_start, end, api_key=FRED_API_KEY)
        else:
            s = web.DataReader(ticker, 'fred', start, end, api_key=FRED_API_KEY)
        
        s.columns = [name]
        logger.debug(f"✓ FRED {name}: {len(s)} rows")
        return (name, s, None)
        
    except Exception as e:
        error_msg = str(e)[:100]
        logger.warning(f"✗ FRED {name} ({ticker}): {error_msg}")
        return (name, None, error_msg)


def _fetch_fred_parallel(indicators: dict, start: datetime.datetime, end: datetime.datetime) -> list:
    """
    Fetch multiple FRED series in parallel using ThreadPoolExecutor.
    
    Args:
        indicators: Dict of {name: ticker}
        start: Start date
        end: End date
    
    Returns:
        list: List of DataFrames (successful fetches only)
    """
    fred_series = []
    errors = []
    
    logger.info(f"Fetching {len(indicators)} FRED indicators with {MAX_WORKERS_FRED} workers...")
    fetch_start = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_FRED) as executor:
        # Submit all tasks
        futures = {
            executor.submit(_fetch_single_fred, name, ticker, start, end): name
            for name, ticker in indicators.items()
        }
        
        # Collect results as they complete
        for future in as_completed(futures, timeout=FRED_REQUEST_TIMEOUT * 2):
            name = futures[future]
            try:
                result_name, df, error = future.result(timeout=FRED_REQUEST_TIMEOUT)
                if df is not None:
                    fred_series.append(df)
                elif error:
                    errors.append((result_name, error))
            except Exception as e:
                errors.append((name, str(e)[:100]))
    
    elapsed = time.time() - fetch_start
    logger.info(f"FRED fetch completed: {len(fred_series)}/{len(indicators)} success in {elapsed:.1f}s")
    
    if errors:
        logger.warning(f"FRED errors ({len(errors)}): {errors[:5]}...")  # Show first 5
    
    return fred_series


def _fetch_yahoo_data(indicators: dict, start: datetime.datetime, end: datetime.datetime) -> pd.DataFrame:
    """
    Fetch Yahoo Finance data. yf.download already handles batching efficiently.
    
    Returns:
        DataFrame with renamed columns
    """
    logger.info(f"Fetching {len(indicators)} Yahoo indicators...")
    fetch_start = time.time()
    
    try:
        y_tickers = list(indicators.values())
        y_data = yf.download(y_tickers, start=start, end=end, progress=False, threads=True)['Close']
        
        # Rename columns from ticker to name
        inv_yahoo = {v: k for k, v in indicators.items()}
        y_data = y_data.rename(columns=inv_yahoo)
        
        elapsed = time.time() - fetch_start
        logger.info(f"Yahoo fetch completed: {len(y_data.columns)} columns in {elapsed:.1f}s")
        
        return y_data
        
    except Exception as e:
        logger.error(f"Yahoo fetch failed: {e}")
        return pd.DataFrame()


# ========== FRED RELEASE DATES ==========
@st.cache_data(ttl=3600, show_spinner=False)
def get_fred_release_dates(fred_ids: list) -> dict:
    """Fetch actual release dates from FRED API"""
    release_dates = {}
    for series_id in fred_ids:
        try:
            url = f"https://api.stlouisfed.org/fred/series?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'seriess' in data and len(data['seriess']) > 0:
                    series_info = data['seriess'][0]
                    last_updated_str = series_info.get('last_updated', '')
                    if last_updated_str:
                        date_part = last_updated_str.split(' ')[0]
                        release_dates[series_id] = {
                            'last_updated': date_part,
                            'title': series_info.get('title', ''),
                            'frequency': series_info.get('frequency', ''),
                            'observation_end': series_info.get('observation_end', '')
                        }
        except:
            pass
    return release_dates

# ========== MAIN DATA FUNCTION ==========
@st.cache_data(ttl=600, show_spinner=False)
def get_market_data(_csv_mtime=None, _force_refresh=False):
    """Main data aggregation function - fetches all market data"""
    
    # Try disk cache first
    if not _force_refresh:
        cached_df, cached_original = _load_from_disk_cache()
        if cached_df is not None and cached_original is not None:
            return cached_df, cached_original
    
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=1825) # 5 years to ensure sufficient history for calculations (e.g. Credit Impulse)
    
    logger.info("="*60)
    logger.info(f"Starting market data fetch at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    total_start = time.time()
    
    # Fetch FRED Data (PARALLEL)
    fred_series = _fetch_fred_parallel(FRED_INDICATORS, start, end)
    
    # Fetch Yahoo Data (already uses threading internally)
    y_data = _fetch_yahoo_data(YAHOO_INDICATORS, start, end)
    
    total_elapsed = time.time() - total_start
    logger.info(f"Total fetch time: {total_elapsed:.1f}s")
    
    # Join All Data
    df = pd.concat(fred_series + ([y_data] if not y_data.empty else []), axis=1).sort_index()

    # Manual Data Injection (Override/Append)
    if MANUAL_GLOBAL_M2:
        for key, data in MANUAL_GLOBAL_M2.items():
            try:
                # Parse date (assume start of month for FRED consistency)
                date_str = data.get('date')
                val = data.get('value')
                cpi_val = data.get('cpi')
                
                if date_str and val is not None:
                    # Create datetime object (Day 1)
                    dt = pd.to_datetime(date_str)
                    dt = dt.replace(day=1)
                    
                    # Ensure column exists
                    if key not in df.columns:
                        df[key] = np.nan
                    
                    # Update M2 Value
                    df.loc[dt, key] = val
                    
                    # Update CPI Value if provided (for Real calculation)
                    region = key.split('_')[0] # CN, JP, EU
                    cpi_col = f"{region}_CPI"
                    if cpi_val is not None:
                        if cpi_col not in df.columns:
                            df[cpi_col] = np.nan
                        df.loc[dt, cpi_col] = cpi_val
            except Exception as e:
                print(f"Manual data injection error for {key}: {e}")
                pass
    
    # Sort again just in case new rows were added at the end (though loc usually handles order if index is datetime)
    df = df.sort_index()

    # Calculate Real M2 for Global data (using CPI from FRED)
    for region in ['CN', 'JP', 'EU']:
        m2_col = f'{region}_M2'
        cpi_col = f'{region}_CPI'
        real_col = f'{region}_M2_Real'
        
        if m2_col in df.columns and cpi_col in df.columns:
            cpi_latest = df[cpi_col].dropna().iloc[-1] if not df[cpi_col].dropna().empty else 0
            df[real_col] = df[m2_col] / (1 + cpi_latest / 100)
    
    # Unit Normalization (Million to Billion)
    mil_to_bil = ['Fed_Assets', 'TGA', 'Reserves', 'SOMA_Total', 'Bank_Cash', 
                  'SRF', 'FIMA', 'Primary_Credit', 'Total_Loans', 'SOMA_Bills', 
                  'M2SL', 'M2REAL', 'CI_Loans', 'CRE_Loans']
    for col in mil_to_bil:
        if col in df.columns:
            df[col] = df[col] / 1000
    
    # Calculate Net Liquidity
    if all(c in df.columns for c in ['Fed_Assets', 'TGA', 'ON_RRP']):
        df['Net_Liquidity'] = df['Fed_Assets'] - df['TGA'] - df['ON_RRP']
    
    # Calculate Real M2 Index
    if all(c in df.columns for c in ['M2SL', 'CPI']):
        cpi_filled = df['CPI'].ffill()
        cpi_base = cpi_filled.dropna().iloc[0] if not cpi_filled.dropna().empty else 1
        df['US_Real_M2_Index'] = (df['M2SL'] / cpi_filled) * cpi_base
    
    # Calculate SOMA Bills Ratio
    if all(c in df.columns for c in ['SOMA_Bills', 'SOMA_Total']):
        df['SomaBillsRatio'] = (df['SOMA_Bills'] / df['SOMA_Total']) * 100
    
    # RMP Detection Logic
    if 'SOMA_Bills' in df.columns:
        df['RMP_Alert_Active'] = False
        df['RMP_Status_Text'] = "📊 RMP監視中（2025年12月12日開始）"
        
        bills_recent = df['SOMA_Bills'].tail(30)
        
        if len(bills_recent) >= 7:
            bills_7d_ago = bills_recent.iloc[-7] if len(bills_recent) >= 7 else bills_recent.iloc[0]
            bills_now = bills_recent.iloc[-1]
            weekly_change = bills_now - bills_7d_ago
            
            expected_weekly_min = 4.5
            expected_weekly_max = 15.0
            
            if weekly_change >= expected_weekly_min:
                if weekly_change <= expected_weekly_max:
                    df.loc[df.index[-1], 'RMP_Alert_Active'] = True
                    df.loc[df.index[-1], 'RMP_Status_Text'] = f"✅ RMP実行中: +${weekly_change:.1f}B/週（目標ペース）"
                else:
                    df.loc[df.index[-1], 'RMP_Alert_Active'] = True
                    df.loc[df.index[-1], 'RMP_Status_Text'] = f"⚠️ RMP加速: +${weekly_change:.1f}B/週（通常ペース超過！）"
            elif weekly_change >= 0:
                df.loc[df.index[-1], 'RMP_Status_Text'] = f"🔄 RMP縮小: +${weekly_change:.1f}B/週（ペース減速）"
            else:
                df.loc[df.index[-1], 'RMP_Status_Text'] = f"⛔ Bills売却: ${weekly_change:.1f}B/週（RMP停止？）"
    
    # Calculate China Credit Impulse
    if 'CN_Credit_Stock' in df.columns:
        credit = df['CN_Credit_Stock'].dropna()
        if len(credit) >= 5:
            try:
                credit_flow = credit.diff()
                credit_flow_change = credit_flow - credit_flow.shift(4)
                annual_gdp_bln_cny = 136000 # 2024 est
                quarterly_gdp = annual_gdp_bln_cny / 4
                credit_impulse = (credit_flow_change / quarterly_gdp) * 100
                df['CN_Credit_Impulse'] = credit_impulse.reindex(df.index)
            except Exception as e:
                print(f"Error calculating Credit Impulse: {e}")

    # Normalize International M2 to Trillions and Calculate Global M2
    # Heuristic: if value > 1000, it's likely Billions (or Trillions Yen), so divide by 1000 to get Trillions (or consistent unit)
    # CN_M2 (Trillion CNY), JP_M2 (Trillion JPY), EU_M2 (Trillion EUR)
    for col in ['CN_M2', 'JP_M2', 'EU_M2']:
        if col in df.columns:
            last_val = df[col].dropna().iloc[-1] if len(df[col].dropna()) > 0 else 0
            if last_val > 1000:
                df[col] = df[col] / 1000

    # Calculate Global M2 (USD)
    # Global M2 = US M2 + CN M2/USDCNY + JP M2/USDJPY + EU M2 * EURUSD
    required_cols = ['M2SL', 'CN_M2', 'JP_M2', 'EU_M2', 'USDCNY', 'USDJPY', 'EURUSD']
    if all(c in df.columns for c in required_cols):
        try:
            # CN M2 (Trillion USD)
            cn_m2_usd = df['CN_M2'] / df['USDCNY']
            
            # JP M2 (Trillion USD)
            jp_m2_usd = df['JP_M2'] / df['USDJPY']
            
            # EU M2 (Trillion USD)
            eu_m2_usd = df['EU_M2'] * df['EURUSD']
            
            # Sum up (M2SL is already Trillions USD)
            df['Global_M2'] = df['M2SL'] + cn_m2_usd + jp_m2_usd + eu_m2_usd
        except Exception as e:
            print(f"Error calculating Global M2: {e}")
    
    # Store last valid dates BEFORE forward fill
    last_valid_dates = {}
    for col in df.columns:
        valid_data = df[col].dropna()
        if len(valid_data) > 0:
            last_valid_dates[col] = valid_data.index[-1].strftime('%Y-%m-%d')
    
    # Fetch FRED release dates
    fred_ids = list(set(FRED_INDICATORS.values()))
    fred_release_info = get_fred_release_dates(fred_ids)
    
    col_release_dates = {}
    for indicator, series_id in FRED_INDICATORS.items():
        if series_id in fred_release_info:
            col_release_dates[indicator] = fred_release_info[series_id]['last_updated']
    
    # Store original BEFORE forward fill
    df_original = df.copy()
    
    # Forward fill
    df = df.ffill()
    
    # Backward fill for Global M2 (manual data is recent, need to fill historical)
    global_m2_cols = ['CN_M2', 'JP_M2', 'EU_M2', 'CN_CPI', 'JP_CPI', 'EU_CPI']
    for col in global_m2_cols:
        if col in df.columns:
            df[col] = df[col].bfill()
    
    # Store metadata
    df.attrs['last_valid_dates'] = last_valid_dates
    df.attrs['fred_release_dates'] = col_release_dates
    df_original.attrs = df.attrs.copy()
    
    # Save to disk cache
    _save_to_disk_cache(df, df_original)
    
    return df, df_original

# ========== P/E RATIOS ==========
@st.cache_data(ttl=3600, show_spinner=False)
def get_pe_ratios():
    """Fetch S&P 500 and NASDAQ P/E ratios"""
    try:
        result = {
            'sp500_pe': None,
            'sp500_pe_avg': 19.5,
            'nasdaq_pe': None,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # S&P 500 P/E from multpl.com
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            url = "https://www.multpl.com/s-p-500-pe-ratio"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                match = re.search(r'Current S&P 500 PE Ratio is\s*([\d.]+)', response.text)
                if match:
                    result['sp500_pe'] = float(match.group(1))
        except:
            pass
        
        # NASDAQ P/E from Yahoo Finance (QQQ as proxy)
        try:
            qqq = yf.Ticker("QQQ")
            info = qqq.info
            result['nasdaq_pe'] = info.get('trailingPE')
        except:
            pass
        
        return result
    except:
        return None

# ========== CRYPTO LEVERAGE DATA ==========
def _fetch_funding_rate_binance(symbol: str) -> float:
    """Fetch funding rate from Binance (blocked in Japan)"""
    try:
        url = f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}USDT&limit=1"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data:
                return float(data[0]['fundingRate']) * 100
    except:
        pass
    return None

def _fetch_funding_rate_bybit(symbol: str) -> float:
    """Fetch funding rate from Bybit (fallback #1)"""
    try:
        url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}USDT"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('result', {}).get('list'):
                fr = data['result']['list'][0].get('fundingRate')
                if fr:
                    return float(fr) * 100
    except:
        pass
    return None

def _fetch_funding_rate_okx(symbol: str) -> float:
    """Fetch funding rate from OKX (fallback #2)"""
    try:
        url = f"https://www.okx.com/api/v5/public/funding-rate?instId={symbol}-USDT-SWAP"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('data'):
                fr = data['data'][0].get('fundingRate')
                if fr:
                    return float(fr) * 100
    except:
        pass
    return None

def _fetch_open_interest_bybit(symbol: str) -> float:
    """Fetch open interest from Bybit"""
    try:
        url = f"https://api.bybit.com/v5/market/open-interest?category=linear&symbol={symbol}USDT&intervalTime=1h&limit=1"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('result', {}).get('list'):
                oi = data['result']['list'][0].get('openInterest')
                if oi:
                    return float(oi)
    except:
        pass
    return None

def _fetch_long_short_ratio_bybit() -> float:
    """Fetch long/short ratio from Bybit"""
    try:
        url = "https://api.bybit.com/v5/market/account-ratio?category=linear&symbol=BTCUSDT&period=1h&limit=1"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get('result', {}).get('list'):
                buy = float(data['result']['list'][0].get('buyRatio', 0.5))
                sell = float(data['result']['list'][0].get('sellRatio', 0.5))
                if sell > 0:
                    return buy / sell
    except:
        pass
    return None

def _fetch_oi_from_coingecko() -> dict:
    """Fetch Open Interest from CoinGecko (works in Japan)"""
    try:
        url = "https://api.coingecko.com/api/v3/derivatives/exchanges/binance_futures"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            btc_oi = data.get('open_interest_btc')
            if btc_oi:
                return {'btc': float(btc_oi), 'source': 'CoinGecko'}
    except:
        pass
    return None

def _fetch_ls_ratio_from_coingecko() -> float:
    """Fetch Long/Short ratio approximation from CoinGecko derivatives tickers"""
    try:
        # Get top perpetual contracts
        url = "https://api.coingecko.com/api/v3/derivatives"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            # Find BTCUSDT perpetual
            for contract in data:
                if contract.get('symbol') == 'BTCUSDT' and 'perpetual' in contract.get('contract_type', '').lower():
                    # Use funding rate as proxy for L/S sentiment
                    funding = contract.get('funding_rate')
                    if funding:
                        # Positive funding = longs pay shorts (more longs)
                        # Convert to approximate L/S ratio
                        funding_val = float(funding)
                        if funding_val > 0:
                            return 1.0 + funding_val * 10  # Scale to visible ratio
                        else:
                            return 1.0 / (1 - funding_val * 10)
    except:
        pass
    return None

def _fetch_from_coinmarketcap() -> dict:
    """Fetch derivatives data from CoinMarketCap (priority 1 - works in Japan)"""
    try:
        url = "https://api.coinmarketcap.com/data-api/v3/exchange/market-pairs/latest?slug=binance&category=perpetual"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('status', {}).get('error_code') == '0' or 'data' in data:
                pairs = data.get('data', {}).get('marketPairs', [])
                result = {'source': 'CoinMarketCap'}
                
                for pair in pairs:
                    # BTC/USDT Perpetual
                    if pair.get('marketPair') == 'BTC/USDT' and pair.get('category') == 'perpetual':
                        oi_usd = pair.get('openInterestUsd')
                        funding = pair.get('fundingRate')
                        price = pair.get('price', 95000)
                        result['btc_oi'] = oi_usd / price if oi_usd and price else None
                        result['btc_oi_usd'] = oi_usd
                        result['btc_funding_rate'] = funding * 100 if funding else None
                    
                    # ETH/USDT Perpetual
                    if pair.get('marketPair') == 'ETH/USDT' and pair.get('category') == 'perpetual':
                        oi_usd = pair.get('openInterestUsd')
                        funding = pair.get('fundingRate')
                        price = pair.get('price', 3300)
                        result['eth_oi'] = oi_usd / price if oi_usd and price else None
                        result['eth_oi_usd'] = oi_usd
                        result['eth_funding_rate'] = funding * 100 if funding else None
                
                return result if 'btc_oi' in result else None
    except:
        pass
    return None


@st.cache_data(ttl=300, show_spinner=False)
def get_crypto_leverage_data():
    """Fetch crypto leverage indicators with API fallback
    Priority: 1. CoinMarketCap, 2. CoinGecko, 3. OKX
    (Binance/Bybit blocked in Japan)
    """
    try:
        result = {
            'btc_funding_rate': None,
            'eth_funding_rate': None,
            'btc_open_interest': None,
            'eth_open_interest': None,
            'btc_long_short_ratio': None,
            'btc_oi_avg_30d': None,
            'btc_oi_ath': None,
            'eth_oi_avg_30d': None,
            'eth_oi_ath': None,
            'btc_oi_history': None,
            'eth_oi_history': None,
            'data_source': None,
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Priority 1: CoinMarketCap (most reliable, works in Japan)
        cmc_data = _fetch_from_coinmarketcap()
        if cmc_data:
            result['btc_open_interest'] = cmc_data.get('btc_oi')
            result['btc_funding_rate'] = cmc_data.get('btc_funding_rate')
            result['eth_open_interest'] = cmc_data.get('eth_oi')
            result['eth_funding_rate'] = cmc_data.get('eth_funding_rate')
            result['data_source'] = 'CoinMarketCap'
        
        # Priority 2: CoinGecko (fallback for OI)
        if not result['btc_open_interest']:
            coingecko_oi = _fetch_oi_from_coingecko()
            if coingecko_oi:
                result['btc_open_interest'] = coingecko_oi.get('btc')
                result['data_source'] = 'CoinGecko'
        
        # Priority 3: OKX/Bybit for funding rate (if CMC failed)
        if not result['btc_funding_rate']:
            result['btc_funding_rate'] = (
                _fetch_funding_rate_bybit('BTC') or
                _fetch_funding_rate_okx('BTC')
            )
            if result['btc_funding_rate'] and not result['data_source']:
                result['data_source'] = 'Bybit/OKX'
        
        # ETH Funding Rate
        if not result['eth_funding_rate']:
            result['eth_funding_rate'] = (
                _fetch_funding_rate_bybit('ETH') or
                _fetch_funding_rate_okx('ETH')
            )
        
        # Long/Short Ratio from CoinGecko approximation
        result['btc_long_short_ratio'] = _fetch_ls_ratio_from_coingecko()
        
        # Historical OI estimates
        if result['btc_open_interest']:
            result['btc_oi_avg_30d'] = result['btc_open_interest'] * 0.95
            result['btc_oi_ath'] = result['btc_open_interest'] * 1.1
        
        if result['eth_open_interest']:
            result['eth_oi_avg_30d'] = result['eth_open_interest'] * 0.95
            result['eth_oi_ath'] = result['eth_open_interest'] * 1.1
        
        return result
    except:
        return None


# ========== STABLECOIN DATA ==========
@st.cache_data(ttl=3600, show_spinner=False)
def get_stablecoin_data():
    """Fetch stablecoin supply data from DeFiLlama"""
    try:
        url = "https://stablecoins.llama.fi/stablecoins?includePrices=true"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        data = response.json()
        stablecoins = data.get('peggedAssets', [])
        
        top_coins = []
        total_supply = 0
        coin_ids = {}
        
        for coin in stablecoins:
            if coin.get('pegType') == 'peggedUSD':
                circulating = coin.get('circulating', {}).get('peggedUSD', 0)
                if circulating and circulating > 1000000:
                    total_supply += circulating
                    coin_data = {
                        'id': coin.get('id', ''),
                        'name': coin.get('name', ''),
                        'symbol': coin.get('symbol', ''),
                        'circulating': circulating / 1e9,
                        'mechanism': coin.get('pegMechanism', ''),
                        'price': coin.get('price', 1.0),
                        'prev_day': coin.get('circulatingPrevDay', {}).get('peggedUSD', 0) / 1e9,
                        'prev_week': coin.get('circulatingPrevWeek', {}).get('peggedUSD', 0) / 1e9,
                        'prev_month': coin.get('circulatingPrevMonth', {}).get('peggedUSD', 0) / 1e9,
                    }
                    top_coins.append(coin_data)
                    coin_ids[coin.get('symbol', '')] = coin.get('id', '')
        
        top_coins.sort(key=lambda x: x['circulating'], reverse=True)
        
        return {
            'total_supply': total_supply / 1e9,
            'top_coins': top_coins[:15],
            'coin_ids': coin_ids,
            'timestamp': datetime.datetime.now().isoformat()
        }
    except:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_stablecoin_historical():
    """Fetch historical stablecoin supply from DeFiLlama"""
    try:
        url = "https://stablecoins.llama.fi/stablecoincharts/all?stablecoin=1"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        data = response.json()
        records = []
        
        if isinstance(data, list):
            for point in data:
                try:
                    date_val = point.get('date', 0)
                    if isinstance(date_val, str):
                        date_val = int(date_val)
                    date = datetime.datetime.fromtimestamp(date_val)
                    
                    total = 0
                    if 'totalCirculating' in point and isinstance(point['totalCirculating'], dict):
                        total = point['totalCirculating'].get('peggedUSD', 0) / 1e9
                    elif 'totalCirculatingUSD' in point and isinstance(point['totalCirculatingUSD'], dict):
                        total = point['totalCirculatingUSD'].get('peggedUSD', 0) / 1e9
                    
                    if total > 0:
                        records.append({'date': date, 'Total': total})
                except:
                    continue
        
        df = pd.DataFrame(records)
        if not df.empty:
            df = df.set_index('date').sort_index()
            return df
        return None
    except:
        return None

# ========== TOKENIZED TREASURY DATA ==========
@st.cache_data(ttl=3600, show_spinner=False)
def get_tokenized_treasury_data():
    """Fetch tokenized US Treasury data from DeFiLlama"""
    try:
        url = "https://api.llama.fi/protocols"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        protocols = response.json()
        
        treasury_keywords = ['treasury', 'tbill', 't-bill', 'buidl', 'usdy', 'usdm', 'usyc', 'ondo', 'openeden', 'hashnote', 'mountain', 'backed']
        gold_keywords = ['gold', 'xaut', 'paxg', 'gld', 'xau']
        
        treasury_data = []
        gold_data = []
        other_rwa_data = []
        
        treasury_tvl = 0
        gold_tvl = 0
        other_rwa_tvl = 0
        
        for protocol in protocols:
            name = protocol.get('name', '').lower()
            slug = protocol.get('slug', '').lower()
            symbol = protocol.get('symbol', '').lower()
            category = protocol.get('category', '').lower()
            
            is_rwa = 'rwa' in category or 'real world' in category
            if not is_rwa:
                continue
            
            tvl = protocol.get('tvl', 0)
            if not tvl or tvl < 1000000:
                continue
            
            protocol_info = {
                'name': protocol.get('name', ''),
                'symbol': protocol.get('symbol', '-'),
                'slug': protocol.get('slug', ''),
                'tvl': tvl / 1e9,
                'category': protocol.get('category', 'RWA'),
                'change_1d': protocol.get('change_1d', 0),
                'change_7d': protocol.get('change_7d', 0),
            }
            
            is_gold = any(kw in name or kw in symbol or kw in slug for kw in gold_keywords)
            is_treasury = any(kw in name or kw in symbol or kw in slug for kw in treasury_keywords)
            
            if is_gold:
                gold_data.append(protocol_info)
                gold_tvl += tvl
            elif is_treasury:
                treasury_data.append(protocol_info)
                treasury_tvl += tvl
            else:
                other_rwa_data.append(protocol_info)
                other_rwa_tvl += tvl
        
        treasury_data.sort(key=lambda x: x['tvl'], reverse=True)
        gold_data.sort(key=lambda x: x['tvl'], reverse=True)
        other_rwa_data.sort(key=lambda x: x['tvl'], reverse=True)
        
        return {
            'treasury': {
                'total_tvl': treasury_tvl / 1e9,
                'protocols': treasury_data[:10],
            },
            'gold': {
                'total_tvl': gold_tvl / 1e9,
                'protocols': gold_data[:5],
            },
            'other_rwa': {
                'total_tvl': other_rwa_tvl / 1e9,
                'protocols': other_rwa_data[:10],
            },
            'total_rwa_tvl': (treasury_tvl + gold_tvl + other_rwa_tvl) / 1e9,
            'timestamp': datetime.datetime.now().isoformat()
        }
    except:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_protocol_historical(slug: str):
    """Fetch historical TVL for a protocol from DeFiLlama"""
    try:
        url = f"https://api.llama.fi/protocol/{slug}"
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None
        
        data = response.json()
        tvl_history = data.get('tvl', [])
        
        records = []
        for point in tvl_history:
            try:
                date = datetime.datetime.fromtimestamp(point['date'])
                tvl = point.get('totalLiquidityUSD', 0) / 1e9
                records.append({'date': date, 'TVL': tvl})
            except:
                continue
        
        df = pd.DataFrame(records)
        if not df.empty:
            df = df.set_index('date').sort_index()
            return df
        return None
    except:
        return None

# ========== SENTIMENT INDICATORS ==========
@st.cache_data(ttl=3600, show_spinner=False)
def get_crypto_fear_greed():
    """Fetch Crypto Fear & Greed Index"""
    try:
        url = "https://api.alternative.me/fng/?limit=30"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                current = data['data'][0]
                history = []
                for item in data['data']:
                    history.append({
                        'date': datetime.datetime.fromtimestamp(int(item['timestamp'])),
                        'value': int(item['value']),
                        'classification': item['value_classification']
                    })
                return {
                    'current': int(current['value']),
                    'classification': current['value_classification'],
                    'history': pd.DataFrame(history).set_index('date').sort_index()
                }
    except:
        pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_cnn_fear_greed():
    """Fetch CNN Fear & Greed Index"""
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'fear_and_greed' in data:
                fg = data['fear_and_greed']
                history = []
                if 'fear_and_greed_historical' in data:
                    for point in data['fear_and_greed_historical'].get('data', []):
                        history.append({
                            'date': datetime.datetime.fromtimestamp(point['x'] / 1000),
                            'value': point['y']
                        })
                return {
                    'current': fg.get('score', None),
                    'classification': fg.get('rating', ''),
                    'previous_close': fg.get('previous_close', None),
                    'history': pd.DataFrame(history).set_index('date').sort_index() if history else None
                }
    except:
        pass
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_put_call_ratio():
    """Fetch Put/Call Ratio from CBOE"""
    try:
        url = "https://www.cboe.com/us/options/market_statistics/daily/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            content = response.text
            matches = re.findall(r'EQUITY.*?(\d\.\d{2})', content, re.IGNORECASE | re.DOTALL)
            if matches:
                return float(matches[0])
            pcr_match = re.search(r'Equity\s+Put/Call\s+Ratio.*?([\d\.]+)', content, re.IGNORECASE | re.DOTALL)
            if pcr_match:
                return float(pcr_match.group(1))
    except:
        pass
    return None

@st.cache_data(ttl=86400, show_spinner=False)
def get_aaii_sentiment():
    """Fetch AAII Investor Sentiment Survey"""
    try:
        bullish = 38.5
        neutral = 31.2
        bearish = 30.3
        return {
            'bullish': bullish,
            'neutral': neutral,
            'bearish': bearish,
            'bull_bear_spread': bullish - bearish,
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'note': 'データソース準備中'
        }
    except:
        return None

# ========== FOMC & FED WATCH ==========
@st.cache_data(ttl=86400, show_spinner=False)
def get_fomc_sep_projections():
    """Fetch FOMC SEP projections from FRED"""
    try:
        sep_series = {
            'ff_rate': 'FEDTARMD',
            'gdp_growth': 'GDPC1CTM',
            'unemployment': 'UNRATECTM',
            'core_pce': 'PCECTPICTM',
        }
        
        projections = {}
        for key, series_id in sep_series.items():
            try:
                data = web.DataReader(series_id, 'fred', 
                                      datetime.datetime.now() - datetime.timedelta(days=730), 
                                      datetime.datetime.now(), 
                                      api_key=FRED_API_KEY)
                if data is not None and len(data) > 0:
                    recent = data.dropna().tail(5)
                    projections[key] = {
                        'series': recent,
                        'latest': recent.iloc[-1].values[0] if len(recent) > 0 else None,
                        'previous': recent.iloc[-2].values[0] if len(recent) > 1 else None,
                        'date': recent.index[-1].strftime('%Y-%m-%d') if len(recent) > 0 else None
                    }
            except:
                projections[key] = None
        
        return projections if projections else None
    except:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_cme_fedwatch():
    """Fetch CME FedWatch probabilities (placeholder)"""
    return {
        'next_meeting': '2026-01-29',
        'current_rate': '4.25-4.50%',
        'probabilities': {
            'cut_50bp': 5.0,
            'cut_25bp': 65.0,
            'hold': 28.0,
            'hike_25bp': 2.0,
        },
        'expected_rate': '4.00-4.25%',
        'note': 'データソース準備中'
    }

# ========== MANUAL H.4.1 DATA ==========
def load_manual_data():
    """Load manual H.4.1 data from CSV file"""
    try:
        if os.path.exists(MANUAL_DATA_FILE):
            df_manual = pd.read_csv(MANUAL_DATA_FILE, index_col=0, parse_dates=True)
            if 'SOMA_Bills' in df_manual.columns:
                return df_manual[['SOMA_Bills']]
            return df_manual
    except:
        pass
    return pd.DataFrame(columns=['SOMA_Bills'])

def save_manual_data(date, soma_bills):
    """Save manual H.4.1 data to CSV file"""
    df_manual = load_manual_data()
    df_manual.loc[date] = [soma_bills]
    df_manual = df_manual.sort_index()
    df_manual.to_csv(MANUAL_DATA_FILE)

def fetch_h41_data():
    """Fetch latest H.4.1 data from FRB website"""
    url = "https://www.federalreserve.gov/releases/h41/current/"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None, None, None, f"HTTP {response.status_code}"
        
        tables = pd.read_html(StringIO(response.text))
        
        report_date = None
        date_patterns = [
            r'Week ended[^>]*>(\w+\s+\d+,\s+\d{4})',
            r'(\w+ \d+, \d{4})',
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, response.text, re.IGNORECASE)
            if date_match:
                try:
                    report_date = pd.to_datetime(date_match.group(1))
                    break
                except:
                    pass
        
        if not report_date:
            report_date = pd.Timestamp.now()
        
        table1 = tables[1] if len(tables) > 1 else None
        soma_bills = None
        total_loans = None
        
        if table1 is not None:
            last_col_idx = table1.shape[1] - 1
            for idx, row in table1.iterrows():
                row_text = str(row.iloc[0]).strip().lower()
                if row_text == 'bills' or (row_text.startswith('bills') and 'note' not in row_text and 'bond' not in row_text):
                    try:
                        soma_bills = float(row.iloc[last_col_idx]) / 1000
                        break
                    except:
                        pass
            
            for idx, row in table1.iterrows():
                row_text = str(row.iloc[0]).strip().lower()
                if row_text == 'loans':
                    try:
                        val = row.iloc[last_col_idx]
                        if pd.notna(val) and isinstance(val, (int, float)):
                            total_loans = float(val) / 1000
                            break
                    except:
                        pass
        
        if soma_bills or total_loans:
            return report_date, soma_bills, total_loans, None
        else:
            return None, None, None, "No data extracted from tables"
        
    except Exception as e:
        return None, None, None, str(e)
