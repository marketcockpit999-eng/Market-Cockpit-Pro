#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Scheduled Data Update Script
================================================================================
This script is designed to be run by Windows Task Scheduler to pre-fetch
market data before users access the dashboard.

Usage:
    python scripts/update_data.py              # Normal update
    python scripts/update_data.py --force      # Force refresh all data
    python scripts/update_data.py --verbose    # Verbose output
    python scripts/update_data.py --log        # Write to log file

Scheduling (Windows Task Scheduler):
    - Run every 10 minutes during market hours (9:00-17:00 ET)
    - Run every 30 minutes outside market hours
    
See: scripts/setup_scheduled_task.bat
================================================================================
"""

import sys
import os
import argparse
import logging
from datetime import datetime
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'data_update.log')


def setup_logging(to_file=False, verbose=False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    
    handlers = [logging.StreamHandler()]
    
    if to_file:
        os.makedirs(LOG_DIR, exist_ok=True)
        handlers.append(logging.FileHandler(LOG_FILE, encoding='utf-8'))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )


def clear_caches():
    """Clear all cache layers"""
    # 1. Delete disk cache
    cache_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '.market_data_cache.pkl'
    )
    if os.path.exists(cache_file):
        os.remove(cache_file)
        logging.info("Deleted disk cache")
    
    # 2. Clear pycache
    pycache_dirs = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils', '__pycache__'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pages', '__pycache__'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '__pycache__'),
    ]
    
    for pycache in pycache_dirs:
        if os.path.exists(pycache):
            import shutil
            shutil.rmtree(pycache)
            logging.debug(f"Deleted {pycache}")


def update_market_data(force=False):
    """Fetch fresh market data"""
    from utils.data_fetcher import get_market_data
    from utils.indicators import INDICATORS, get_fred_indicators, get_yahoo_indicators
    
    logging.info("=" * 60)
    logging.info("Starting market data update")
    logging.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Force refresh: {force}")
    logging.info("=" * 60)
    
    # Get indicator counts
    fred_count = len(get_fred_indicators())
    yahoo_count = len(get_yahoo_indicators())
    logging.info(f"Expected indicators: {fred_count} FRED + {yahoo_count} Yahoo = {fred_count + yahoo_count} total")
    
    # Fetch data
    start_time = datetime.now()
    
    try:
        df, df_original = get_market_data(_force_refresh=force)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logging.info(f"Data fetch completed in {elapsed:.1f} seconds")
        
        # Validate results
        columns = len(df.columns)
        rows = len(df)
        date_range = f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}"
        
        logging.info(f"Result: {columns} columns, {rows} rows")
        logging.info(f"Date range: {date_range}")
        
        # Check for missing indicators
        all_indicators = list(get_fred_indicators().keys()) + list(get_yahoo_indicators().keys())
        missing = [ind for ind in all_indicators if ind not in df.columns]
        all_nan = [ind for ind in all_indicators if ind in df.columns and df[ind].isna().all()]
        
        if missing:
            logging.warning(f"Missing indicators: {missing}")
        if all_nan:
            logging.warning(f"All-NaN indicators: {all_nan}")
        
        # Summary
        ok_count = len(all_indicators) - len(missing) - len(all_nan)
        logging.info(f"Summary: {ok_count} OK, {len(all_nan)} NaN, {len(missing)} missing")
        
        return True, {
            'columns': columns,
            'rows': rows,
            'elapsed': elapsed,
            'missing': missing,
            'all_nan': all_nan,
        }
        
    except Exception as e:
        logging.error(f"Data fetch failed: {e}")
        logging.error(traceback.format_exc())
        return False, {'error': str(e)}


def update_crypto_data():
    """Fetch crypto-specific data"""
    logging.info("Fetching crypto data...")
    
    try:
        from utils.data_fetcher import (
            get_crypto_leverage_data,
            get_stablecoin_data,
            get_crypto_fear_greed,
        )
        
        # Crypto leverage
        leverage_data = get_crypto_leverage_data()
        if leverage_data:
            logging.info(f"  Crypto leverage: {len(leverage_data)} protocols")
        
        # Stablecoin data
        stablecoin_data = get_stablecoin_data()
        if stablecoin_data:
            logging.info(f"  Stablecoins: {len(stablecoin_data)} coins")
        
        # Fear & Greed
        fg_data = get_crypto_fear_greed()
        if fg_data:
            logging.info(f"  Crypto Fear & Greed: {fg_data.get('value', 'N/A')}")
        
        return True
        
    except Exception as e:
        logging.warning(f"Crypto data fetch failed: {e}")
        return False


def update_sentiment_data():
    """Fetch sentiment data"""
    logging.info("Fetching sentiment data...")
    
    try:
        from utils.data_fetcher import (
            get_cnn_fear_greed,
            get_put_call_ratio,
            get_aaii_sentiment,
        )
        
        # CNN Fear & Greed
        cnn_fg = get_cnn_fear_greed()
        if cnn_fg:
            logging.info(f"  CNN Fear & Greed: {cnn_fg.get('score', 'N/A')}")
        
        # Put/Call ratio
        pc_ratio = get_put_call_ratio()
        if pc_ratio:
            logging.info(f"  Put/Call ratio: {pc_ratio}")
        
        # AAII sentiment
        aaii = get_aaii_sentiment()
        if aaii:
            logging.info(f"  AAII: Bull {aaii.get('bullish', 'N/A')}%, Bear {aaii.get('bearish', 'N/A')}%")
        
        return True
        
    except Exception as e:
        logging.warning(f"Sentiment data fetch failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Market Cockpit Pro - Data Update')
    parser.add_argument('--force', '-f', action='store_true', help='Force refresh all data')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--log', '-l', action='store_true', help='Write to log file')
    parser.add_argument('--clear-cache', '-c', action='store_true', help='Clear caches before update')
    parser.add_argument('--market-only', '-m', action='store_true', help='Only update market data (skip crypto/sentiment)')
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(to_file=args.log, verbose=args.verbose)
    
    # Clear caches if requested
    if args.clear_cache or args.force:
        clear_caches()
    
    # Update market data
    success, result = update_market_data(force=args.force)
    
    if not success:
        logging.error("Market data update FAILED")
        return 1
    
    # Update additional data (unless market-only)
    if not args.market_only:
        update_crypto_data()
        update_sentiment_data()
    
    logging.info("=" * 60)
    logging.info("Data update completed successfully")
    logging.info("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
