# 📊 Market Cockpit Pro - 監視対象項目一覧

> **Source**: Auto-generated from `utils/indicators.py`  
> **更新日**: 2026-01-19 17:10  
> **⚠️ このファイルは自動生成です。直接編集せず、indicators.pyを修正後にスクリプトを再実行してください。**

---

## 📈 サマリー

| 頻度 | 指標数 |
|------|--------|
| Daily (日次) | 25 |
| Weekly (週次) | 18 |
| Monthly (月次) | 16 |
| Quarterly (四半期) | 12 |
| **合計** | **71** |

---

## ✅ Daily (日次): 25項目

| # | Indicator | Source | ID | Unit | Category | Description |
|---|-----------|--------|-----|------|----------|-------------|
| 1 | `BTC` | YAHOO | BTC-USD | - | crypto | ビットコイン |
| 2 | `Breakeven_10Y` | FRED | T10YIE | % | inflation_expectations | 10年期待インフレ率 |
| 3 | `CP_Spread` | FRED | CPFF | % | financial_stress | CP-FFスプレッド（企業資金ストレス） |
| 4 | `Credit_Spread` | FRED | BAMLH0A0HYM2 | % | rates | ハイイールドスプレッド |
| 5 | `DXY` | YAHOO | DX-Y.NYB | - | fx | ドルインデックス |
| 6 | `EFFR` | FRED | EFFR | % | rates | 実効FF金利 |
| 7 | `ETH` | YAHOO | ETH-USD | - | crypto | イーサリアム |
| 8 | `EURUSD` | YAHOO | EURUSD=X | - | fx | ユーロドル |
| 9 | `FedFundsLower` | FRED | DFEDTAR | % | rates | FF金利下限 |
| 10 | `FedFundsUpper` | FRED | DFEDTARU | % | rates | FF金利上限 |
| 11 | `GBPUSD` | YAHOO | GBPUSD=X | - | fx | ポンドドル (Fiat Health Monitor) |
| 12 | `Gold` | YAHOO | GC=F | - | commodities | 金先物 |
| 13 | `HYG` | YAHOO | HYG | - | credit | ハイイールド債ETF（投機的社債） |
| 14 | `IORB` | FRED | IORB | % | rates | 準備預金付利 |
| 15 | `LQD` | YAHOO | LQD | - | credit | 投資適格社債ETF（IG社債） |
| 16 | `MOVE` | YAHOO | ^MOVE | - | volatility | MOVE債券恐怖指数 |
| 17 | `Oil` | YAHOO | CL=F | - | commodities | WTI原油先物 |
| 18 | `ON_RRP` | FRED | RRPONTSYD | B | fed_liquidity | Overnight Reverse Repo (余剰資金の滞留) |
| 19 | `SOFR` | FRED | SOFR | % | rates | SOFR |
| 20 | `SP500` | YAHOO | ^GSPC | - | equity | S&P 500 |
| 21 | `Silver` | YAHOO | SI=F | - | commodities | 銀先物 |
| 22 | `T10Y2Y` | FRED | T10Y2Y | % | rates | 10年-2年スプレッド（逆イールド） |
| 23 | `USDCNY` | YAHOO | CNY=X | - | fx | ドル人民元 |
| 24 | `USDJPY` | YAHOO | JPY=X | - | fx | ドル円 |
| 25 | `US_TNX` | FRED | DGS10 | % | rates | 米10年国債利回り |
| 26 | `VIX` | YAHOO | ^VIX | - | volatility | VIX恐怖指数 |
| 27 | `Copper` | YAHOO | HG=F | - | commodities | 銅先物（景気先行指標） |
| 28 | `AUDUSD` | YAHOO | AUDUSD=X | - | fx | 豪ドル (Fiat Health Monitor) |
| 29 | `USDCHF` | YAHOO | CHF=X | - | fx | ドルスイスフラン (Fiat Health Monitor) |

---

## ✅ Weekly (週次): 18項目

| # | Indicator | Source | ID | Unit | Category | Description |
|---|-----------|--------|-----|------|----------|-------------|
| 1 | `Bank_Cash` | FRED | CASACBW027SBOG | B | banking_h8 | 銀行の現金保有 |
| 2 | `Bank_Deposits` | FRED | DPSACBW027SBOG | B | banking_h8 | 銀行預金総額 |
| 3 | `Bank_Securities` | FRED | H8B1002NCBCAG | B | banking_h8 | 銀行保有有価証券 |
| 4 | `CRE_Loans` | FRED | CREACBW027SBOG | B | banking_loans | CRE融資残高 |
| 5 | `Credit_Card_Loans` | FRED | CCLACBW027SBOG | B | banking_h8 | クレカ残高 |
| 6 | `ECB_Assets` | FRED | ECBASSETSW | M | central_bank | ECB総資産 (Million EUR) |
| 7 | `FIMA` | FRED | H41RESPPALGTRFNWW | B | fed_plumbing | FIMA Repo Facility |
| 8 | `Fed_Assets` | FRED | WALCL | B | fed_liquidity | FRB総資産 |
| 9 | `Financial_Stress` | FRED | STLFSI4 | - | financial_stress | セントルイス連銀金融ストレス指数 |
| 10 | `ICSA` | FRED | ICSA | K | employment | 新規失業保険申請件数 |
| 11 | `NFCI` | FRED | NFCI | - | financial_stress | シカゴ連銀金融環境指数 |
| 12 | `Primary_Credit` | FRED | WLCFLPCL | B | fed_plumbing | 割引窓口プライマリークレジット |
| 13 | `Reserves` | FRED | WRESBAL | B | fed_liquidity | 銀行準備預金 |
| 14 | `SRF` | FRED | WORAL | B | fed_plumbing | Standing Repo Facility |
| 15 | `SOMA_Bills` | FRED | TREAST | B | fed_liquidity | SOMA短期国債（RMP対象） |
| 16 | `SOMA_Total` | FRED | WALCL | B | fed_liquidity | SOMA総資産 |
| 17 | `SomaBillsRatio` | CALCULATED | SOMA_RATIO | % | fed_liquidity | SOMA短期国債比率 |
| 18 | `Small_Bank_Deposits` | FRED | DPSSCBW027SBOG | B | financial_stress | 地銀預金（取り付け警報） |
| 19 | `TGA` | FRED | WTREGEN | B | fed_liquidity | 財務省一般口座 |
| 20 | `Total_Loans` | FRED | WLCFLL | B | fed_plumbing | FRB貸出総額 |
| 21 | `Global_Liquidity_Proxy` | CALCULATED | GLP_USD | B USD | liquidity | グローバル流動性プロキシ (Fed+ECB-TGA-RRP) |

---

## ✅ Monthly (月次): 16項目

| # | Indicator | Source | ID | Unit | Category | Description |
|---|-----------|--------|-----|------|----------|-------------|
| 1 | `ADP` | FRED | ADPWNUSNERSA | K | employment | ADP雇用統計 |
| 2 | `AvgHourlyEarnings` | FRED | CES0500000003 | $/hr | employment | 平均時給 |
| 3 | `CI_Loans` | FRED | BUSLOANS | B | banking_loans | C&I融資残高 |
| 4 | `Consumer_Loans` | FRED | CLSACBW027NBOG | B | banking_h8 | 消費者ローン残高 |
| 5 | `ConsumerSent` | FRED | UMCSENT | idx | sentiment | ミシガン消費者信頼感 |
| 6 | `CPI` | FRED | CPIAUCSL | idx | inflation | 消費者物価指数 |
| 7 | `CPICore` | FRED | CPILFESL | idx | inflation | コアCPI |
| 8 | `CorePCE` | FRED | PCETRIM12M159SFRBDAL | % | inflation | コアPCE（Fedの最重視指標） |
| 9 | `JOLTS` | FRED | JTSJOL | K | employment | JOLTS求人数 |
| 10 | `M2REAL` | FRED | M2REAL | T | money_supply | 米実質M2 |
| 11 | `M2SL` | FRED | M2SL | T | money_supply | 米M2 |
| 12 | `NFP` | FRED | PAYEMS | K | employment | 非農業部門雇用者数 |
| 13 | `NIKKEI` | YAHOO | ^N225 | - | equity | 日経225 |
| 14 | `PPI` | FRED | PPIACO | idx | inflation | 生産者物価指数 |
| 15 | `RetailSales` | FRED | RSAFS | B | consumption | 小売売上高 |
| 16 | `UNRATE` | FRED | UNRATE | % | employment | 失業率（別名） |
| 17 | `INDPRO` | FRED | INDPRO | idx | manufacturing | 工業生産指数 (2017=100) |
| 18 | `NEWORDER` | FRED | NEWORDER | B | manufacturing | 製造業新規受注 (SAAR) |

---

## ✅ Quarterly (四半期): 12項目

| # | Indicator | Source | ID | Unit | Category | Description |
|---|-----------|--------|-----|------|----------|-------------|
| 1 | `CC_Delinquency` | FRED | DRCCLACBS | % | financial_stress | クレカ延滞率 |
| 2 | `CI_Demand` | FRED | DRSDCILM | pts | banking_sloos | C&I融資需要 |
| 3 | `CI_Std_Large` | FRED | DRTSCILM | pts | banking_sloos | C&I基準（大企業） |
| 4 | `CI_Std_Small` | FRED | DRTSCIS | pts | banking_sloos | C&I基準（小企業） |
| 5 | `CRE_Demand` | FRED | SUBLPDRCDN | pts | banking_sloos | CRE融資需要 |
| 6 | `CRE_Std_Construction` | FRED | SUBLPDRCSC | pts | banking_sloos | CRE基準（建設） |
| 7 | `CRE_Std_Multifamily` | FRED | SUBLPDRCSM | pts | banking_sloos | CRE基準（集合住宅） |
| 8 | `CRE_Std_Office` | FRED | SUBLPDRCSN | pts | banking_sloos | CRE基準（オフィス） |
| 9 | `M2_Velocity` | FRED | M2V | - | economy | M2通貨回転率（インフレ・景気過熱） |
| 10 | `RealGDP` | FRED | GDPC1 | B | gdp | 実質GDP |

---

## 📚 データソース

| Source | Description |
|--------|-------------|
| FRED | Federal Reserve Economic Data (セントルイス連銀) |
| YAHOO | Yahoo Finance (yfinance経由) |
| CALCULATED | 他の指標から計算される派生値 |

---

## 🔧 メンテナンス

### 指標の追加・修正方法

1. `utils/indicators.py` の `INDICATORS` ディクショナリを編集
2. 以下のコマンドでこのドキュメントを再生成:
   ```bash
   python scripts/generate_monitored_items.py
   ```
3. `git commit` で変更をコミット

### 必須フィールド

```python
'INDICATOR_NAME': {
    'source': 'FRED',        # FRED, YAHOO, CALCULATED
    'id': 'SERIES_ID',       # FRED series ID or Yahoo ticker
    'unit': '%',             # Display unit
    'frequency': 'daily',    # daily, weekly, monthly, quarterly
    'freshness': 'daily',    # For staleness monitoring
    'category': 'rates',     # Grouping category
    'ui_page': '01_liquidity', # Which page displays this
    'ai_include': True,      # Include in AI analysis?
    'ai_section': '金利',    # AI summary section name
    'notes': 'Description',  # Human-readable description
}
```

---

## 🔍 SLOOS指標の正しいFRED ID（参考）

| カテゴリ | 指標 | FRED ID | 説明 |
|----------|------|---------|------|
| **C&I Standards** | Large/Mid Firms | DRTSCILM | 大企業向け融資基準 |
| | Small Firms | DRTSCIS | 中小企業向け融資基準 |
| **C&I Demand** | Large/Mid Firms | DRSDCILM | 大企業向け融資需要 |
| **CRE Standards** | Construction & Land | SUBLPDRCSC | 建設・土地開発 |
| | Nonfarm Nonresidential | SUBLPDRCSN | オフィス等 |
| | Multifamily | SUBLPDRCSM | 集合住宅 |
| **CRE Demand** | Nonfarm Nonresidential | SUBLPDRCDN | オフィス等需要 |
