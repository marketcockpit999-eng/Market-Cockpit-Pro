# Phase 5 US Economic Data Expander化 詳細計画（分割版）
# ====================================================

> **作業憲章**: `handoffs/US_ECONOMIC_EXPANDER_CHARTER.md`
> **対象ファイル**: `pages/03_us_economic.py`
> **総スレッド数**: 8スレッド（分割により作業量を均等化）

---

## 🗓️ スレッド分割計画（分割版）

| Phase | セクション | 行数 | 推定時間 | 状態 |
|-------|-----------|------|----------|------|
| 5-1a | Employment (col1) | 65行 | 20-25分 | ⬜ |
| 5-1b | Employment (col2) | 70行 | 20-25分 | ⬜ |
| 5-2 | Inflation + Economy | 80行 | 20-25分 | ⬜ |
| 5-3 | Michigan + Leading | 37行 | 15-20分 | ⬜ |
| 5-4 | Manufacturing | 97行 | 25-30分 | ⬜ |
| 5-5a | Services | 95行 | 25-30分 | ⬜ |
| 5-5b | Housing | 34行 | 15-20分 | ⬜ |

**合計**: 7スレッド、各スレッド15-30分で完了可能

---

## ⚠️ 作業順序（推奨）

```
5-3 (軽) → 5-2 (中) → 5-1a+5-1b (重) → 5-4 (中) → 5-5a → 5-5b (軽)

理由:
1. 5-3: 最も軽い。変更パターンに慣れる
2. 5-2: 中程度。display_macro_card中心
3. 5-1a+5-1b: 最も重いが、慣れた状態で挑む
4. 5-4: Richmond Fed特殊処理の練習
5. 5-5a: 5-4と同構造。Richmond Fed Services
6. 5-5b: 最も軽い。Housingのみ
```

---

## 🟢 Phase 5-3: Michigan + Leading（ウォームアップ）

### 基本情報
- **行数**: 37行
- **推定時間**: 15-20分
- **難易度**: ⭐最も軽い

### ⚠️ 技術的リスクポイント

```
🔴 Leading のヘッダーに📈絵文字が含まれている
   st.markdown(f"### 📈 {t('us_economic_section_leading')}")
   → expanderタイトル: f"📈 {t('us_economic_section_leading')}"
   → 絵文字を忘れずに含める！
```

### Michigan Inflation セクション（行276-295）

**削除する行:**
```python
st.markdown(f"#### {t('michigan_inflation_title')}")
```

**追加する行:**
```python
with st.expander(t('michigan_inflation_title'), expanded=True):
```

**インデント追加範囲**: 行278-295（約18行）

### Leading Indicators セクション（行492-508）

**削除する行:**
```python
st.markdown(f"### 📈 {t('us_economic_section_leading')}")
```

**追加する行（絵文字含む！）:**
```python
with st.expander(f"📈 {t('us_economic_section_leading')}", expanded=True):
```

**インデント追加範囲**: 行495-508（約14行）

### チェックポイント
- [ ] Michigan Inflation Expectations が表示される
- [ ] Leading Index（CFNAI）が表示される
- [ ] expanderタイトルに📈絵文字が含まれている

---

## 🟡 Phase 5-2: Inflation + Economy

### 基本情報
- **行数**: 80行
- **推定時間**: 20-25分
- **難易度**: ⭐⭐中程度

### ⚠️ 技術的リスクポイント

```
🟡 Inflation内部にもst.markdown("---")がある → expander内に残す
🟡 GDP計算ロジック（qoq_pct, annualized）→ 絶対に触らない
🟡 Yield CurveのPlotlyチャート key引数 → 触らない
```

### Inflation セクション（行194-219）

**削除する行:**
```python
st.markdown(f"### {t('us_economic_section_inflation')}")
```

**追加する行:**
```python
with st.expander(t('us_economic_section_inflation'), expanded=True):
```

**インデント追加範囲**: 行196-219（約24行）

### Economy セクション（行221-274）

**削除する行:**
```python
st.markdown(f"### {t('us_economic_section_economy')}")
```

**追加する行:**
```python
with st.expander(t('us_economic_section_economy'), expanded=True):
```

**インデント追加範囲**: 行223-274（約52行）

### チェックポイント
- [ ] CPI, Core CPI, Core PCE, PPI が表示される
- [ ] Retail Sales, Consumer Sentiment が表示される
- [ ] GDP計算値が正しい
- [ ] Yield Curveの0ラインが表示される

---

## 🔴 Phase 5-1a: Employment (col1)【重要：特殊手順】

### ⚠️ 特殊な作業フロー

```
❗ このスレッドの終了時点ではコードは動作しません
❗ コミットせずに次のスレッド(5-1b)に引き継ぎます
❗ 5-1bが完了して初めてコミット可能になります
```

### 基本情報
- **行数**: 約65行（col1部分）
- **推定時間**: 20-25分
- **難易度**: ⭐⭐⭐高（特殊手順）

### ⚠️ 技術的リスクポイント

```
🔴 col1とcol2は同じst.columns(2)に属する
   → 片方だけインデントすると構文エラー
   → 5-1aと5-1bを連続で実行する必要あり

🔴 from imports が2箇所に散在（col1内）
   from utils.help_texts import HELP_EN, HELP_JA
   from utils.i18n import get_current_language
   → これらの位置を変えない

🔴 内部に2つのst.markdown("---")がある
   → expander内に残す
```

### 作業内容

**Step 1: セクションヘッダーを変更（行57）**
```python
# Before
st.markdown(f"### {t('us_economic_section_employment')}")

# After
with st.expander(t('us_economic_section_employment'), expanded=True):
```

**Step 2: col1, col2 定義をインデント（行58）**
```python
    col1, col2 = st.columns(2)
```

**Step 3: with col1: 以下をインデント（行60-125）**
- NFP部分（約25行）
- ADP部分（約20行）
- Unemployment部分（約20行）

### 終了時の状態
```
⚠️ コードは構文エラー状態（col2がインデントされていない）
⚠️ コミットしない
⚠️ 次のスレッド(5-1b)に引き継ぐ
```

### 引き継ぎ情報
```
Phase 5-1a 完了。コードは構文エラー状態。
次のPhase 5-1bでcol2をインデントして完成させる。

残作業:
- with col2: 以下（行127-192）をインデント
- 動作確認
- コミット
```

---

## 🔴 Phase 5-1b: Employment (col2)【5-1aの続き】

### ⚠️ 前提条件

```
❗ Phase 5-1aが完了していること
❗ コードは現在構文エラー状態
❗ このスレッドで完成させてコミットする
```

### 基本情報
- **行数**: 約70行（col2部分）
- **推定時間**: 20-25分
- **難易度**: ⭐⭐⭐高（前スレッドからの継続）

### 作業内容

**Step 1: with col2: 以下をインデント（行127-192）**
- AvgHourlyEarnings部分（約20行）
- JOLTS部分（約15行）
- ICSA部分（約35行）

### 完了後の状態
```
✅ コードが完成
✅ 動作確認可能
✅ コミット可能
```

### チェックポイント（5-1a + 5-1b 合計）
- [ ] NFP（雇用統計）が表示される
- [ ] ADP雇用統計が表示される
- [ ] 失業率が表示される
- [ ] 平均時給が表示される
- [ ] JOLTSが表示される
- [ ] ICSA（失業保険申請）が表示される
- [ ] 全てのスパークラインチャートが描画される
- [ ] 内部の区切り線（---）が正常に表示される

---

## 🟠 Phase 5-4: Manufacturing

### 基本情報
- **行数**: 97行
- **推定時間**: 25-30分
- **難易度**: ⭐⭐中（特殊処理あり）

### ⚠️ 技術的リスクポイント

```
🔴 Richmond Fed 特殊データ取得
   richmond_data = get_richmond_fed_survey()
   → この行とその後のロジックを絶対に触らない

🔴 内部expanderが既存
   with st.expander(t('manufacturing_guide').split('\n')[0], expanded=False):
   → ネストとして維持

🟡 4つのPlotlyチャート
   → 各変数名とkey引数を触らない
```

### 作業内容

**削除する行（行299）:**
```python
st.markdown(f"### {t('us_economic_section_manufacturing')}")
```

**追加する行:**
```python
with st.expander(t('us_economic_section_manufacturing'), expanded=True):
```

**インデント追加範囲**: 行300-393（約94行）
- 内部の`with st.expander(t('manufacturing_guide')...)`を含む

### チェックポイント
- [ ] Empire State, Philly Fed, Dallas Fed が表示される
- [ ] Richmond Fed が表示される（データ取得含む）
- [ ] Manufacturing Guide の内部expanderが動作する

---

## 🟠 Phase 5-5a: Services

### 基本情報
- **行数**: 95行
- **推定時間**: 25-30分
- **難易度**: ⭐⭐中（5-4と同構造）

### ⚠️ 技術的リスクポイント

```
🔴 Richmond Fed Services 特殊データ取得
   richmond_svc_data = get_richmond_fed_services_survey()
   → 絶対に触らない

🔴 内部expander（services_guide）
   → ネストとして維持
```

### 作業内容

**削除する行:**
```python
st.markdown(f"### {t('us_economic_section_services')}")
```

**追加する行:**
```python
with st.expander(t('us_economic_section_services'), expanded=True):
```

**インデント追加範囲**: 約95行

### チェックポイント
- [ ] Philly Fed Services, Dallas Fed Services, NY Fed Services が表示される
- [ ] Richmond Fed Services が表示される（データ取得含む）
- [ ] Services Guide の内部expanderが動作する

---

## 🟢 Phase 5-5b: Housing

### 基本情報
- **行数**: 34行
- **推定時間**: 15-20分
- **難易度**: ⭐軽い

### ⚠️ 技術的リスクポイント

```
🔴 ヘッダーに🏠絵文字が含まれている
   st.markdown(f"### 🏠 {t('us_economic_section_housing')}")
   → expanderタイトル: f"🏠 {t('us_economic_section_housing')}"
   → 絵文字を忘れずに含める！
```

### 作業内容

**削除する行:**
```python
st.markdown(f"### 🏠 {t('us_economic_section_housing')}")
```

**追加する行（絵文字含む！）:**
```python
with st.expander(f"🏠 {t('us_economic_section_housing')}", expanded=True):
```

**インデント追加範囲**: 約32行

### チェックポイント
- [ ] Housing Starts が表示される
- [ ] Building Permits が表示される
- [ ] expanderタイトルに🏠絵文字が含まれている

---

## 🔧 スレッド開始テンプレート

```markdown
## Phase 5-[X]: [セクション名]

### 必読ドキュメント
- ✅ `handoffs/US_ECONOMIC_EXPANDER_CHARTER.md`
- ✅ `handoffs/PHASE5_US_ECONOMIC_PLAN.md`

### 前スレッド
[URL]

### 開始宣言
US_ECONOMIC_EXPANDER_CHARTER.md を読みました。
Phase 5-[X] の [セクション名] を作業します。
絶対ルールを守ります。

### このスレッドの技術的リスク
1. [リスク1]
2. [リスク2]

### やること
1. [具体的な変更1]
2. [具体的な変更2]

### やらないこと
- 他のセクションの変更
- show_metric_with_sparkline等の引数変更
- Richmond Fed のデータ取得ロジック変更
- 「ついでに」の改善

### ロールバック準備
git checkout -- pages/03_us_economic.py
```

---

## 📊 進捗トラッキング

### Phase 5-3: Michigan + Leading（ウォームアップ）
- [ ] 作業開始
- [ ] 変更完了
- [ ] 動作確認
- [ ] コミット完了
- スレッドURL: 

### Phase 5-2: Inflation + Economy
- [ ] 作業開始
- [ ] 変更完了
- [ ] 動作確認
- [ ] コミット完了
- スレッドURL: 

### Phase 5-1a: Employment (col1)
- [ ] 作業開始
- [ ] 変更完了
- [ ] ⚠️ コミットしない（5-1bに引き継ぎ）
- スレッドURL: 

### Phase 5-1b: Employment (col2)
- [ ] 作業開始
- [ ] 変更完了
- [ ] 動作確認
- [ ] コミット完了（5-1a + 5-1b 合計）
- スレッドURL: 

### Phase 5-4: Manufacturing
- [ ] 作業開始
- [ ] 変更完了
- [ ] 動作確認
- [ ] コミット完了
- スレッドURL: 

### Phase 5-5a: Services
- [ ] 作業開始
- [ ] 変更完了
- [ ] 動作確認
- [ ] コミット完了
- スレッドURL: 

### Phase 5-5b: Housing
- [ ] 作業開始
- [ ] 変更完了
- [ ] 動作確認
- [ ] コミット完了
- スレッドURL: 

---

## 📝 派生課題リスト

作業中に発見した問題はここに追記：

1. （まだなし）

---

Created: 2026-01-30
Version: 2.0 (分割版)
