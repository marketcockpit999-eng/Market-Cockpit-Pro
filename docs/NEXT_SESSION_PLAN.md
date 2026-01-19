# Implementation Plan - Advanced Market Lab Features

## Overview
前スレ(Gemini)で計画されたが未実装の機能を完成させる。

## 未実装機能一覧

### 1. Lag Correlation Analysis (Feature 4)
- **目的**: 流動性(GLP)が株価/BTCを何日先行しているか判定
- **入力**: `Global_Liquidity_Proxy` vs `BTC` or `SP500`
- **出力**: "Best Lag: X days"
- **実装先**: `pages/11_analysis_lab.py`
- **ロジック**: Cross-correlation analysis

### 2. Regime Detection (Feature 5)
- **目的**: 市場の加速/減速を判定
- **入力**: `Global_Liquidity_Proxy` の変化率
- **出力**: "Chance" (加速) / "Caution" (減速)
- **実装先**: `pages/11_analysis_lab.py`

### 3. Cross-Asset Liquidity Monitor (Feature 7)
- **目的**: 全資産クラスのスプレッド監視
- **対象ETF**: SPY, TLT, GLD, SLV, USO
- **データ**: `yfinance` から `bid`/`ask` 取得
- **出力**: Spread (bps) + 健全性ラベル (Green/Yellow/Red)
- **実装先**: `pages/11_analysis_lab.py`

### 4. CEX/DEX Market Depth (Feature 6)
- **目的**: 仮想通貨の流動性品質比較
- **対象**: BTC (CEX: Binance/Coinbase), WBTC (DEX: Uniswap/Curve)
- **データ**: CoinGecko API
- **実装先**: `pages/04_crypto.py`

### 5. Global Liquidity YoY Growth
- **目的**: Global Liquidity Proxy の前年比チャート
- **実装先**: `pages/02_global_money.py`

---

## API Information

| データ | ソース | 取得方法 |
|--------|--------|----------|
| ETF Bid/Ask | Yahoo Finance | `yf.Ticker("SPY").info['bid']` / `['ask']` |
| CEX Spreads | CoinGecko | `/exchanges/{id}/tickers` |
| DEX Spreads | CoinGecko | `/coins/{id}/tickers` |

---

## Files to Modify

1. `pages/11_analysis_lab.py` - Lag, Regime, Cross-Asset追加
2. `pages/04_crypto.py` - Market Depth追加
3. `pages/02_global_money.py` - YoY Growth追加
4. `utils/data_fetcher.py` - ETF spread取得関数追加(必要なら)

---

## Priority Order
1. Cross-Asset Spreads (最も視覚的インパクト大)
2. Regime Detection (シンプルなロジック)
3. Lag Analysis (統計計算が必要)
4. Market Depth (外部API依存)
5. YoY Growth (簡単)

---

## Start Command
```powershell
# ワークフロー呼び出し
/market-cockpit-pro
```

Then say: "前スレの未実装機能を実装してください。implementation_plan.md を参照。"
