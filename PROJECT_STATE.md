# Market Cockpit Pro - プロジェクト状態

**最終更新**: 2026-01-12 13:30 JST

---

## 🔄 現在の状態

**ステータス**: ✅ 運用中・安定（モジュール化リファクタリング完了）

---

## 🏗️ アーキテクチャ

### 新アーキテクチャ（2026-01-12移行完了）
| ファイル/ディレクトリ | 役割 |
| :--- | :--- |
| **`market_app_nav.py`** | エントリポイント（`st.navigation`使用）|
| **`utils/`** | 共有モジュールパッケージ |
| ↳ `data.py` | FRED/Yahoo/DeFiLlama等のデータ取得・加工 |
| ↳ `ai.py` | Gemini/Claude AIオーケストレーション |
| ↳ `charts.py` | Sparkline、Dual Axis等の可視化 |
| ↳ `constants.py` | 定数、FRED系列ID、単位定義 |
| ↳ `news.py` | RSS/Google Newsスキャン |
| **`pages/`** | 8つの独立ページモジュール |

> [!IMPORTANT]
> 旧 `market_app.py` は参照用アーカイブとしてのみ保持。起動は `market_app_nav.py` から行ってください。

## 🏗️ AI システム・アーキテクチャ（Knowledge Transfer 用）

### AI 機能の役割分担（重要）
| 機能 (Tab) | 役割 | 情報源 (Source) |
| :--- | :--- | :--- |
| **🤖 Tab 5: AI Analysis** | **定量データの解釈（分析）** | Cockpit内の数値データ + 必要に応じた補足ニュース。 |
| **📰 Tab 7: Intelligence Hunter**| **定性シグナルの発掘（予兆）** | 金融当局等の一次ソース（.gov, .org, PDF）。ニュースになる前の芽を探す。 |

### 🚀 コア・ロジック
- **Primary Source Mode**: `search_google_news` 関数に `mode='primary'` を実装。ドメイン制限（site:.gov等）と `filetype:pdf` を組み合わせ、メディアのノイズを完全に排除した公式レポート探索を行う。
- **インテリジェンス評価**: AIプロンプトを「ストラテジスト」から「アナリスト」へ。発見価値（Discovery Value）やニュース化確率（News Generalization Prob）を算出。

---

## ✅ 完成済み機能

### 🛸 Primary Source Intelligence Hunter（2026-01-09）
- [x] **一次情報特化検索**: ニュースメディアを排除し、政府・中銀・国際機関の公式資料（PDF）を狙い撃ち。
- [x] **探索モード選択**: 「Pro (一次情報/レポート)」と「General (一般ニュース)」の切り替え。
- [x] **新評価指標**: 発見価値、メディア煽り度、構造的シグナル、ニュース化予見の数値化。
- [x] **Pro Insight**: 難解な一次資料から将来のマーケットを動かす核心を抽出。

### ⚡ 高速起動・パフォーマンス（2026-01-09）
- [x] **ディスクキャッシュ**: `.market_data_cache.pkl` による起動高速化（30秒→5秒）。

### 🆕 AI Global Pulse Search 高度化（2026-01-08）
- [x] Google News RSS 多角的検索、5軸センチメント、X投稿フォーマット、情報鮮度表示。

... (中略) ...

---

## 📝 作業ログ（最新）

| 日時 | 作業内容 |
|-----|---------|
| 2026-01-15 | ✅ **並列データ取得実装**: `utils/data.py` にThreadPoolExecutor導入。FRED/Yahoo同時取得、Release Dates並列化。起動時間 57s→15s（73%改善）。 |
| 2026-01-15 | ✅ **Claude for Desktop + MCP設定**: `claude_desktop_config.json` 作成。Claudeがmarket_monitorフォルダ直接アクセス可能に。 |
| 2026-01-14 | ✅ **Claude修正版統合**: `market_cockpit_pro_fixed.zip` をインポート。`utils.py`, `utils_config.py`, `utils_constants.py` 統合構造に変更。バックアップ: `market_monitor_backup_20260114_032409` |
| 2026-01-13 | ✅ **修正**: M2データ（中国、日本、欧州）を手動更新モード（Configベース）に変更。`config.py`に`MANUAL_GLOBAL_M2`を追加し、FRED取得不可/古い場合に適用。UIに「手動更新」ラベルを追加。 |
| 2026-01-13 | ✅ **修正**: `pages/02_global_money.py` の固定値フォールバックを削除し、データ欠損時は「N/A」等を表示するように変更。 |
| 2026-01-13 | ✅ **修正**: `utils/data.py` (および `data_fetcher.py`) のGlobal M2ハードコードを削除し、FRED参照ロジックに統一。 |
| 2026-01-12 | ✅ **データエクスポート**: ユーザー要望により分割前の `market_app.py` を `market_app_legacy.py` としてデスクトップに出力。 |
| 2026-01-12 | ✅ **アップデート(Zip)**: `market_cockpit_pro_v2.zip` を展開・適用。TTL延長(3600s)、Cryptoページ修正を反映。 |
| 2026-01-12 | ✅ **バグ修正**: `pages/04_crypto.py` の `round(None)` エラーを修正 (`or 0` 追加)。 |
| 2026-01-12 | ✅ **プロジェクト再開**: ユーザー提供の `market_cockpit_pro_v2 (1).zip` (Desktop) をインポート。`main.py` を `market_app_nav.py` に統一。メタデータ復元完了。 |
| 2026-01-12 | ✅ **モジュール化完全完了**: `utils/`パッケージへのロジック分離、100%ロジックパリティ監査、Put/Call Ratio実装、st.navigation修正。 |
| 2026-01-11 | ✅ **ページ分離実装完了**: 全8タブを個別ページファイルに分離（st.navigation()アーキテクチャ）。パフォーマンス大幅改善、メンテナンス性向上。 |
| 2026-01-11 | ✅ Market Voices全自動インテリジェンススキャナー実装。ワンクリックで優先3カテゴリ（中銀・流動性・銀行）を巡回、結果キャッシュ機能付き。 |
| 2026-01-11 | ✅ AI Analysis送信データにマーケットセンチメント追加（VIX、Crypto F&G、AAII Bull-Bear Spread）。display_macro_card()にYoY%チャート追加。 |
| 2026-01-11 | ✅ SEC/Treasury/CFTC等監視対象拡充 + 能動的アラート機能。サイドバーに「Market Alerts」追加、FRB/Treasury/BIS の直近24h発表をRSSチェック。 |
| 2026-01-11 | ✅ UI洗練: サイドバー再構成（AI Focus上部へ移動、Data Health Monitor折りたたみ化）、Sparkline高さ拡大(80→100px) |
| 2026-01-11 | ✅ AI Analysis に送信されるデータを監視項目と自動連動。サイドバーに「AI分析の焦点」セクション追加、選択領域がAIデータの先頭に★マーク付きで表示。既存データ全て保持。 |
| 2026-01-10 | アイコン追加（コックピットデザイン）、ショートカット修正 |
| 2026-01-09 | Market Voices を「Primary Source Intelligence Hunter」へ特化。一次ソース（PDF等）狙い撃ちロジック実装。 |
| 2026-01-09 | ディスクキャッシュ実装による起動高速化（5秒以内）。 |
| 2026-01-08 | AI Global Pulse Search高度化、ADP雇用統計追加、NFP月次変化表示改善。 |
| 2026-01-06 | バリュエーション&レバレッジ指標追加。 |

---

## 🔧 次のステップ案
- [x] ~~能動的アラート機能（一次情報ハンターの常時監視）~~
- [x] ~~クリーンなUIへのさらなる洗練~~
- [ ] 自動スケジュール監視（バックグラウンド実行）
- [ ] プッシュ通知連携（Discord/Slack等）
- [ ] **銀行決算データ監視（2026-01-14発案）**
  - 信用損失引当金（Loan Loss Provisions）: 大手銀行（JPM, BAC, C, WFC）の四半期決算から取得
  - 消費者の健全性を測る「隠れた指標」として有用
  - ソース: The Daily Upside / Morningstar分析
  - 関連指標: クレジットカード平均金利（Bankrate）
