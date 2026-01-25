# 88項目 表示パターン分類

## 概要

Market Cockpit Pro の88項目の表示パターンを分類し、標準パターンと例外パターンを明確化する。

**目的:** 場当たり的な対応を防ぎ、新規指標追加時の一貫性を確保する。

---

## 標準8要素パターン

`show_metric_with_sparkline()` を使用する標準パターン:

| # | 要素 | 実装 |
|---|------|------|
| 1 | 監視名 | `label` パラメータ |
| 2 | ？補足説明 | `help` テキスト（HELP_EN/HELP_JA） |
| 3 | データ数字 | 最新値 + delta（前回比） |
| 4 | 📅 データ期間 | `df.attrs['last_valid_dates']` |
| 5 | 🔄 提供元更新日 | `df.attrs['fred_release_dates']` |
| 6 | 簡潔な一言補足 | `notes` パラメータ |
| 7 | 📊 60日推移 | スパークライン（自動） |
| 8 | 長期トレンド | `styled_line_chart()` |

---

## パターン分類

### A. 標準パターン（67項目）

`show_metric_with_sparkline` を使用し、8要素全てを表示。

#### A-1. Fed流動性 (11項目) - Page 01
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| ON_RRP | FRED | daily |
| Reserves | FRED | weekly |
| TGA | FRED | weekly |
| Fed_Assets | FRED | weekly |
| SOMA_Total | FRED | weekly |
| SOMA_Treasury | FRED | weekly |
| SOMA_Bills | FRED | weekly |
| SRF | FRED | weekly |
| FIMA | FRED | weekly |
| Primary_Credit | FRED | weekly |
| Total_Loans | FRED | weekly |

#### A-2. 金利 (8項目) - Page 01
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| EFFR | FRED | daily |
| IORB | FRED | daily |
| SOFR | FRED | daily |
| FedFundsUpper | FRED | daily |
| FedFundsLower | FRED | daily |
| US_TNX | FRED | daily |
| T10Y2Y | FRED | daily |
| Credit_Spread | FRED | daily |

#### A-3. 通貨供給 (2項目) - Page 02
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| M2SL | FRED | monthly |
| M2REAL | FRED | monthly |

#### A-4. 為替 (7項目) - Page 02
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| DXY | YAHOO | daily |
| USDJPY | YAHOO | daily |
| EURUSD | YAHOO | daily |
| USDCNY | YAHOO | daily |
| GBPUSD | YAHOO | daily |
| USDCHF | YAHOO | daily |
| AUDUSD | YAHOO | daily |

#### A-5. コモディティ (4項目) - Page 02
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| Gold | YAHOO | daily |
| Silver | YAHOO | daily |
| Oil | YAHOO | daily |
| Copper | YAHOO | daily |

#### A-6. 株式指数 (3項目) - Page 01/02
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| SP500 | YAHOO | daily |
| VIX | YAHOO | daily |
| NIKKEI | YAHOO | daily |

#### A-7. 暗号通貨 (2項目) - Page 02
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| BTC | YAHOO | daily |
| ETH | YAHOO | daily |

#### A-8. 社債 (2項目) - Page 01/11
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| HYG | YAHOO | daily |
| LQD | YAHOO | daily |

#### A-9. 雇用 (3項目) - Page 03
| 項目名 | ソース | 頻度 | 備考 |
|--------|--------|------|------|
| JOLTS | FRED | monthly | 標準パターン |
| Housing_Starts | FRED | monthly | 標準パターン |
| Building_Permits | FRED | monthly | 標準パターン |

#### A-10. 地域連銀 - 製造業 (3項目) - Page 03
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| Empire_State_Mfg | FRED | monthly |
| Philly_Fed_Mfg | FRED | monthly |
| Dallas_Fed_Mfg | FRED | monthly |

#### A-11. 地域連銀 - サービス業 (3項目) - Page 03
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| Philly_Fed_Services | FRED | monthly |
| Dallas_Fed_Services | FRED | monthly |
| NY_Fed_Services | FRED | monthly |

#### A-12. 景気先行 (1項目) - Page 03
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| Leading_Index | FRED | monthly |

#### A-13. 銀行H.8 (7項目) - Page 09
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| Bank_Cash | FRED | weekly |
| CI_Loans | FRED | monthly |
| CRE_Loans | FRED | weekly |
| Credit_Card_Loans | FRED | weekly |
| Consumer_Loans | FRED | monthly |
| Bank_Securities | FRED | weekly |
| Bank_Deposits | FRED | weekly |

#### A-14. 銀行SLOOS (8項目) - Page 09
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| CI_Std_Large | FRED | quarterly |
| CI_Std_Small | FRED | quarterly |
| CI_Demand | FRED | quarterly |
| CRE_Std_Construction | FRED | quarterly |
| CRE_Std_Office | FRED | quarterly |
| CRE_Std_Multifamily | FRED | quarterly |
| CRE_Demand | FRED | quarterly |

#### A-15. 金融ストレス (6項目) - Page 09
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| Small_Bank_Deposits | FRED | weekly |
| CC_Delinquency | FRED | quarterly |
| CP_Spread | FRED | daily |
| NFCI | FRED | weekly |
| Breakeven_10Y | FRED | daily |
| MOVE | YAHOO | daily |

#### A-16. その他 (3項目) - Page 10
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| M2_Velocity | FRED | quarterly |
| Financial_Stress | FRED | weekly |
| ECB_Assets | FRED | weekly |

#### A-17. インフレ期待 (1項目) - Page 03
| 項目名 | ソース | 頻度 |
|--------|--------|------|
| Michigan_Inflation_Exp | FRED | monthly |

---

### B. MoM/YoY計算パターン（6項目）

`display_macro_card()` を使用。前月比・前年比を自動計算。

| 項目名 | ソース | 頻度 | ページ |
|--------|--------|------|--------|
| CPI | FRED | monthly | 03 |
| CPICore | FRED | monthly | 03 |
| CorePCE | FRED | monthly | 03 |
| PPI | FRED | monthly | 03 |
| RetailSales | FRED | monthly | 03 |
| ConsumerSent | FRED | monthly | 03 |

**表示要素:**
- MoM%, YoY% 自動計算
- 60日スパークライン
- 長期チャート
- 日付情報

---

### C. 手動計算パターン（6項目）

個別にロジックを実装。`st.metric` 直接使用。

| 項目名 | 計算内容 | ページ |
|--------|----------|--------|
| NFP | 前月差（雇用者増減数） | 03 |
| UNRATE | 前月差（失業率変化） | 03 |
| AvgHourlyEarnings | MoM%, YoY% | 03 |
| ICSA | 前週差（失業保険） | 03 |
| RealGDP | QoQ年率換算 | 03 |
| EFFR-IORB | 差分計算（bps） | 01 |

**特徴:**
- 計算ロジックがページ内にハードコード
- 日付情報は `show_date_info()` で手動表示
- スパークラインは手動描画

---

### D. Webスクレイピングパターン（2項目）

外部関数から取得。FREDにないデータ。

| 項目名 | ソース | 頻度 | ページ |
|--------|--------|------|--------|
| Richmond_Fed_Mfg | WEB | monthly | 03 |
| Richmond_Fed_Services | WEB | monthly | 03 |

**表示要素:**
- `st.metric` 直接使用
- 手動で日付情報表示
- 履歴データがあればチャート表示
- フォールバック: `st.info(t('data_fetch_failed'))`

---

### E. 計算項目パターン（2項目）

複数指標から算出。

| 項目名 | 計算式 | ページ |
|--------|--------|--------|
| Net_Liquidity | Fed_Assets - TGA - ON_RRP | 01 |
| Global_Liquidity_Proxy | Fed + ECB - TGA - RRP | 10 |

**注意:**
- `Net_Liquidity` は `show_metric_with_sparkline` 使用可能
- `Global_Liquidity_Proxy` は indicators.py で定義済み

---

### F. 外部APIパターン（7項目）

04_crypto.py で使用。DeFiLlama, CoinGecko等から取得。

| 項目名 | API | 表示形式 |
|--------|-----|----------|
| Stablecoin Total | DeFiLlama | st.metric + テーブル + チャート |
| USDT Supply | DeFiLlama | st.metric |
| USDC Supply | DeFiLlama | st.metric |
| Tokenized Treasury TVL | DeFiLlama | st.metric + テーブル |
| Tokenized Gold TVL | DeFiLlama | st.metric + テーブル |
| Other RWA TVL | DeFiLlama | st.metric + テーブル |
| Market Depth | CoinGecko | st.metric + チャート |

**注意:** これらは indicators.py の88項目には含まれない

---

### G. 特殊計算比率（1項目）

Page 09 のみで使用。

| 項目名 | 計算式 | ページ |
|--------|--------|--------|
| Copper/Gold Ratio | (Copper/Gold) * 1000 | 09 |

**特徴:**
- 手動でスパークライン描画
- 手動で日付情報表示
- 独自のキャプション

---

### H. 01_liquidity専用（4項目）

外部関数から取得。バリュエーション・レバレッジ。

| 項目名 | ソース | 表示形式 |
|--------|--------|----------|
| SP500_PE | get_pe_ratios() | st.metric |
| NASDAQ_PE | get_pe_ratios() | st.metric |
| BTC_Funding_Rate | get_crypto_leverage_data() | st.metric |
| BTC_Long_Short_Ratio | get_crypto_leverage_data() | st.metric |
| BTC_Open_Interest | get_crypto_leverage_data() | st.metric + caption |
| ETH_Open_Interest | get_crypto_leverage_data() | st.metric + caption |

**注意:** これらは indicators.py の88項目には含まれない

---

## 集計

### indicators.py の88項目（ソース別）

| ソース | 項目数 |
|--------|--------|
| FRED | 66 |
| YAHOO | 19 |
| WEB | 2 |
| CALCULATED | 1 |
| **合計** | **88** |

### 表示パターン別（88項目の内訳）

| パターン | 項目数 | 項目例 |
|----------|--------|--------|
| A. 標準パターン | 72 | ON_RRP, DXY, BTC, JOLTS, etc. |
| B. MoM/YoY計算 | 6 | CPI, CPICore, PPI, CorePCE, RetailSales, ConsumerSent |
| C. 手動計算 | 6 | NFP, UNRATE, AvgHourlyEarnings, ICSA, RealGDP, ADP |
| D. Webスクレイピング | 2 | Richmond_Fed_Mfg, Richmond_Fed_Services |
| E. 計算項目 | 1 | Global_Liquidity_Proxy |
| F. 派生計算（df内） | 1 | Net_Liquidity（indicators.py外、df内で計算）|
| **合計** | **88** | |

### indicators.py 外（UI専用）

| パターン | 項目数 | 項目例 | 備考 |
|----------|--------|--------|------|
| 外部API | ~7 | Stablecoin, RWA TVL | 04_crypto.py |
| P/E比率 | 2 | SP500_PE, NASDAQ_PE | 01_liquidity.py |
| Leverage指標 | 4 | Funding Rate, OI | 01_liquidity.py |
| 計算比率 | 2 | EFFR-IORB, Cu/Au | 01/09 |
| - | - | これらは88項目には含まれない | - |

---

## 新規指標追加時のガイドライン

### 1. 標準パターン（推奨）

```python
# indicators.pyに追加後、ページで以下を使用:
show_metric_with_sparkline(
    label=t('indicator_title'),
    series=df.get('INDICATOR_NAME'),
    column_name='INDICATOR_NAME',
    unit="単位",
    explanation_key="INDICATOR_NAME",
    notes=t('indicator_notes')
)
if 'INDICATOR_NAME' in df.columns:
    styled_line_chart(df[['INDICATOR_NAME']], height=200)
```

### 2. MoM/YoY計算が必要な場合

```python
display_macro_card(
    label=t('indicator_title'),
    series=df.get('INDICATOR_NAME'),
    column_name='INDICATOR_NAME',
    df_original=df_original,
    notes=t('indicator_notes')
)
```

### 3. Webスクレイピングの場合

1. `utils/data_fetcher.py` にスクレイピング関数を追加
2. ページで関数を呼び出し、手動で表示
3. フォールバック処理を必ず実装

### 4. 計算項目の場合

1. `indicators.py` に `source: 'CALCULATED'` で定義
2. `utils/data_fetcher.py` で計算ロジックを実装
3. 表示は標準パターンを使用可能

---

## 注意事項

1. **一貫性の維持**: 新規追加は可能な限り標準パターンを使用
2. **例外の明文化**: 例外パターンを使用する場合は、このドキュメントを更新
3. **テスト**: 新規追加後は必ず Update Status と AI Analysis で確認
