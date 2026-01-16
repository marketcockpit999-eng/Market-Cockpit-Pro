# 📊 Market Cockpit Pro - 監視対象66項目一覧

> **Version**: v2.0.0 Modular Edition  
> **更新日**: 2026-01-14  
> **目的**: このファイルは監視対象の正規リストです。機能追加・修正時は必ず参照してください。

---

## ✅ Daily (日次): 22項目
| # | Indicator | FRED/Yahoo | 説明 |
|---|-----------|------------|------|
| 1 | `EFFR` | EFFR | 実効FF金利 |
| 2 | `IORB` | IORB | 準備預金付利 |
| 3 | `SOFR` | SOFR | 担保付翌日物金利 |
| 4 | `SP500` | ^GSPC | S&P 500 |
| 5 | `VIX` | ^VIX | 恐怖指数 |
| 6 | `HYG` | HYG | ハイイールド債ETF |
| 7 | `DXY` | DX-Y.NYB | ドル指数 |
| 8 | `USDJPY` | JPY=X | ドル円 |
| 9 | `EURUSD` | EURUSD=X | ユーロドル |
| 10 | `USDCNY` | CNY=X | ドル人民元 |
| 11 | `Gold` | GC=F | 金先物 |
| 12 | `Silver` | SI=F | 銀先物 |
| 13 | `Oil` | CL=F | WTI原油 |
| 14 | `Copper` | HG=F | 銅先物 |
| 15 | `BTC` | BTC-USD | ビットコイン |
| 16 | `ETH` | ETH-USD | イーサリアム |
| 17 | `Credit_Spread` | BAMLH0A0HYM2 | ハイイールドスプレッド |
| 18 | `US_TNX` | DGS10 | 10年国債利回り |
| 19 | `T10Y2Y` | T10Y2Y | イールドカーブ |
| 20 | `ON_RRP` | RRPONTSYD | ON RRP |
| 21 | `FedFundsUpper` | DFEDTARU | FF金利上限 |
| 22 | `FedFundsLower` | DFEDTAR | FF金利下限 |
| 23 | `USD_EUR` | DEXUSEU | ドル/ユーロレート |
| 24 | `Global_Liquidity_Proxy` | (計算値) | 世界流動性 (Fed+ECB) |
| 25 | `Asset_Spreads` | Yahoo | 流動性監視 (SPY, TLT, GLD, SLV, USO) |

---

## ✅ Weekly (週次): 14項目
| # | Indicator | FRED | 説明 |
|---|-----------|------|------|
| 1 | `Reserves` | WRESBAL | 銀行準備預金 |
| 2 | `TGA` | WTREGEN | 財務省一般口座 |
| 3 | `Fed_Assets` | WALCL | FRB総資産 |
| 4 | `SOMA_Total` | WALCL | SOMA総資産 |
| 5 | `SOMA_Bills` | TREAST | SOMA短期国債 |
| 6 | `SRF` | WORAL | Standing Repo Facility |
| 7 | `FIMA` | H41RESPPALGTRFNWW | FIMA Repo |
| 8 | `Primary_Credit` | WLCFLPCL | 緊急融資 (一次) |
| 9 | `Total_Loans` | WLCFLL | 緊急融資 (合計) |
| 10 | `Bank_Cash` | CASACBW027SBOG | 銀行現金保有 |
| 11 | `ICSA` | ICSA | 新規失業保険申請 |
| 12 | `Net_Liquidity` | (計算値) | ネットリクイディティ |
| 13 | `SomaBillsRatio` | (計算値) | Bills比率 |
| 14 | `CRE_Loans` | CREACBW027SBOG | CRE融資残高 |
| 15 | `Financial_Stress` | STLFSI4 | 金融ストレス指数 |
| 16 | `ECB_Assets` | ECBASSETSW | ECB総資産 |

---

## ✅ Monthly (月次): 22項目
| # | Indicator | FRED/Manual | 説明 |
|---|-----------|-------------|------|
| 1 | `M2SL` | M2SL | 米国M2 (名目) |
| 2 | `M2REAL` | M2REAL | 米国M2 (実質) |
| 3 | `CPI` | CPIAUCSL | 消費者物価指数 |
| 4 | `CPICore` | CPILFESL | コアCPI |
| 5 | `PPI` | PPIACO | 生産者物価指数 |
| 6 | `Unemployment` | UNRATE | 失業率 |
| 7 | `UNRATE` | UNRATE | 失業率 (Sahm Rule) |
| 8 | `CorePCE` | PCETRIM12M159SFRBDAL | コアPCE |
| 9 | `ConsumerSent` | UMCSENT | 消費者信頼感 |
| 10 | `CN_M2` | Manual (PBoC) | 中国M2 |
| 11 | `JP_M2` | Manual (BOJ) | 日本M2 |
| 12 | `EU_M2` | Manual (ECB) | 欧州M2 |
| 13 | `NFP` | PAYEMS | 非農業部門雇用者数 |
| 14 | `ADP` | ADPWNUSNERSA | ADP雇用統計 |
| 15 | `AvgHourlyEarnings` | CES0500000003 | 平均時給 |
| 16 | `JOLTS` | JTSJOL | 求人数 |
| 17 | `RetailSales` | RSAFS | 小売売上 |
| 18 | `CN_CPI` | CHNCPIALLMINMEI / Manual | 中国CPI |
| 19 | `JP_CPI` | Manual (BOJ) | 日本CPI |
| 20 | `EU_CPI` | CP0000EZ19M086NEST | 欧州CPI |
| 21 | `US_Real_M2_Index` | (計算値) | 米国実質M2指数 |
| 22 | `CI_Loans` | BUSLOANS | C&I融資残高 |

---

## ✅ Quarterly (四半期): 9項目
| # | Indicator | FRED | 説明 |
|---|-----------|------|------|
| 1 | `Lending_Standards` | DRTSCILM | 融資態度 (総合) |
| 2 | `CI_Std_Large` | DRTSCILM | C&I融資基準 (大企業) |
| 3 | `CI_Std_Small` | DRTSCIS | C&I融資基準 (中小) |
| 4 | `CI_Demand` | DRTSCLCC | C&I融資需要 |
| 5 | `CRE_Std_Construction` | SUBLPDRCSC | CRE融資基準 (建設) |
| 6 | `CRE_Std_Office` | DRTSSP | CRE融資基準 (オフィス) |
| 7 | `CRE_Std_Multifamily` | DRTSSP | CRE融資基準 (集合住宅) |
| 8 | `CRE_Demand` | DRTSCLCC | CRE融資需要 |
| 9 | `RealGDP` | GDPC1 | 実質GDP |
| 10 | `M2_Velocity` | M2V | M2回転速度 |

---

## ⚠️ 注意事項

1. **手動更新が必要な項目**: `CN_M2`, `JP_M2`, `EU_M2`, `JP_CPI` は FRED では最新データが遅延するため、`utils/config.py` の `MANUAL_GLOBAL_M2` で手動更新が必要
2. **計算値**: `Net_Liquidity`, `SomaBillsRatio`, `US_Real_M2_Index` は他の項目から計算される派生指標
3. **監視ルールの定義場所**: `utils/constants.py` の `DATA_FRESHNESS_RULES`
4. **修正時の注意**: `constants.py` と `config.py` の両方に `DATA_FRESHNESS_RULES` が存在するため、同期を維持すること

---

**Total: 73 items** (25 Daily + 16 Weekly + 22 Monthly + 10 Quarterly)
