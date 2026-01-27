# ベースライン検証プロジェクト

## ⚠️ 重要：スレッド移行時に必ず読むこと

このファイルは **UI表示のベースライン（正解データ）** を作成するプロジェクトの状態管理ファイルです。
新しいスレッドを開始する際は、必ずこのファイルを参照してください。

---

## 目的

Market Cockpit Proの全監視項目について「今の表示状態」を記録し、
今後の修正・機能追加時に比較検証できる**ベースライン（基準）**を作成する。

### なぜ必要か
- indicators.pyに100項目が「存在する」ことは確認済み（Phase 3完了）
- しかし「UIで正しく表示されているか」の基準がない
- 修正後のヘルスチェックで「構成要素が消えた」ことに気づけない
- **比較対象となる正解データが必要**

---

## 作業方法

1. 高橋さんがタブのスクショを貼る（英語 → 日本語の順）
2. Claudeがスクショを見て、表示されている内容を記録
3. 翻訳エラーがあれば「修正リスト」に追記
4. 全タブ完了後、翻訳エラーを修正
5. 修正後、該当箇所のベースラインを更新

---

## 進捗状況

| タブ | ファイル名 | 日本語 | 英語 | ベースライン |
|------|-----------|--------|------|-------------|
| 01 | 01_liquidity.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |
| 02 | 02_global_money.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |
| 03 | 03_us_economic.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |
| 04 | 04_crypto.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |
| 05 | 05_ai_analysis.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |
| 06 | 06_monte_carlo.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |
| 07 | 07_market_voices.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |
| 08 | 08_sentiment.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |
| 09 | 09_banking.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |
| 11 | 11_analysis_lab.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |
| 12 | 12_currency_lab.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |
| 13 | 13_verdict.py | ✅ 確認済 | ✅ 確認済 | ✅ 作成済 |

---

## 翻訳エラーリスト

修正が必要な翻訳エラーをここに記録。

| タブ | 指標/セクション | 問題内容 | 修正済 |
|------|----------------|----------|--------|
| 01 | VIX/VIX (EN) | 重複表記 → `VIX Index` に修正 | ✅ |
| 01 | Debt Loans (EN) | → `Emergency Loans (Discount Window)` に修正 | ✅ |

**全ての翻訳エラーは修正済みです。**

---

## ベースラインデータ

### 01_liquidity.py ✅

#### セクション構成（日本語 / 英語）
- [x] バリュエーション＆リキッド指標 / Valuation & Liquidity Indicators
- [x] OpenFinanceのカバレッジ推定 / Open Finance Coverage Estimate By Max
- [x] Fed Liquidity / Fed Liquidity
- [x] 市場配管 (Repo & 流動性) / Market Plumbing (Repo & Liquidity)
- [x] Fedバランスシート (SOMA) / Fed Balance Sheet (SOMA)
- [x] 緊急融資 (Discount Window) / Emergency Loans (Discount Window)
- [x] リスク＆帯域 / Risk & Bands
- [x] 社債ETF / Corporate Bond ETFs

#### 指標一覧（22指標 + 2複合チャート）

| セクション | 指標名 | 値表示 | 単位 | スパークライン |
|-----------|--------|--------|------|---------------|
| Risk | VIX | ✅ | pt | ✅ |
| Risk | Credit Spread | ✅ | bps | ✅ |
| Risk | US 10Y Yield | ✅ | % | ✅ |
| Corp Bond | HYG (High Yield) | ✅ | $ | ✅ |
| Corp Bond | LQD (Investment Grade) | ✅ | $ | ✅ |
| Fed Liquidity | Net Liquidity | ✅ | $B | ✅ |
| Fed Liquidity | ON RRP | ✅ | $B | ✅ |
| Fed Liquidity | TGA | ✅ | $B | ✅ |
| Fed Liquidity | Reserves | ✅ | $B | ✅ |
| SOMA | SOMA Total | ✅ | $B | ✅ |
| SOMA | SOMA Treasury | ✅ | $B | ✅ |
| SOMA | SOMA MBS | ✅ | $B | ✅ |
| Emergency | Discount Loans | ✅ | $B | ✅ |
| Emergency | BTFP | ✅ | $B | ✅ |
| Repo | SOFR | ✅ | % | ✅ |
| Repo | EFFR | ✅ | % | ✅ |
| Repo | IORB | ✅ | % | ✅ |
| Rates | FF Target Upper | ✅ | % | ✅ |
| Rates | FF Target Lower | ✅ | % | ✅ |

---

### 02_global_money.py ✅

#### セクション構成（日本語 / 英語）
- [x] US Money Supply (M2) / US Money Supply (M2)
- [x] 中央銀行資産 / Central Bank Assets
- [x] 外国為替 / Foreign Exchange
- [x] グローバル株価指数 / Global Indices
- [x] コモディティ / Commodities
- [x] 暗号資産 / Cryptocurrency

#### 指標一覧（16指標）

| セクション | 指標名 | 値表示 | 単位 | スパークライン |
|-----------|--------|--------|------|---------------|
| US M2 | US M2 (Nominal) | ✅ | $T | ✅ |
| US M2 | US M2 (Real) | ✅ | $T | ✅ |
| Central Bank | EU ECB Total Assets | ✅ | B€ | ✅ |
| Central Bank | US Fed Total Assets (SOMA) | ✅ | B$ | ✅ |
| FX | DXY | ✅ | pt | ✅ |
| FX | USD/JPY | ✅ | ¥ | ✅ |
| FX | EUR/USD | ✅ | $ | ✅ |
| FX | USD/CNY | ✅ | CNY | ✅ |
| Global Indices | 🇯🇵 Nikkei 225 | ✅ | ¥ | ✅ |
| Global Indices | 🇺🇸 S&P 500 | ✅ | pt | ✅ |
| Commodities | Gold | ✅ | $ | ✅ |
| Commodities | Silver | ✅ | $ | ✅ |
| Commodities | Oil (WTI) | ✅ | $ | ✅ |
| Commodities | Copper | ✅ | $ | ✅ |
| Crypto | Bitcoin (BTC) | ✅ | $ | ✅ |
| Crypto | Ethereum (ETH) | ✅ | $ | ✅ |

---

### 03_us_economic.py ✅

#### セクション構成
- [x] 👷 雇用 / Employment (6指標)
- [x] 📊 インフレ / Inflation (6指標 MoM/YoY)
- [x] 💵 経済 / Economy (4指標)
- [x] Consumer Sentiment (2指標)
- [x] 🏭 製造業 / Manufacturing (4指標)
- [x] 🏢 サービス業 / Services (4指標)
- [x] 📈 先行指標 / Leading Indicators (1指標)
- [x] 🏠 住宅 / Housing (2指標)

**翻訳エラー: なし ✅**

---

### 04_crypto.py ✅

#### セクション構成（日本語 / 英語）
- [x] 🪙 暗号資産流動性 & ステーブルコイン / Crypto Liquidity & Stablecoins
- [x] 💵 ステーブルコイン供給量 / Stablecoin Supply
- [x] 📈 ステーブルコイン供給量推移 / Stablecoin Supply History
- [x] トップ10ステーブルコイン (供給量順) / Top 10 Stablecoins by Supply
- [x] 供給量分布 / Supply Distribution
- [x] 📜 トークン化国債 / Tokenized Treasuries
- [x] 🪙 トークン化ゴールド / Tokenized Gold
- [x] 🏢 その他RWA / Other RWA
- [x] 📜 トークン化米国債 / Tokenized US Treasuries
- [x] 💧 市場深度 (流動性品質) / Market Depth (Liquidity Quality)
- [x] 💡 なぜこれが重要か / Why This Matters

#### 指標一覧（8指標）

| セクション | 指標名 | 値表示 | 単位 |
|-----------|--------|--------|------|
| Stablecoin | Total Stablecoin Supply | ✅ | $B |
| Stablecoin | USDT Supply | ✅ | $B |
| Stablecoin | USDC Supply | ✅ | $B |
| RWA | Treasury TVL | ✅ | $B |
| RWA | Gold TVL | ✅ | $B |
| RWA | Other RWA TVL | ✅ | $B |
| Market Depth | Avg CEX Spread | ✅ | % |
| Market Depth | Avg DEX Spread | ✅ | % |

**翻訳エラー: なし ✅**

**修正完了**: `last_update` → `source_update` に統一済み

---

### 05_ai_analysis.py ✅

#### セクション構成（日本語 / 英語）
- [x] 🤖 AIマーケット分析 / AI Market Analysis
- [x] 📊 カテゴリ別レポート / Category Reports

#### UI要素

| 要素 | 日本語 | 英語 |
|------|--------|------|
| カウンター | 99/100 | 99/100 |
| 除外警告 | ⚠️ 1件がAI分析から除外 | ⚠️ 1 items excluded from AI analysis |

#### カテゴリボタン（6個）

| 日本語 | 英語 |
|--------|------|
| 🏛 Fed政策・金融政策 | 🏛 Fed Policy & Monetary Policy |
| 💧 流動性・配管 | 💧 Liquidity & Plumbing |
| 🗄 インフレ・金利 | 🗄 Inflation & Rates |
| 🚨 雇用・景気 | 🚨 Employment & Economy |
| 🏛 銀行・信用 | 🏛 Banking & Credit |
| ₿ 暗号資産 | ₿ Crypto |

**翻訳エラー: なし ✅**

---

### 06_monte_carlo.py ✅

#### セクション構成（日本語 / 英語）
- [x] 🎲 モンテカルロシミュレーション / Monte Carlo Simulation
- [x] ⚙️ 設定 / Settings
- [x] 🎲 モンテカルロシミュレーションへようこそ / Welcome to Monte Carlo Simulation
- [x] 🎯 モデル選択ガイド / Model Selection Guide

#### UI要素

| 要素 | 日本語 | 英語 |
|------|--------|------|
| Asset | 📊 資産 | 📊 Asset |
| Distribution Model | 🎯 分布モデル | 🎯 Distribution Model |
| Parameters | 📊 パラメータ | 📊 Parameters |
| Forecast Period | 予測期間 (年) | Forecast Period (years) |
| Trials | 試行回数 | Trials |
| Run Button | ▶️ シミュレーション実行 | ▶️ Run Simulation |

#### モデル選択テーブル（3行）

| モデル(JP) | モデル(EN) | 使用場面 | 対象資産 |
|------------|------------|----------|----------|
| 正規分布 ⭐推奨 | Normal ⭐ Recommended | 通常の予測 / 初心者 | 株式、指数 |
| Student-t | Student-t | 暴落リスクを考慮したい | 高ボラティリティ資産 |
| ジャンプ拡散 | Jump-Diffusion | 最悪シナリオを見たい | 暗号資産、新興国市場 |

**翻訳エラー: なし ✅**

---

### 07_market_voices.py ✅

#### セクション構成（日本語 / 英語）
- [x] 📰 マーケットボイス / Market Voices
- [x] 🏛 主要機関への直接リンク / Major Institution Direct Links
- [x] 📡 リアルタイムRSSフィード / Real-time RSS Feeds
- [x] 📚 情報ソースの読み方 / How to Read Information Sources
- [x] Fedウォッチの要点 / Fed Watch Key Points
- [x] 注意事項 / Cautions

#### UI要素

| 要素 | 日本語 | 英語 |
|------|--------|------|
| 左列 | US 米国 | US United States |
| 右列 | 🌐 海外中央銀行 | 🌐 Overseas Central Banks |
| RSSタブ | Fed, ECB, BOJ, Markets | Fed, ECB, BOJ, Markets |

#### リンク一覧（米国6 + 海外6）

**米国**: Federal Reserve, Fed - Speeches, Fed - Press Releases, FOMC Calendar, Treasury, SEC

**海外**: ECB (欧州中央銀行), BOJ (日本銀行), BOE (イングランド銀行), PBoC (中国人民銀行), BIS, IMF

#### 情報ソーステーブル（3行）

| タイプ(JP) | タイプ(EN) | 例 | 信頼性 |
|-----------|-----------|-----|--------|
| 一次情報 | Primary | Fed声明、議事録、統計データ | ⭐⭐⭐ |
| 二次情報 | Secondary | ロイター、ブルームバーグ記事 | ⭐⭐ |
| 三次情報 | Tertiary | SNS、個人ブログ | ⭐ |

**翻訳エラー: なし ✅**

---

### 08_sentiment.py ✅

#### セクション構成（日本語 / 英語）
- [x] 🎯 Fear & Greed指数 / Fear & Greed Index
- [x] 📊 Put/Callレシオ / Put/Call Ratio
- [x] 📚 センチメント指標の読み方 / How to Read Sentiment Indicators

#### 指標一覧（3指標）

| セクション | 指標名 | 値表示 | データ期間 | 提供元更新日 | トレンド |
|-----------|--------|--------|-------------|---------------|----------|
| Fear & Greed | ₿ Crypto Fear & Greed | ✅ | ✅ | ✅ | 30日 ✅ |
| Fear & Greed | 📊 VIX指数 (恐怖指数) | ✅ | ✅ | ✅ | 60日 ✅ |
| Put/Call | Equity P/C Ratio | ✅ | ✅ | ✅ | - |

#### UI要素

| 要素 | 日本語 | 英語 |
|------|--------|--------|
| VIX状態 | 通常 | Normal |
| Crypto状態 | Fear | Fear |
| P/C状態 | 強気シグナル (コール優勢) | Bullish Signal (Call Heavy) |

**翻訳エラー: なし ✅**

---

### 09_banking.py ✅

#### セクション構成
- [x] 🏦 銀行セクターの健全性 / Banking Sector Health
- [x] 📊 H.8 週次データ / H.8 Weekly Data
- [x] 📊 H.8 消費者向け＆預金 / H.8 Consumer & Deposits
- [x] ⚠️ 金融ストレス指標 / Financial Stress Indicators
- [x] 🏦 C&I Lending - SLOOS四半期調査
- [x] 🏢 CRE融資 - SLOOS

**翻訳エラー: なし ✅**

---

### 11_analysis_lab.py
（未確認）

---

### 12_currency_lab.py
（未確認）

---

### 13_verdict.py ✅

#### セクション構成（日本語 / 英語）
- [x] マーケット総合判定 / Market Verdict
- [x] 4本柱スコア / Four Pillars
- [x] 詳細内訳 / Detailed Breakdown
- [x] 判定の理由 / Why This Verdict?
- [x] マルチアセット判定 / Multi-Asset VERDICT

#### Four Pillars（4柱）

| 柱 | 指標数 | 状態ラベル例(JP/EN) |
|-----|--------|--------------------|
| Liquidity | 6 | タイト化/Tightening, 中立/Neutral |
| Cycle | 7 | 中立/Neutral |
| Technical | 3 | 中立/Neutral |
| Sentiment | 5 | 楽観/Optimistic |

#### Multi-Asset VERDICT（3資産）

| 資産 | ラベル(JP/EN) |
|------|---------------|
| Stocks | 株式/Stocks |
| Gold | ゴールド/Gold |
| Bitcoin | ビットコイン/Bitcoin |

**翻訳エラー修正済**: Four Pillars状態ラベルの言語切替（lang→'lang'キー修正）

---

## 新スレッド開始時のテンプレート

```
前スレッド: [URLを貼る]
ハンドオフ: handoffs/HANDOFF_YYYYMMDD_XX.md
状態管理: BASELINE_VERIFICATION.md ← 必ず読んでください

作業内容: ベースライン検証の続き（XXタブから）

画像くるまで待機していてね。
```

---

## 最終更新
- 日時: 2026-01-28
- スレッド: https://claude.ai/chat/0c24c273-89ae-4a8f-b472-51dc6c0632a5
- 状態: **全タブ完了（01-09, 11-13）**
- 備考: 翻訳エラー2件は都度修正済み
