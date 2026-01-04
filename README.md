# Market Cockpit Pro - 完全ガイド

**最終更新**: 2026年1月4日  
**場所**: `C:\Users\81802\.gemini\antigravity\scratch\market_monitor\`

---

## 🚀 起動方法

```powershell
cd C:\Users\81802\.gemini\antigravity\scratch\market_monitor
streamlit run market_app.py
```

---

## 📊 現在の機能（完成済み）

### Tab 1: Liquidity & Rates
| セクション | 機能 |
|-----------|------|
| Net Liquidity vs S&P 500 | 流動性と株価の相関 |
| ON RRP, Reserves, TGA | FRBバランスシート構成要素 |
| Market Plumbing | SOFR, SRF, FIMA, Credit Spreads |
| SOMA | 総保有額、Bills比率、RMPアラート |
| Emergency Loans | ディスカウントウィンドウ、緊急融資 |
| Private Banking | 銀行現金、貸出態度（SLOOS） |
| M2 | 名目・実質通貨供給量 |

### Tab 2: Macro & Markets
| セクション | 機能 |
|-----------|------|
| 経済指標 | 失業率、CPI、Core PCE |
| FX | ドル指数、USD/JPY、EUR/USD |
| コモディティ | 原油、銅、金 |
| 暗号通貨 | BTC、ETH |

### Tab 3: AI Analysis
| 機能 | 説明 |
|------|------|
| Gemini分析 | Google AIによる市場分析 |
| Claude分析 | Anthropic AIによる市場分析 |
| データフレッシュネス | データ鮮度の監視 |

### 中国クレジットインパルス
- プロキシ指標として実装
- M2増加率ベース

---

## 🔧 重要な設定

### APIキー（.envファイル）

```
GEMINI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx
FRED_API_KEY=4e9f89c09658e42a4362d1251d9a3d05
```

### 不変のルール（PROJECT_RULES.md参照）

1. **外科手術的修正** - 必要な行だけを変更
2. **UIコンテキスト保護** - 説明文やタブ構造を消さない
3. **単位の正規化** - Million → Billion に変換
4. **日付表示** - 実際のデータ日付を表示（今日ではない）

---

## ⚠️ 既知の注意点

### M2 (Real) の計算

```python
Real M2 = (M2_nominal / CPI_current) × CPI_base
```

キャッシュ問題で0.1 Bと表示される場合がある。
→ 詳細は `RECOVERY_NOTES.md` 参照

### SOMA Bills

FREDに直接データがないため、H.4.1レポートから手動取得する仕組みあり。

---

## 📁 ファイル構成

### 重要ファイル
| ファイル | 役割 |
|---------|------|
| `market_app.py` | メインアプリ（2351行） |
| `.env` | APIキー（機密） |
| `PROJECT_RULES.md` | 開発ルール（不変） |
| `RECOVERY_NOTES.md` | トラブルシューティング |
| `PROJECT_STATE.md` | プロジェクト状態（この下に統合） |

### データファイル
| ファイル | 役割 |
|---------|------|
| `market_monitor_log.csv` | ログデータ |
| `market_data_v3.csv` | 保存された市場データ |
| `manual_h41_data.csv` | 手動入力H.4.1データ |

### デバッグ用（必要時のみ）
- `debug_*.py` - 各種デバッグスクリプト
- `test_*.py` - テストスクリプト

### レポート（参考資料）
- `*.pdf` - Gemini DeepResearchレポート

---

## 📝 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-01-04 | ドキュメント統合・整理 |
| 2026-01-02 | PROJECT_STATE.md作成 |
| 2025-12-31 | 中国クレジットインパルス追加 |
| 2025-12-30 | データフレッシュネス監視実装 |
| 2025-12-29 | デュアルAI分析（Gemini/Claude）実装 |
| 2025-12-28 | 統一レイアウト完成 |

---

## 🎯 次にやること候補

1. [ ] データフレッシュネス監視の改善
2. [ ] 中国クレジットインパルス表示の洗練
3. [ ] エラーハンドリング強化
4. [ ] パフォーマンス最適化

---

## 🔍 クイックリファレンス

### よく使うコマンド

```powershell
# アプリ起動
streamlit run market_app.py

# キャッシュクリア起動
streamlit run market_app.py --server.fileWatcherType none

# デバッグ
python debug_m2_real.py
```

### トラブル時

1. まず `RECOVERY_NOTES.md` を確認
2. Force Update ボタンをクリック
3. Streamlit再起動
4. デバッグスクリプト実行

---

## 💡 AIへの引継ぎメモ

次回このプロジェクトを触る時のために：

1. **このファイルを最初に読む** - 全体像の把握
2. **PROJECT_RULES.md** - 絶対守るルール
3. **RECOVERY_NOTES.md** - M2 Realの問題など詳細
4. **market_app.py** - メインコード（2351行、慎重に編集）

**重要**: ユーザーは「おっさん」と自称しているが、金融市場に詳しく、品質への目が厳しい。UIの変更は慎重に、必ず確認を取ること。
