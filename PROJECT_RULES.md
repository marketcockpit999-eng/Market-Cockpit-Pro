# Market Monitor Project Rules

## FRB/SOMA Monitoring Specification (Memorized)
- **Tab 1: Liquidity & Rates**
  - **Subheader**: `🔧 Market Plumbing (Repo & Liquidity)` (Must not use "FX").
  - **RMP Status**: Persistent status box in SOMA section showing latest RMP alert/stable text.
  - **RMP Alert Logic**: Trigger alert if `Reserves` are declining AND (`SomaBillsRatio` up for 2 weeks OR `SOMA_Bills` absolute increase).
  - **SOMA Bills Metrics**: 
    - Display `RMP (短期国債)` instead of generic "Bills".
    - `SomaBillsRatio` = (SOMA Bills / SOMA Total) * 100.
  - **SOMA Chart**: 
    - Dual-axis: `SOMA_Total` (Bar) and `SomaBillsRatio` (Line).
    - Use Weekly resampling (`W-WED`) and Stepped line (`shape='hv'`).
    - Axis scaling: Ensure subtle (1%) ratio changes are clearly visible.
  - **Terminology**: Use exact Japanese text provided for `SomaBillsRatio` explanation and `RMP` alerts.
  - **Data Resilience**: Use `df.get()` for all UI accesses to prevent crashes.

これらのルールは、マーケット監視アプリの開発において「不変」であり、修正のたびに必ず確認すること。

## 1. 修正のスタイル (No Regression Policy)
- **外科手術的修正 (Surgical Edits)**: 常に関数全体を書き換えるのではなく、必要な数行だけを差し替え・追加すること。
- **UIコンテキストの保護**: 詳細な「解説テキスト (EXPLANATIONS)」や、タブ (tabs) の構造、ウィジェットの配置を絶対に削除しないこと。

## 2. データ処理の鉄則
- **単位の正規化 (Million to Billion)**:
    - FREDの以下の指標は「百万ドル(Million)」で取得されるため、取得直後に必ず **1000で割って「十億ドル(Billion)」に統一** すること。
    - 対象: `Fed_Assets`, `TGA`, `Reserves`, `SOMA_Total`, `SOMA_Bills`, `Primary_Credit`, `Total_Loans`
    - `ON_RRP` は最初からBillion単位なのでそのまま扱うこと。
- **計算の整合性**:
    - `Net_Liquidity` などの誘導指標を計算する際は、単位が揃っていることを確認すること。

## 3. 日付表示のルール
- **「今日」を表示しない**: `show_metric` では、必ず「データセットの中でNaNではない最後の有効な値の日付」を表示すること。
- **指標ごとの独立性**: 雇用統計などが古い月の日付であれば、それをそのまま表示し、無理に最新日に合わせないこと。

---

## ⚠️ 4. 回帰防止ルール (CRITICAL - 2026-01-09追加)

### 🔒 修正・機能追加時の必須チェックリスト

**修正前に必ず確認:**
1. 変更対象のコードブロック**のみ**を編集する（周辺コードは絶対に削除しない）
2. 既存の `show_metric_with_sparkline()` 呼び出しを削除・移動しない
3. データ取得関数 (`get_market_data`) の構造を変更しない

**修正後に必ず確認:**
1. **全タブが表示されているか** - tabs[0]〜tabs[6] の全てが動作確認
2. **全指標が表示されているか** - 以下の指標が欠けていないか目視確認:
   - Liquidity: Net_Liquidity, ON_RRP, Reserves, TGA
   - SOMA: SOMA_Total, SOMA_Bills, SomaBillsRatio
   - Employment: NFP, ADP, UNRATE, AvgHourlyEarnings, JOLTS, **ICSA**
   - Inflation: CPI, CPICore, PPI, CorePCE
   - Economy: RetailSales, RealGDP, ConsumerSent, T10Y2Y
3. **提供元更新日が表示されているか** - `show_metric_with_sparkline` 使用箇所

### 📋 保護すべき重要コード領域

| 領域 | 行番号（目安） | 内容 |
|------|--------------|------|
| `show_metric_with_sparkline` | 1414-1500 | 統一表示関数 |
| Employment セクション | 2466-2680 | 雇用関連全指標 |
| ICSA 表示 | 2624-2673 | 新規失業保険 |
| Market Voices | 4000-4280 | 一次情報ハンター |

### ❌ 絶対にやってはいけないこと
- 「効率化」のためにセクション全体を書き換える
- 関数を「改善」するために既存の出力を変更する
- 新機能追加時に既存コードを「整理」する

---

## 5. Primary Source Intelligence Hunter 機能仕様 (2026-01-09追加)

### 概要
「Market Voices」タブにある一次情報ハンター機能。
AIが政府・中銀・国際機関の公式資料を探索・分析する。

### アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│ UI Layer (market_app.py: 4295-4550)                         │
├─────────────────────────────────────────────────────────────┤
│ 1. 探索キーワード入力 (text_input)                           │
│    key: "global_pulse_query"                                │
│                                                             │
│ 2. 探索モード選択 (radio)                                    │
│    - "一次情報/レポート (Pro)" → primary                     │
│    - "一般ニュース (General)" → general                      │
│                                                             │
│ 3. コンテキスト複数選択 (multiselect)                        │
│    key: "global_pulse_contexts"                             │
│    → CONTEXT_KEYWORDS辞書から自動キーワード生成              │
└─────────────────────────────────────────────────────────────┘
```

### コンテキスト選択とキーワード連携のロジック

**ファイル**: `market_app.py` 行 4316-4455

```python
# 構造体定義
CONTEXT_KEYWORDS = {
    "🏛️ 中央銀行 (Central Bank)": {
        "keywords": ["Fed policy", "rate cut", ...],  # 詳細キーワード
        "desc": "利下げ・QT・バランスシート",           # UI表示用説明
        "main_keyword": "Fed policy"                   # 自動セット用メインキーワード
    },
    # ... 13カテゴリ定義
}
```

**自動キーワード更新ロジック** (行 4400-4455):

```python
# 1. 選択したコンテキストからメインキーワードを結合
auto_keywords = [CONTEXT_KEYWORDS[ctx]["main_keyword"] for ctx in selected_contexts]
combined = " OR ".join(auto_keywords)  # 例: "Fed policy OR liquidity crisis"

# 2. 自動更新の条件判定 (session_state活用)
if st.session_state["last_auto_keyword"] != combined:
    # ユーザーが手動入力していない場合のみ自動セット
    if not current_query or current_query == st.session_state["last_auto_keyword"]:
        st.session_state["global_pulse_query"] = combined
        st.rerun()
```

**重要なsession_stateキー**:
| キー | 用途 |
|-----|------|
| `global_pulse_query` | 探索キーワード入力欄の値 |
| `global_pulse_contexts` | 選択中のコンテキスト（リスト） |
| `last_auto_keyword` | 最後に自動セットしたキーワード（上書き防止用） |

### 探索実行フロー

```
[ボタンクリック: "🔎 一次情報の深層を探索"]
    ↓
[search_primary_sources(query, mode, context)]
    ↓
[1. 地域別Googleニュース検索 (US/EU/Asia)]
    ↓
[2. ドメインフィルタリング (.gov, .org, .int優先)]
    ↓
[3. AI評価 (Gemini/Claude)]
    - Discovery Value (発見価値)
    - Structural Signal (構造的シグナル)
    - Trustworthiness (信頼性)
    - News Generalization Probability (N日後ニュース化確率)
    ↓
[4. 結果表示 (カード形式)]
```

### コンテキストカテゴリ一覧

| カテゴリ | メインキーワード | 用途 |
|---------|----------------|------|
| 🌐 地政学リスク | geopolitical risk | 制裁・紛争 |
| 📊 マクロ経済 | recession risk | 景気後退 |
| 🏛️ 中央銀行 | Fed policy | 金融政策 |
| 💧 流動性・配管 | liquidity crisis | レポ・準備金 |
| 🛢️ コモディティ | oil price gold | 原油・金 |
| ₿ 仮想通貨 | Bitcoin regulation | 規制・ETF |
| 🏦 銀行・信用 | bank stress | 信用収縮 |
| 🏢 不動産 | commercial real estate | CRE危機 |
| 💵 通貨・為替 | dollar strength | ドル・介入 |
| 📉 株式 | stock market bubble | バリュエーション |
| 🇨🇳 中国 | China economy | 中国経済 |
| 🇪🇺 欧州 | ECB policy | ECB政策 |
| 🌍 新興国 | emerging market crisis | EM危機 |

---

## 6. Market Sentimentタブ仕様 (2026-01-09追加)

### 概要
tabs[7]に配置。投資家心理を可視化。

### 表示指標

| 指標 | データソース | 更新頻度 |
|-----|------------|---------|
| Crypto Fear & Greed | alternative.me API | 毎日 |
| VIX | Yahoo Finance (^VIX) | リアルタイム |
| AAII Investor Sentiment | aaii.com (プレースホルダ) | 週次 |
| Put/Call Ratio | CBOE (プレースホルダ) | 毎日 |

### Bull-Bear Spread 解釈ガイド

```
+30%以上: 🔴 過熱（逆張り売りシグナル）
+10〜+30%: 🟡 やや強気
-10〜+10%: 🟢 中立
-30〜-10%: 🟡 やや弱気
-30%以下: 🔴 極度の悲観（逆張り買いシグナル）
```

