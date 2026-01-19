# Data Connection Audit Script
import requests
import json

print("=" * 60)
print("Market Cockpit Pro - Data Connection Audit")
print("=" * 60)

# 1. Hyperliquid DEX - BTC/ETH Open Interest
print("\n[1] Hyperliquid DEX - Open Interest")
try:
    r = requests.post('https://api.hyperliquid.xyz/info', 
                      json={'type': 'metaAndAssetCtxs'}, timeout=15)
    data = r.json()
    meta = data[0]
    ctx = data[1]
    universe = meta.get('universe', [])
    
    # Find BTC (first asset)
    btc_ctx = ctx[0]
    btc_oi = float(btc_ctx.get('openInterest', 0))
    btc_funding = float(btc_ctx.get('funding', 0)) * 100
    btc_price = float(btc_ctx.get('markPx', 0))
    
    print(f"  BTC OI: {btc_oi:,.0f} BTC")
    print(f"  BTC Funding: {btc_funding:.4f}%")
    print(f"  BTC Price: ${btc_price:,.0f}")
    
    # Find ETH
    for i, asset in enumerate(universe):
        if asset.get('name', '').upper() == 'ETH':
            eth_ctx = ctx[i]
            eth_oi = float(eth_ctx.get('openInterest', 0))
            eth_funding = float(eth_ctx.get('funding', 0)) * 100
            print(f"  ETH OI: {eth_oi:,.0f} ETH")
            print(f"  ETH Funding: {eth_funding:.4f}%")
            break
except Exception as e:
    print(f"  ERROR: {e}")

# 2. CoinMarketCap - Funding Rate
print("\n[2] CoinMarketCap - Derivatives")
try:
    url = "https://api.coinmarketcap.com/data-api/v3/exchange/market-pairs/latest?slug=binance&category=perpetual"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()
    pairs = data.get('data', {}).get('marketPairs', [])
    
    for pair in pairs[:5]:
        if 'BTC' in pair.get('marketPair', ''):
            funding = pair.get('fundingRate')
            oi_usd = pair.get('openInterestUsd')
            print(f"  {pair.get('marketPair')}: Funding={funding}, OI=${oi_usd/1e9:.2f}B" if oi_usd else f"  {pair.get('marketPair')}: Funding={funding}")
            break
except Exception as e:
    print(f"  ERROR: {e}")

# 3. CoinGecko - L/S Ratio
print("\n[3] CoinGecko - Derivatives")
try:
    url = "https://api.coingecko.com/api/v3/derivatives"
    r = requests.get(url, timeout=10)
    data = r.json()
    
    for contract in data[:3]:
        if 'BTC' in contract.get('symbol', ''):
            funding = contract.get('funding_rate')
            print(f"  {contract.get('symbol')}: Funding={funding}")
            break
except Exception as e:
    print(f"  ERROR: {e}")

# 4. P/E Ratio - multpl.com
print("\n[4] S&P 500 P/E - multpl.com")
try:
    import re
    url = "https://www.multpl.com/s-p-500-pe-ratio"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    match = re.search(r'Current S&P 500 PE Ratio is\s*([\d.]+)', r.text)
    if match:
        print(f"  S&P 500 P/E: {match.group(1)}")
    else:
        print("  P/E not found in page")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("Audit Complete")
