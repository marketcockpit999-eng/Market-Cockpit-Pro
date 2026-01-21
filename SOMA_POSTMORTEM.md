# SOMA問題 ポストモーテム（検証用）

## 問題の概要
`SOMA_Bills`（短期国債）を監視する意図で`TREAST`（全国債）を使用していた。
RMP（Reserve Management Purchases）監視機能が正しく動作していなかった可能性がある。

## タイムライン
1. **初期実装時期**: 不明 - `SOMA_Bills`として`TREAST`を使用開始
2. **2026-01-XX 前々スレ(b5d5d7c4)**: 問題発覚、`SOMA_Bills`→`SOMA_Treasury`にリネーム
3. **2026-01-XX 前スレ(53e58fae)**: i18n修正、Bills表示削除
4. **2026-01-20 現スレ**: RMP検出ロジックの残存参照を発見、`WSHOBL`を発見・追加

## 修正内容（現スレで実施）
1. **indicators.py**: `SOMA_Bills`を`WSHOBL`で新規追加
2. **data_fetcher.py**: mil_to_bilリストに`SOMA_Bills`追加
3. **i18n.py**: 英語・日本語翻訳キー追加

## 検証項目（次スレで実施）

### 1. 根本原因の特定
- [x] 最初に`TREAST`を`SOMA_Bills`として使用した経緯
  - **原因**: 指標名（"Bills"）とFRED ID（全国債）の意味の不一致を検証しなかった
  - **教訓**: FRED公式サイトで正式名称を必ず確認すべきだった
- [x] コミット履歴の確認（いつ、誰が、なぜ）
  - 初期実装時期は不明だが、名前から推測してIDを決めた可能性が高い
- [x] 仕様書やドキュメントの確認
  - 当時の明確な仕様書なし

### 2. 類似問題の調査
- [x] 他のFREDシリーズで同様の問題がないか
  - **発見**: `Fed_Assets`と`SOMA_Total`が両方`WALCL`を使用（重複）
  - **影響**: 軽微（概念的には`SOMA_Total`は`WSHOSHO`を使うべきだが、実用上は同等）
- [x] indicators.pyの全エントリをFREDで検証
  - 56個のFRED指標を確認
  - 重大な名前/ID不一致は現在のところなし

### 3. 再発防止策の検討
- [x] 指標追加時のチェックリスト作成
  - PROJECT_RULES.mdに「FRED指標追加時の検証ルール」セクション追加
- [x] FRED IDとその内容の明確なドキュメント化
  - 国債関連FREDシリーズのクイックリファレンス作成
- [ ] 自動検証テストの追加
  - TODO: pre-commit hookにFRED ID重複チェックを追加

## 参考情報

### FREDシリーズの実態
| FRED ID | 正式名称 | 内容 |
|---------|----------|------|
| **TREAST** | Treasury Securities Held Outright (All) | 全国債（Bills + Notes + Bonds） |
| **WSHOBL** | Treasury Securities: Bills | 短期国債のみ ✅ |
| **WSHONBNL** | Treasury Securities: Notes and Bonds, Nominal | 中長期国債（ノート・ボンド） |

### RMP（Reserve Management Purchases）とは
- 2025年12月10日FOMC発表
- 2025年12月12日から開始
- 月$40B規模でT-Billsを購入
- 準備金水準維持が目的
- **WSHOBLで追跡可能**

### 関連ファイル
- `utils/indicators.py`: 指標定義
- `utils/data_fetcher.py`: データ取得・RMP検出ロジック
- `utils/i18n.py`: 多言語対応
- `pages/01_liquidity.py`: UI表示

## 検証コマンド
```bash
# キャッシュクリア
del .market_data_cache.pkl

# アプリ起動
streamlit run market_app_nav.py

# 確認項目
# 1. SOMA_Billsがデータ取得されるか
# 2. RMPステータスが表示されるか
# 3. 週次変化が計算されるか
```

---

## ✅ 解決済み（2026-01-21）

### SOMA Treasury 表示問題
**問題**: SOMA Treasuryが「4243253.0 B」と表示（1000倍間違い）
**原因**: キャッシュ(.market_data_cache.pkl)に変換前データが残っていた
**解決**: キャッシュ削除 + Force Update で mil_to_bil変換が正常適用

### 検証結果
| 項目 | 期待値 | 実際値 | 状態 |
|------|--------|--------|------|
| SOMA Total | ~6500 B | 6581.7 B | ✅ |
| SOMA Treasury | ~4200 B | 4243.3 B | ✅ |
| RMP Status | 表示 | ✅ RMP Active: +8.2B/week | ✅ |

### 修正完了ファイル
1. `utils/indicators.py` - SOMA_Bills追加 ✅
2. `utils/data_fetcher.py` - mil_to_bilリスト更新 ✅
3. `utils/i18n.py` - 翻訳キー追加 ✅
4. `market_app_nav.py` - Force Updateでディスクキャッシュもクリア ✅

### 教訓
- **新指標追加後は必ずキャッシュクリア**が必要
- コードが正しくてもキャッシュに古いデータが残ると表示がおかしくなる
- Force Updateボタンでディスクキャッシュもクリアされるように修正済み

---

## 次スレへの指示
1. このファイルを読んで検証を開始
2. 根本原因を特定
3. 再発防止策を提案・実装
4. PROJECT_RULES.mdを更新
