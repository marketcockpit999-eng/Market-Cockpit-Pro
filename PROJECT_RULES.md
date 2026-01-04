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
