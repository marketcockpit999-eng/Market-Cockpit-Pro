# Claude引き継ぎ用ファイル

このフォルダには Market Cockpit Pro の修正作業に必要なファイルが含まれています。

## 📁 ファイル一覧

| ファイル名 | 説明 |
|-----------|------|
| `market_app_nav.py` | 現在のメインエントリーポイント（分割後） |
| `market_app_original.py` | 分割前の元ファイル（参照用） |
| `pages/` | 各タブのページファイル（01〜08） |
| `utils_config.py` | 設定・定数ファイル |
| `utils_constants.py` | 詳細定数・EXPLANATIONS辞書 |
| `MONITORED_ITEMS.md` | 監視対象67項目リスト |

## 📋 Claudeへのプロンプト

以下をコピーしてClaudeに送信してください：

---

以下の修正を行ってください：

1. **🔄 提供元更新日の表示追加**
   - 全67項目（MONITORED_ITEMS.md参照）に対して「🔄 提供元更新日」を表示
   - market_app_original.pyを参考に、抜け漏れを修正

2. **補足説明文の復元**
   - market_app_original.pyに含まれていた詳しい説明文を各指標に復元
   - 特にH4.1関連（Reserves, TGA, ON_RRP等）と金利関連（EFFR, SOFR, IORB等）は詳細に
   - utils_constants.pyのEXPLANATIONS辞書を活用

3. **タイトル位置の修正**
   - 「Market Cockpit Pro v2.0.0 - Modular Edition」を各タブ表示の上（最上部）に移動
   - 現在は各タブ表示の下にあるので修正

market_app_original.pyと分割後のコードを比較し、欠落している機能があれば復元してください。

---

## 🔄 作業後の手順

1. 修正されたファイルをダウンロード
2. 元の場所 (`C:\Users\81802\.gemini\antigravity\scratch\market_monitor\`) に上書きコピー
3. アプリを再起動して確認
