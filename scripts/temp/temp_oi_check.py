import requests
import json

r = requests.post('https://api.hyperliquid.xyz/info', json={'type': 'metaAndAssetCtxs'}, timeout=15)
data = r.json()
meta = data[0]
ctx = data[1]
universe = meta.get('universe', [])

print("=" * 60)
print("Hyperliquid DEX - Open Interest Data")
print("=" * 60)

for i in range(min(10, len(ctx))):
    name = universe[i]['name']
    oi = float(ctx[i]['openInterest'])
    price = float(ctx[i]['markPx'])
    oi_usd = oi * price
    funding = float(ctx[i]['funding']) * 100
    
    print(f"\n{name}:")
    print(f"  Open Interest: {oi:,.2f} {name}")
    print(f"  Price: ${price:,.2f}")
    print(f"  OI (USD): ${oi_usd/1e6:,.2f}M")
    print(f"  Funding Rate: {funding:.4f}%")
