# Phase 3.5 仕様書：構成要素（9要素）の検出

> **目標**: 関数呼び出しの引数をパースし、構成要素の欠落を警告

---

## 📋 背景

### 現状（Phase 3まで）
- 関数呼び出しの**有無**は検出できる
- 関数の**引数**は検出できない

### 問題例
```python
# これは検出できる（呼び出しあり）
show_metric_with_sparkline(t('ind_EFFR'), df.get('EFFR'), 'EFFR')

# これは検出できない（引数変更）
show_metric_with_sparkline(t('ind_EFFR'), df.get('EFFR'), 'EFFR',
    explanation_key='',  # ← help_textが消える！
    notes='',            # ← 補足が消える！
)
```

---

## 🔍 調査結果：charts.py 関数シグネチャ

### 1. show_metric_with_sparkline（standard/calculated パターン）

```python
def show_metric_with_sparkline(
    label,                  # ① 監視名（必須）
    series,                 # ③ データ値
    df_column,              # ⑧ スパークライン用キー
    unit="",                # ③ 単位
    explanation_key="",     # ② help_text キー
    notes="",               # ⑦ 簡潔な補足
    alert_func=None,        # アラート関数
    decimal_places=1        # 小数点桁数
):
```

**9要素との対応**:
| 引数 | 9要素 | 必須 | 検出対象 |
|------|-------|------|----------|
| `label` | ① 監視名 | ◎ | 常にあり |
| `explanation_key` | ② help_text | ◎ | **空文字を警告** |
| `series` | ③ 値 | ◎ | 常にあり |
| - | ④ delta | ○ | 自動計算 |
| - | ⑤ data_period | ◎ | 自動取得 |
| - | ⑥ release_date | ◎ | 自動取得 |
| `notes` | ⑦ 補足 | ○ | 空文字を警告 |
| `df_column` | ⑧ sparkline | ○ | 常にあり |
| - | ⑨ full_chart | ○ | ページ実装依存 |

### 2. display_macro_card（mom_yoy パターン）

```python
def display_macro_card(
    title,                  # ① 監視名
    series,                 # ③ データ値
    df_column,              # ⑧ スパークライン用キー
    df_original=None,       # 原データ（デルタ計算用）
    unit="",                # ③ 単位
    notes="",               # ⑦ 簡潔な補足
    freq='M',               # 頻度
    show_level=True         # レベル表示（重要！）
):
```

**9要素との対応**:
| 引数 | 9要素 | 必須 | 検出対象 |
|------|-------|------|----------|
| `title` | ① 監視名 | ◎ | 常にあり |
| - | ② help_text | ◎ | 内部でshow_metric_with_sparkline呼び出し |
| `series` | ③ 値 | ◎ | 常にあり |
| - | ④ delta | ○ | 自動計算 |
| - | ⑤ data_period | ◎ | 自動取得 |
| - | ⑥ release_date | ◎ | 自動取得 |
| `notes` | ⑦ 補足 | ○ | 空文字を警告 |
| `df_column` | ⑧ sparkline | ○ | 常にあり |
| - | ⑨ full_chart | ○ | 自動描画 |
| **`show_level`** | 特殊 | - | **Falseを警告** |

---

## 🎯 実装計画

### Step 1: 引数パース正規表現の強化

現行の正規表現:
```python
# キーのみ抽出
spark_pat = re.compile(r'show_metric_with_sparkline\s*\(\s*[^,]+,\s*[^,]+,\s*[\'"]([\w_]+)[\'"]')
```

新しい正規表現（引数全体を抽出）:
```python
# 関数呼び出し全体を抽出（閉じ括弧まで）
spark_full_pat = re.compile(
    r'show_metric_with_sparkline\s*\(([^)]+)\)',
    re.DOTALL
)
```

### Step 2: 引数パーサーの実装

```python
def parse_function_args(args_str: str) -> Dict[str, str]:
    """
    関数引数文字列をパースして辞書で返す
    
    例: "label, series, 'KEY', explanation_key='', notes='test'"
    -> {'pos_0': 'label', 'pos_1': 'series', 'pos_2': "'KEY'", 
        'explanation_key': "''", 'notes': "'test'"}
    """
```

### Step 3: 警告ルールの定義

```python
ELEMENT_WARNINGS = {
    'show_metric_with_sparkline': {
        'explanation_key': {
            'check': lambda v: v in ('', "''", '""'),
            'message': 'explanation_key is empty (help_text will be missing)',
            'severity': 'WARN',  # 必須だがhelp_texts.pyに定義されていれば表示される
        },
        'notes': {
            'check': lambda v: v in ('', "''", '""'),
            'message': 'notes is empty',
            'severity': 'INFO',  # オプション要素
        },
    },
    'display_macro_card': {
        'show_level': {
            'check': lambda v: v.lower() == 'false',
            'message': 'show_level=False (level metric will be hidden)',
            'severity': 'WARN',
        },
        'notes': {
            'check': lambda v: v in ('', "''", '""'),
            'message': 'notes is empty',
            'severity': 'INFO',
        },
    },
}
```

### Step 4: 検証結果に追加

```python
results['element_warnings'] = [
    {
        'key': 'EFFR',
        'file': '01_liquidity.py',
        'function': 'show_metric_with_sparkline',
        'issue': 'explanation_key is empty',
        'severity': 'WARN',
    },
    ...
]
```

---

## 📊 出力例

```
============================================================
ELEMENT COMPOSITION WARNINGS (構成要素の警告)
============================================================

[WARN] EFFR (01_liquidity.py)
       show_metric_with_sparkline: explanation_key is empty

[INFO] SP500 (05_market.py)
       show_metric_with_sparkline: notes is empty

[WARN] CPI (03_us_economic.py)
       display_macro_card: show_level=False
```

---

## ✅ 実装チェックリスト

- [ ] 引数パース関数 `parse_function_args()` 追加
- [ ] 警告ルール定義 `ELEMENT_WARNINGS` 追加
- [ ] `verify_display_patterns()` に引数チェック統合
- [ ] レポート出力に警告セクション追加
- [ ] pre-commitでINFO以上を表示（WARNはブロックしない）

---

## 🔗 関連ファイル

- `utils/charts.py` - 表示関数定義
- `utils/display_checker.py` - チェッカー本体
- `docs/DISPLAY_SPEC.md` - 9要素仕様

---

## 📝 履歴

| 日付 | 内容 |
|------|------|
| 2026-01-27 | Phase 3.5 仕様書作成 |
