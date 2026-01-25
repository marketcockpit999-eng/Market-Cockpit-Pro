# Display Checker 設計書

## 目的

**display_pattern 別の必須表示要素が揃っているかをチェックする**

機能追加・修正時に「構成要素が消える」のを自動検出することが最終目標。

---

## 各パターンの必須要素

### 1. standard（73項目）

使用関数: `show_metric_with_sparkline()`

| 要素 | 説明 | 例 |
|------|------|-----|
| label | 指標名 | "ON-RRP" |
| value | 最新値 | "85.2 B" |
| delta | 前回比 | "+2.1" |
| date | データ日付 | "2026-01-23" |
| sparkline | 60日ミニチャート | ✓ |

**チェックポイント:**
- value が N/A でない
- delta が表示されている
- sparkline が描画されている

### 2. mom_yoy（6項目）

使用関数: `display_macro_card()`

対象: CPI, CPICore, CorePCE, PPI, RetailSales, ConsumerSent

| 要素 | 説明 |
|------|------|
| mom_pct | 前月比% |
| yoy_pct | 前年比% |
| sparkline | 60日ミニチャート |
| yoy_chart | YoY%推移チャート |
| long_term_chart | 長期トレンド（水準） |

**チェックポイント:**
- MoMとYoYの両方が計算できている
- チャートが3つ描画されている

### 3. manual_calc（6項目）

対象: NFP, UNRATE, AvgHourlyEarnings, ICSA, RealGDP, ADP

| 指標 | 表示パターン |
|------|-------------|
| NFP | 前月比変化（+300K等） |
| UNRATE | 現在値 + 前月差 |
| AvgHourlyEarnings | MoM% + YoY% |
| ICSA | 最新値 + 前週比 |
| RealGDP | QoQ年率換算% |
| ADP | 前月比変化 |

**チェックポイント:**
- 各指標固有の計算ロジックが正しい

### 4. web_scrape（2項目）

対象: Richmond_Fed_Mfg, Richmond_Fed_Services

| 要素 | 説明 |
|------|------|
| value | スクレイピング値 |
| date | データ月 |
| fallback | エラー時のフォールバック表示 |

**チェックポイント:**
- スクレイピング成功/失敗の判定
- fallback が適切に表示される

### 5. calculated（1項目）

対象: Global_Liquidity_Proxy

| 要素 | 説明 |
|------|------|
| value | 計算値（Fed+ECB-TGA-RRP） |
| chart | トレンドチャート |

**チェックポイント:**
- 計算元の指標が全て揃っている
- 計算結果が妥当な範囲内

### 6. api（12項目）

対象: SP500_PE, NASDAQ_PE, BTC_Funding_Rate, etc.

| 要素 | 説明 |
|------|------|
| value | API取得値 |
| error_handling | エラー時表示 |

**チェックポイント:**
- API応答があるか
- タイムアウト時の表示

---

## 実装方針

### Phase 1: データ検証チェッカー（今回作成）

```python
# utils/display_checker.py

def check_all_indicators(df, df_original):
    """全指標の表示要素をチェック"""
    results = {
        'standard': [],
        'mom_yoy': [],
        'manual_calc': [],
        'web_scrape': [],
        'calculated': [],
        'api': [],
    }
    ...
    return results
```

### Phase 2: UIレンダリング検証（将来）

Streamlit画面を実際にレンダリングして、要素の有無を検証。

---

## ファイル構成

```
utils/
  display_checker.py    # チェッカー関数（新規作成）

scripts/
  test_display_checker.py  # テストスクリプト
```

---

## 次のアクション

1. `utils/display_checker.py` 作成
2. `scripts/test_display_checker.py` 作成
3. 動作確認
