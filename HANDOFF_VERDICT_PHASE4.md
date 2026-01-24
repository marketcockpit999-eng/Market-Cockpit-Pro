# MARKET VERDICT Phase 4 - WHYセクション実装ガイド
> 次スレッド引き継ぎ用ドキュメント
> 作成日: 2026-01-24

---

## 🎯 Phase 4のゴール

**現状**: VERDICTはスコア（0-100）と内訳を表示するが、「なぜそう判断したか」の説明が不十分

**目標**: 一流投資家の思考プロセスを反映した「WHYレポート」を生成し、ユーザーに判定根拠を明確に伝える

---

## 📚 設計哲学（Thread #1で確定）

VERDICTは以下の一流投資家の**共通エッセンス**を抽出して設計されている：

### 🧠 Ray Dalio（Bridgewater）
- **核心**: マクロ経済サイクルの理解
- **教え**: 「債務サイクルと金融政策のフェーズで資産配分を変える」
- **VERDICT反映**: サイクルスコア（景気の位置づけ判定）

### 🎯 Howard Marks（Oaktree）
- **核心**: 市場サイクルと極端の回避
- **教え**: 「皆が強気の時こそ注意せよ。振り子の位置を知れ」
- **名言**: "You can't predict. You can prepare."
- **VERDICT反映**: センチメントスコア（VIX、AAII、52週位置で過熱/恐怖を検出）

### 💰 Stanley Druckenmiller
- **核心**: 流動性が全てを動かす
- **教え**: 「中央銀行の動きを見ろ。流動性が資産価格を決める」
- **VERDICT反映**: 流動性スコア（Fed資産、Net Liquidity、M2成長）

### 📊 Michael Howell（Capital Wars著者）
- **核心**: 流動性の定量化
- **教え**: グローバル流動性 = 中央銀行資産 + 民間信用創造 - 政府吸収
- **公式**: Net Liquidity = Fed Assets - TGA - ON_RRP
- **VERDICT反映**: 流動性スコアの計算ロジック

### 🔑 共通エッセンス（VERDICTの魂）

```
「相場の方向性は流動性が決める」(Druckenmiller, Howell)
「いつ動くかはサイクルの位置で決める」(Dalio)
「どこまで動くかは極端度で判断する」(Marks)
```

---

## 📋 WHYセクションの要件

### 1. レポート構成案

```
┌─────────────────────────────────────────────┐
│          📊 MARKET VERDICT WHY              │
├─────────────────────────────────────────────┤
│                                             │
│  🎯 総合判定: 強気 (72/100)                 │
│                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                             │
│  💧 流動性が語ること                         │
│  ─────────────────────────────────────────  │
│  Net Liquidityは$6.2兆で過去3年の75%ile。    │
│  Druckenmiller流に言えば「リスクオン環境」。  │
│  ただしTGAが$800Bと高水準、今後の国債発行が   │
│  流動性を吸収する可能性に注意。              │
│                                             │
│  🔄 サイクルが示す位置                       │
│  ─────────────────────────────────────────  │
│  イールドカーブ正常化（+0.3%）、失業率安定、  │
│  製造業指標回復。Dalio流「拡大中期」に相当。  │
│  この局面では株式・シクリカルが好成績を残す   │
│  傾向。                                      │
│                                             │
│  📈 テクニカルの確認                        │
│  ─────────────────────────────────────────  │
│  S&P500は200日MA+8%、52週レンジの82%位置。   │
│  トレンドは上向きだが、短期的には過熱気味。   │
│                                             │
│  📊 センチメントの警告                       │
│  ─────────────────────────────────────────  │
│  VIX 14は楽観を示す。AAII強気/弱気差は+22%。 │
│  Marks流に言えば「振り子がやや楽観側」。     │
│  極端ではないが、追加リスクテイクには慎重に。 │
│                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                             │
│  💡 示唆されるアクション                     │
│  ─────────────────────────────────────────  │
│  • 流動性環境は良好 → 株式ポジション維持     │
│  • サイクル拡大中期 → グロース/シクリカル有効 │
│  • センチメントやや過熱 → 新規買いは分散で    │
│  • 次の注目: FOMC（2/1）、TGA動向            │
│                                             │
└─────────────────────────────────────────────┘
```

### 2. 生成ロジック要件

| セクション | 入力データ | 生成ロジック |
|-----------|-----------|-------------|
| 流動性解説 | Net Liq, TGA, RRP, M2 | パーセンタイル + 変化方向 + Druckenmiller/Howell視点 |
| サイクル解説 | T10Y2Y, UNRATE, 製造業指標 | 6段階サイクル位置 + Dalio視点 |
| テクニカル解説 | MA乖離, RSI, 52週位置 | トレンド強度 + 過熱度 |
| センチメント解説 | VIX, AAII, 52週位置 | Marks流「振り子位置」判定 |
| アクション示唆 | 4柱の総合 | 条件分岐でテンプレート選択 |

### 3. 実装ファイル案

```
utils/
├── verdict_why.py          # ← 新規作成：WHYレポート生成ロジック
│   ├── generate_why_report(verdict_data) → str
│   ├── explain_liquidity(pillar_data) → str
│   ├── explain_cycle(pillar_data) → str
│   ├── explain_technical(pillar_data) → str
│   ├── explain_sentiment(pillar_data) → str
│   └── suggest_actions(verdict_data) → list[str]
│
pages/
└── 13_verdict.py           # ← 修正：WHYセクション表示追加
    └── render_why_section(verdict) を追加
```

---

## 🔧 実装ステップ

### Step 1: verdict_why.py 作成
- 各柱の解説文生成関数
- 一流投資家の視点を埋め込んだテンプレート
- 日本語/英語対応（t()関数使用）

### Step 2: i18n.py 更新
- WHYセクション用の翻訳キー追加
- 投資家名（Dalio, Marks等）は固有名詞なので翻訳不要

### Step 3: 13_verdict.py 更新
- render_why_section() 関数追加
- スコア表示の下にWHYレポートを表示

### Step 4: テスト
- 各種スコアパターンで適切な解説が生成されるか確認
- 極端な値（0, 100付近）でも自然な文章になるか確認

---

## 📝 テンプレート例（日本語）

### 流動性セクション

```python
def explain_liquidity(pillar: dict) -> str:
    score = pillar['score']
    details = pillar['details']
    net_liq = details.get('net_liquidity', {})
    
    # スコアレベルに応じたテンプレート
    if score >= 70:
        template = """
**💧 流動性は「追い風」**

Net Liquidityは${net_liq_val:.1f}兆ドル（過去3年の{percentile}%ile）。
{druckenmiller_quote}

{tga_warning}
"""
    elif score >= 50:
        template = """
**💧 流動性は「中立」**

Net Liquidityは${net_liq_val:.1f}兆ドル。
特段の追い風も向かい風もない状況。
{tga_status}
"""
    else:
        template = """
**💧 流動性に「黄信号」**

Net Liquidityは${net_liq_val:.1f}兆ドルと低水準。
{howell_warning}

{reserves_status}
"""
    
    # Druckenmiller/Howell視点の引用
    druckenmiller_quotes = {
        'bullish': "Druckenmiller流に言えば「流動性が味方についている」状況。",
        'neutral': "流動性の観点からは中立的な環境。",
        'bearish': "流動性縮小は資産価格の重石になりやすい。"
    }
    
    return template.format(...)
```

### センチメントセクション（Howard Marks視点）

```python
def explain_sentiment(pillar: dict) -> str:
    score = pillar['score']
    details = pillar['details']
    
    # Marks流「振り子」の位置判定
    if score >= 75:
        pendulum = "振り子は「恐怖側」に大きく振れている"
        marks_insight = "Marks曰く「恐怖が支配する時こそ買い場」"
    elif score >= 55:
        pendulum = "振り子は「中立〜やや恐怖」"
        marks_insight = "慎重な楽観が許容される環境"
    elif score >= 35:
        pendulum = "振り子は「楽観側」に傾いている"  
        marks_insight = "Marks曰く「皆が楽観的な時は注意せよ」"
    else:
        pendulum = "振り子は「過度な楽観」を示す"
        marks_insight = "逆張りの準備をすべき局面かもしれない"
    
    return f"""
**📊 センチメント - {pendulum}**

VIXは{vix:.1f}、AAIIブル/ベア差は{aaii_spread:+.0f}%。

{marks_insight}

{extreme_warning if is_extreme else ''}
"""
```

---

## ⚠️ 注意点

### やってはいけないこと
1. **投資助言と受け取られる表現を避ける**
   - ❌「今すぐ買うべき」
   - ✅「この環境では株式に追い風」

2. **断定的な予測を避ける**
   - ❌「来月は上昇する」
   - ✅「過去のパターンでは上昇傾向」

3. **個別銘柄への言及を避ける**
   - セクター/資産クラスレベルに留める

### 必須の免責表示
```
⚠️ 本分析は情報提供を目的としたものであり、
投資助言ではありません。投資判断は自己責任で行ってください。
```

---

## 🗂️ 関連ファイル

| ファイル | 役割 |
|---------|------|
| `utils/verdict_main.py` | 統合スコア計算 |
| `utils/verdict_liquidity.py` | 流動性スコア |
| `utils/verdict_cycle.py` | サイクルスコア |
| `utils/verdict_technical.py` | テクニカルスコア |
| `utils/verdict_sentiment.py` | センチメントスコア |
| `pages/13_verdict.py` | UI表示 |
| `utils/i18n.py` | 翻訳キー |

---

## 📜 前スレッド履歴

| # | 日付 | URL | 内容 |
|---|------|-----|------|
| 1 | 01-23 | https://claude.ai/chat/ee4ad37a-e43c-437f-8b20-bf9d0f0b1121 | 構想・設計哲学確定 |
| 2-3 | 01-23 | https://claude.ai/project/019bb281-b291-72ad-85c0-ceecab814cb7 | Phase 1-2.6 実装 |
| 5 | 01-23 | https://claude.ai/chat/3f892a96-3a63-45f0-a7b6-c880938d12f1 | Phase 3 UI完成 |

---

## ✅ 次スレッドでの作業チェックリスト

- [ ] `utils/verdict_why.py` 作成
- [ ] `utils/i18n.py` にWHYセクション翻訳キー追加
- [ ] `pages/13_verdict.py` にWHYセクション表示追加
- [ ] 各スコアレベルでの出力テスト
- [ ] 日本語/英語切り替えテスト
- [ ] git commit & push

---

**質問があれば次のスレッドで聞いてください！** 🚀
