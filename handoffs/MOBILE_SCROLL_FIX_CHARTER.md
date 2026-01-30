# Mobile Scroll Fix Charter（モバイルスクロール改善 作業憲章）

## 🎯 目的
モバイルでのスクロール地獄を解消する。`st.expander`でセクションを折りたたみ可能にする。

---

## ⚠️ なぜこの作業は危険か

このプロジェクトでは過去に何度も「ちょっとした修正」が派生問題を引き起こしてきた：

1. **show_metric_with_sparkline の呼び出しパターンは繊細**
   - 引数の順序、decimal_places、notes パラメータの微妙な違いで壊れる
   
2. **インデントの変更が予期せぬ影響を与える**
   - Pythonではインデントが構文。1スペースのズレでエラーになる
   
3. **「ついでに」の改善が問題の元**
   - 「ここも直しておこう」という善意が新たなバグを生む
   
4. **複数ファイルを一度に触ると追跡が困難**
   - 何が原因か特定できなくなる

---

## 🔒 絶対ルール（破ってはいけない）

### ルール1: 1スレッド = 1ファイルのみ
- 複数ファイルを同時に変更しない
- 1ファイル完了 → 確認 → コミット → 次のファイル

### ルール2: 既存コードの削除禁止
- `st.expander`で**囲むだけ**
- 既存の`show_metric_with_sparkline`呼び出しを一切変更しない
- 引数の順序、パラメータを触らない

### ルール3: 変更前に必ずバックアップ確認を依頼
- 「git status」で未コミットの変更がないか確認
- 変更前の状態を記録

### ルール4: 変更後は必ず動作確認を依頼
- `streamlit run market_app_nav.py`で起動確認
- 該当タブが正常に表示されるか確認
- データが正しく表示されるか確認

### ルール5: 派生課題が出たら「後でやるリスト」に追記して今は無視
- 新たな問題を見つけても、今のタスクを完了させることを優先
- 発見した問題は文書化して後回し

---

## 📋 作業順序（リスク低→高）

| Phase | ファイル | サイズ | セクション数 | 難易度 | 状態 |
|-------|---------|-------|-------------|--------|------|
| 1 | 02_global_money.py | 8.5KB | 6セクション | ⭐ | ⬜ 未着手 |
| 2 | 09_banking.py | 12KB | 6セクション | ⭐⭐ | ⬜ 未着手 |
| 3 | 04_crypto.py | 14KB | 4セクション | ⭐⭐ | ⬜ 未着手 |
| 4 | 01_liquidity.py | 21KB | 10セクション | ⭐⭐⭐ | ⬜ 未着手 |

**理由**:
- 02_global_money.py は最も小さく、構造がシンプル
- 01_liquidity.py は最も複雑なので経験を積んでから

---

## 🔧 変更パターン（これ以外やらない）

### Before（現在の状態）
```python
st.markdown("---")
st.markdown("### セクション名")
st.caption("説明文")

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 小見出し")
    show_metric_with_sparkline(...)
    ...
```

### After（変更後）
```python
st.markdown("---")
with st.expander("セクション名", expanded=True):
    st.caption("説明文")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 小見出し")
        show_metric_with_sparkline(...)
        ...
```

### 変更点の明確化
1. `st.markdown("### セクション名")` を削除
2. `with st.expander("セクション名", expanded=True):` を追加
3. その下のコード全体を**1インデント（4スペース）追加**
4. 次のセクション（次の`st.markdown("---")`）の手前までを囲む

### expanded=True の理由
- デスクトップでは今まで通り全て展開表示
- モバイルユーザーが折りたたんでスクロール短縮可能
- ユーザー体験を損なわない

---

## 🚫 やってはいけないこと

### 絶対禁止
- [ ] 関数の書き換え
- [ ] `show_metric_with_sparkline`の引数変更
- [ ] インデントの大幅変更（expanderで囲む以外）
- [ ] 「ついでに」の改善
- [ ] 新機能の追加
- [ ] コメントの追加・変更
- [ ] 変数名の変更
- [ ] import文の変更

### 疑わしい時は
- 変更しない
- ユーザーに確認する
- 「後でやるリスト」に追記

---

## 📝 各スレッド開始時の確認

新スレッドを始める時、必ずこのように宣言してください：

```
MOBILE_SCROLL_FIX_CHARTER.md を読みました。
Phase [X] の [ファイル名] を作業します。
絶対ルールを守ります。

■ このスレッドでやること
- [具体的な変更内容]

■ やらないこと
- 他のファイルの変更
- 「ついでに」の改善
```

---

## 📝 各スレッド終了時の記録

変更完了後、以下を記録：

```markdown
## 完了報告

### 変更したファイル
- [ファイル名]

### 変更したセクション
1. [セクション名] - ✅ expander化完了
2. [セクション名] - ✅ expander化完了
...

### 動作確認
- [ ] アプリ起動確認
- [ ] データ表示確認
- [ ] 折りたたみ動作確認

### 発見した派生課題（あれば）
- [課題の説明] → 後で対応

### 次スレッドへの申し送り
- Phase [X] の [ファイル名] へ進む
```

---

## 📋 Phase 1: 02_global_money.py 詳細

### 対象セクション一覧

| # | 行番号 | セクション名 | カラム構成 | 注意点 |
|---|--------|-------------|-----------|--------|
| 1 | 29-46 | US Money Supply (M2) | 2カラム | シンプル |
| 2 | 48-68 | Central Bank Assets | 2カラム | シンプル |
| 3 | 70-127 | FX Section | **7カラム** | モバイルで最も問題 |
| 4 | 129-148 | Global Indices | 2カラム | シンプル |
| 5 | 150-179 | Commodities | 4カラム | 中程度 |
| 6 | 181-200 | Crypto | 2カラム | シンプル |

### 作業手順（Phase 1 専用）

#### Step 1: US M2 Section (行29-46)
```
Before:
29: st.markdown("---")
30: st.markdown(f"### 💵 US Money Supply (M2)")
31: st.caption(t('us_m2_desc'))
32: 
33: col1, col2 = st.columns(2)
...
46: [セクション終了]

After:
29: st.markdown("---")
30: with st.expander("💵 US Money Supply (M2)", expanded=True):
31:     st.caption(t('us_m2_desc'))
32:     
33:     col1, col2 = st.columns(2)
...（以下全て1インデント追加）
```

#### Step 2: Central Bank Assets (行48-68)
同様のパターン

#### Step 3: FX Section (行70-127)
**注意**: 7カラム構造。インデント追加時に注意

#### Step 4: Global Indices (行129-148)
同様のパターン

#### Step 5: Commodities (行150-179)
4カラム構造

#### Step 6: Crypto (行181-200)
同様のパターン

---

## 🔗 参考リンク

- 前スレッド: https://claude.ai/chat/fc53ada7-a0f1-409b-a751-15789f76ec55
- プロジェクトルール: `PROJECT_RULES.md`
- 指標定義: `utils/indicators.py`

---

## 📊 進捗トラッキング

### Phase 1: 02_global_money.py ✅ 完了 (2026-01-30)
- [x] Section 1: US Money Supply (M2)
- [x] Section 2: Central Bank Assets
- [x] Section 3: FX Section
- [x] Section 4: Global Indices
- [x] Section 5: Commodities
- [x] Section 6: Crypto
- [x] 動作確認完了
- [x] コミット完了
- 作業スレッド: https://claude.ai/chat/5b4d6d30-c79c-4ae8-b6fa-2ee7d1b6f158

### Phase 2: 09_banking.py ✅ 完了 (2026-01-30)
- [x] Section 1: H.8 Weekly Data ✅
- [x] Section 2: H.8 Consumer ✅
- [x] Section 3: Financial Stress Indicators ✅
- [x] Section 4: SLOOS C&I Section ✅
- [x] Section 5: SLOOS CRE Section ✅
- [x] Section 6: Loan Comparison Chart ✅
- [x] 動作確認完了
- [x] コミット完了
- 作業スレッド1: https://claude.ai/chat/4b0051c6-45f7-49a9-bc24-7f6d2f5219ff
- 作業スレッド2: https://claude.ai/project/019bb281-b291-72ad-85c0-ceecab814cb7

### Phase 3: 04_crypto.py ✅ 完了 (2026-01-30)
- [x] Section 1: BTC & ETH Prices ✅
- [x] Section 2: Stablecoin Supply ✅
- [x] Section 3: Tokenized Treasury ✅
- [x] Section 4: Market Depth ✅
- [x] 動作確認完了
- [x] コミット完了
- 作業スレッド: https://claude.ai/chat/39be0f90-faf3-4046-b907-73060e13edea

### Phase 4: 01_liquidity.py（6スレッドに分割）

**⚠️ 詳細計画**: `handoffs/PHASE4_PLAN.md` を必ず参照

| スレッド | 内容 | 状態 |
|----------|------|------|
| 4-1 | 翻訳キー追加 | ⬜ 未着手 |
| 4-2 | Corp Bond ETFs, Risk Bonds, Emergency Loans | ⬜ 未着手 |
| 4-3 | Fed Balance Sheet, FF Target Rate | ⬜ 未着手 |
| 4-4 | Market Plumbing | ⬜ 未着手 |
| 4-5 | Net Liquidity, ON RRP/Reserves/TGA | ⬜ 未着手 |
| 4-6 | Valuation & Leverage, Open Interest | ⬜ 未着手 |

**Phase 4 特有の注意点**:
1. Open Interest は `if leverage_data:` の中にexpanderを入れる
2. `record_api_status()` はexpander外に残す
3. Market Plumbingの`diff`変数を分断しない

---

## 📝 後でやるリスト（派生課題）

作業中に発見した問題はここに追記：

1. （まだなし）

---

Created: 2026-01-30
Last Updated: 2026-01-30
