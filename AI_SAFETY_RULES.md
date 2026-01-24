# ⚠️ CRITICAL RULES FOR AI ASSISTANTS
> **このファイルを必ず読んでから作業してください**
> Read this file before making ANY changes

---

## 🚫 絶対にやってはいけないこと (NEVER DO)

### 1. 既存ファイルの大規模書き換え禁止
```
❌ BAD: ファイル全体を新しいコードで置き換える
❌ BAD: 関数を丸ごと書き直す
❌ BAD: import文を変更する（追加はOK）

✅ GOOD: 必要な行だけを追加・修正する（外科手術的修正）
✅ GOOD: 新しい関数を追加する（既存関数は触らない）
```

### 2. 削除禁止
```
❌ NEVER delete existing functions
❌ NEVER delete existing files
❌ NEVER remove show_metric_with_sparkline calls
❌ NEVER remove import statements
```

### 3. これらのファイルは読み取り専用として扱う
```
utils/indicators.py      ← Single Source of Truth, 変更禁止
utils/data_fetcher.py    ← データ取得ロジック、変更禁止
utils/charts.py          ← チャート関数、変更禁止
market_app_nav.py        ← エントリーポイント、変更禁止
```

---

## ✅ 安全な作業パターン

### Phase 4 WHYセクション実装の場合

**新規ファイル作成のみ:**
```
utils/verdict_why.py     ← 新規作成OK
```

**追加のみ（既存コードは触らない）:**
```python
# pages/13_verdict.py の末尾に追加
def render_why_section(verdict):
    # 新しいコードをここに
    pass

# main()関数内に1行追加するだけ
render_why_section(verdict)
```

**i18n.pyへの追加（削除・変更なし）:**
```python
# 既存のキーは触らず、新しいキーを追加するだけ
'verdict_why_title': 'Why This Verdict?',
```

---

## 🔍 作業前チェックリスト

□ `git status` で変更予定ファイルを確認したか？
□ 変更するのは本当に必要な箇所だけか？
□ 既存の関数を削除・書き換えしていないか？
□ 新しいコードは既存コードの末尾に追加しているか？
□ テスト実行して既存機能が壊れていないか確認したか？

---

## 🆘 困ったら

**わからないことがあれば、作業を止めてユーザーに確認してください。**

推測で大規模な変更を行うより、確認を取る方が100倍安全です。

---

## 📁 Phase 4 作業ガイド

詳細は `HANDOFF_VERDICT_PHASE4.md` を参照してください。

主な作業:
1. `utils/verdict_why.py` を新規作成
2. `utils/i18n.py` に翻訳キーを追加（末尾に）
3. `pages/13_verdict.py` に `render_why_section()` を追加（末尾に）
4. `main()` 関数内で `render_why_section(verdict)` を呼び出す

**既存コードの変更は最小限に！**
