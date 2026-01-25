# 表示仕様書（DISPLAY_SPEC.md）

> **「本」= 各指標のあるべき姿の定義**
> 
> この仕様書が「焼肉定食のレシピ」。
> すべての表示はこの仕様に従う。

---

## 📋 標準9要素（Standard 9 Elements）

すべての指標が持つべき基本要素：

| # | 要素名 | 英語キー | 必須 | 説明 | 例 |
|---|--------|----------|------|------|-----|
| 1 | 監視名 | `label` | ◎ | 指標の識別名 | `SRF` |
| 2 | ？の補足説明 | `help_text` | ◎ | 初心者向けの詳しい説明 | `Standing Repo Facilityは...` |
| 3 | データの数字 | `value` | ◎ | 現在値（単位付き） | `0.0 B` |
| 4 | 差分（delta） | `delta` | ○ | 前回からの変化 | `+2.1` |
| 5 | 📅 データ期間 | `data_period` | ◎ | いつのデータか | `2025-11-01 (月次)` |
| 6 | 🔄 提供元更新日 | `release_date` | ◎ | 最新性の確認 | `2025-12-23` |
| 7 | 簡潔な一言補足 | `notes` | ○ | 一言で何か | `Standing Repo Facility` |
| 8 | 📊 60日推移 | `sparkline` | ○ | 短期トレンド | ミニチャート |
| 9 | 長期トレンド | `full_chart` | ○ | 長期チャート | フルサイズチャート |

**凡例**: ◎=必須（欠けたらエラー）、○=推奨（欠けたら警告）

---

## 🍖 表示パターン定義

### 1. standard（標準パターン）- 77件

**対象**: 大多数の指標（FRED、Yahoo Finance等）

```yaml
pattern: standard
elements:
  - label        # 必須
  - help_text    # 必須
  - value        # 必須
  - delta        # 推奨
  - data_period  # 必須
  - release_date # 必須
  - notes        # 推奨
  - sparkline    # 推奨
  - full_chart   # 推奨
```

**対象指標**:
- FRB流動性: ON_RRP, Reserves, TGA, Fed_Assets, SOMA_Total, SOMA_Treasury, SOMA_Bills, SRF, FIMA, Primary_Credit, Total_Loans
- 金利: EFFR, IORB, SOFR, FedFundsUpper, FedFundsLower, US_TNX, T10Y2Y, Credit_Spread
- 通貨供給: M2SL, M2REAL
- 製造業: Empire_State_Mfg, Philly_Fed_Mfg, Dallas_Fed_Mfg, Philly_Fed_Services, Dallas_Fed_Services, NY_Fed_Services
- 住宅: Housing_Starts, Building_Permits
- 雇用: JOLTS
- 銀行: Bank_Cash, CI_Loans, CRE_Loans, CI_Std_Large, CI_Std_Small, CI_Demand, CRE_Std_Construction, CRE_Std_Office, CRE_Std_Multifamily, CRE_Demand, Credit_Card_Loans, Consumer_Loans, Bank_Securities, Bank_Deposits
- 金融ストレス: Small_Bank_Deposits, CC_Delinquency, CP_Spread, NFCI, Breakeven_10Y, Financial_Stress
- 市場: SP500, VIX, MOVE, HYG, LQD, NIKKEI
- 為替: DXY, USDJPY, EURUSD, USDCNY, GBPUSD, USDCHF, AUDUSD
- 商品: Gold, Silver, Oil, Copper
- 暗号資産: BTC, ETH
- その他: Michigan_Inflation_Exp, Leading_Index, M2_Velocity, ECB_Assets

---

### 2. mom_yoy（前月比・前年比パターン）- 6件

**対象**: 物価指数、消費指標など

```yaml
pattern: mom_yoy
base: standard  # 標準9要素を継承
additions:
  - mom_percent    # 前月比（%）
  - yoy_percent    # 前年比（%）
  - yoy_chart      # 前年比チャート
```

**対象指標**:
- CPI（消費者物価指数）
- CPICore（コアCPI）
- PPI（生産者物価指数）
- CorePCE（コアPCE）
- RetailSales（小売売上高）
- ConsumerSent（ミシガン消費者信頼感）

---

### 3. manual_calc（手動計算パターン）- 6件

**対象**: 特殊な計算ロジックが必要な指標

```yaml
pattern: manual_calc
base: standard  # 標準9要素を継承
special_logic:
  NFP: "前月比の変化数（千人）を計算"
  UNRATE: "生のパーセント表示"
  ADP: "千人単位変換"
  AvgHourlyEarnings: "前月比計算"
  ICSA: "千人単位変換"
  RealGDP: "前期比年率換算"
```

**対象指標**:
- UNRATE（失業率）
- NFP（非農業部門雇用者数）
- ADP（ADP雇用統計）
- AvgHourlyEarnings（平均時給）
- ICSA（新規失業保険申請件数）
- RealGDP（実質GDP）

---

### 4. web_scrape（Webスクレイピングパターン）- 2件

**対象**: FREDにないためWebから取得

```yaml
pattern: web_scrape
base: standard  # 標準9要素を継承
data_source: "Richmond Fed Website"
note: "API制限あり、取得失敗時のフォールバック必要"
```

**対象指標**:
- Richmond_Fed_Mfg（リッチモンド連銀製造業景況指数）
- Richmond_Fed_Services（リッチモンド連銀サービス業景況指数）

---

### 5. calculated（計算パターン）- 1件

**対象**: 複数指標から算出

```yaml
pattern: calculated
base: standard  # 標準9要素を継承
formula: "Fed_Assets + ECB_Assets - TGA - ON_RRP"
dependencies:
  - Fed_Assets
  - ECB_Assets
  - TGA
  - ON_RRP
```

**対象指標**:
- Global_Liquidity_Proxy（グローバル流動性プロキシ）

---

### 6. api（APIパターン）- 9件

**対象**: DataFrameに保存せず、個別APIコール

```yaml
pattern: api
elements:
  - label        # 必須
  - help_text    # 必須
  - value        # 必須
  - delta        # 状況による
  - notes        # 推奨
  # 以下はAPIの特性上、異なる場合あり
  - data_period  # APIによる
  - release_date # APIによる（リアルタイムの場合は「リアルタイム」と表示）
  - sparkline    # APIによる
  - full_chart   # なし（履歴データがない場合）
```

**対象指標**:
- バリュエーション: SP500_PE, NASDAQ_PE
- Cryptoレバレッジ: BTC_Funding_Rate, BTC_Open_Interest, BTC_Long_Short_Ratio, ETH_Funding_Rate, ETH_Open_Interest
- DeFiLlama: Stablecoin_Total, Treasury_TVL, Gold_TVL
- センチメント: Crypto_Fear_Greed, CNN_Fear_Greed

---

## 📊 パターン別件数サマリー

| パターン | 件数 | 割合 |
|---------|------|------|
| standard | 77 | 77% |
| mom_yoy | 6 | 6% |
| manual_calc | 6 | 6% |
| web_scrape | 2 | 2% |
| calculated | 1 | 1% |
| api | 9 | 9% |
| **合計** | **100** | **100%** |

---

## 🔧 新規指標追加の手順

### Step 1: indicators.py に追加

```python
'NEW_INDICATOR': {
    'source': 'FRED',           # データソース
    'id': 'SERIES_ID',          # シリーズID
    'unit': '%',                # 単位
    'frequency': 'monthly',     # 頻度
    'freshness': 'monthly',     # 鮮度判定基準
    'category': 'economy',      # カテゴリ
    'ui_page': '03_us_economic',# 表示ページ
    'ai_include': True,         # AI分析に含むか
    'ai_section': '米経済指標', # AIセクション
    'notes': '説明文',          # 一言補足
    'display_pattern': 'standard',  # ★これが重要
}
```

### Step 2: パターンを選ぶ

| 条件 | パターン |
|------|----------|
| 通常の指標 | `standard` |
| 前月比・前年比が必要 | `mom_yoy` |
| 特殊計算が必要 | `manual_calc` |
| Webスクレイピング | `web_scrape` |
| 複数指標から計算 | `calculated` |
| 個別APIコール | `api` |

### Step 3: ヘルプテキストを追加（必要な場合）

`utils/i18n.py` の `HELP_JA` / `HELP_EN` に追加

### Step 4: 確認

1. アプリを起動
2. Update Statusで表示を確認
3. ヘルスチェックでエラーがないか確認

---

## ⚠️ 注意事項

1. **display_pattern は必須**
   - 指定がない指標は `standard` として扱う（後方互換性）
   - 新規追加時は必ず明示的に指定する

2. **パターンの追加は慎重に**
   - 新しいパターンを作る前に、既存パターンで対応できないか検討
   - パターンが増えすぎると管理が複雑化

3. **仕様変更時はこのファイルを更新**
   - コードと仕様書の乖離を防ぐ
   - 変更履歴を記録する

---

## 🔗 パターンと表示関数の対応（Pattern-to-Function Mapping）

各パターンで使用すべき表示関数を定義。チェッカーはこの対応を検証する。

| パターン | 表示関数 | 検証対象 | 備考 |
|---------|---------|---------|------|
| `standard` | `show_metric_with_sparkline()` | ✅ Yes | 標準9要素を自動表示 |
| `mom_yoy` | `display_macro_card()` | ✅ Yes | MoM%/YoY%を自動計算 |
| `calculated` | `show_metric_with_sparkline()` | ✅ Yes | 依存指標から計算 |
| `manual_calc` | 独自ロジック | ❌ No | ページ内で個別実装 |
| `web_scrape` | 独自fetch + st.metric | ❌ No | 外部スクレイピング |
| `api` | 独自ロジック | ❌ No | 個別APIコール |

**検証ルール：**
- `standard` → `display_macro_card()` 使用は **エラー**
- `mom_yoy` → `show_metric_with_sparkline()` 使用は **エラー**
- `manual_calc`, `web_scrape`, `api` → 検証スキップ（独自実装のため）

---

## 📝 変更履歴

| 日付 | 変更内容 |
|------|----------|
| 2026-01-26 | パターン→関数対応表を追加。チェッカー連動の基盤。 |
| 2026-01-26 | 初版作成。100指標を6パターンに分類。 |

---

## 🔗 関連ドキュメント

- `utils/indicators.py` - 指標定義の実体
- `utils/charts.py` - 表示関数
- `utils/display_checker.py` - 表示要素チェッカー
- `docs/DESIGN_DISPLAY_CHECKER.md` - チェッカー設計書
