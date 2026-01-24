# 🎯 Market Cockpit Pro

**FRBの流動性とマクロ経済指標をリアルタイム監視する投資家向けダッシュボード**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mcp999.streamlit.app)

---

## 🌟 なぜこのツールが必要か？

投資で成功するには、**中央銀行の流動性**と**マクロ経済サイクル**を理解することが不可欠です。

> "Cash is not king. Liquidity is king." — Michael Howell

Market Cockpit Proは、Ray Dalio、Howard Marks、Stanley Druckenmiller、Michael Howellといった**世界トップの投資家たちの哲学**を統合し、**70以上のマクロ指標**を一画面で監視できるダッシュボードです。

---

## ✨ 主な機能

### 📊 MARKET VERDICT（AI投資判断）
- 3つの柱（流動性40%、サイクル30%、テクニカル30%）で総合スコアを算出
- 株式・債券・ビットコイン・金への投資判断をAIがサポート
- 投資の巨匠たちの視点を統合した分析

### 📈 リアルタイム監視
| カテゴリ | 主な指標 |
|---------|---------|
| FRB流動性 | SOMA、TGA、RRP、準備預金 |
| 金利 | FFレート、SOFR、イールドカーブ |
| マネーサプライ | M2、信用創造 |
| 暗号資産 | ステーブルコイン時価総額、BTC Dominance |

### 🤖 AI市場分析
- Gemini/Claude APIによる自動市場コメンタリー
- 投資の巨匠たちの思考フレームワークを反映

### 📱 マルチデバイス対応
- PC・スマートフォン・タブレットで利用可能
- ホーム画面に追加してネイティブアプリのように使用可能

---

## 🖼️ スクリーンショット

<!-- TODO: スクリーンショットを追加 -->
*Coming soon...*

---

## 🚀 デモを試す

👉 **[Market Cockpit Pro を開く](https://mcp999.streamlit.app)**

---

## 🛠️ ローカルで実行する

### 必要なもの
- Python 3.10以上
- FRED API キー（無料）

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/marketcockpit999-eng/Market-Cockpit-Pro.git
cd Market-Cockpit-Pro

# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定（.envファイルを作成）
echo "FRED_API_KEY=your_api_key_here" > .env

# アプリを起動
streamlit run market_app_nav.py
```

---

## 📚 投資哲学

このツールは以下の投資家たちの考え方を参考にしています：

| 投資家 | 主な視点 |
|--------|---------|
| **Ray Dalio** | 経済マシン、債務サイクル |
| **Howard Marks** | マーケットサイクル、リスク管理 |
| **Stanley Druckenmiller** | 流動性、FRB政策 |
| **Michael Howell** | グローバル流動性 |

---

## 🤝 コミュニティ

流動性分析やFRBウォッチングに興味のある投資家のコミュニティを作っています。

- 📢 今後Discord/Telegramを開設予定
- 💡 アイデアや改善提案は[Issues](https://github.com/marketcockpit999-eng/Market-Cockpit-Pro/issues)へ

---

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

---

## ⭐ スターをお願いします！

このプロジェクトが役に立ったら、ぜひ**スター⭐**をつけてください！
開発のモチベーションになります 🙏

