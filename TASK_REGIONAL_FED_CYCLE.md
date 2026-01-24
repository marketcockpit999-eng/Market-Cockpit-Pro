# 🎯 タスク: 地区連銀8指標を Market Verdict の Cycle スコアに統合

## 背景
- 地区連銀8指標は indicators.py に既に定義済み
- ISM PMI の代替として Cycle スコアに組み込む
- 製造業4つ → Manufacturing Composite
- サービス業4つ → Services Composite

## 追加する指標（全て indicators.py に定義済み）

| 製造業（Manufacturing） | サービス業（Services） |
|------------------------|----------------------|
| Empire_State_Mfg | NY_Fed_Services |
| Philly_Fed_Mfg | Philly_Fed_Services |
| Dallas_Fed_Mfg | Dallas_Fed_Services |
| Richmond_Fed_Mfg | Richmond_Fed_Services |

## 新しい Cycle 構成

```
【変更前】                    【変更後】
イールドカーブ × 35%    →    イールドカーブ × 30%
失業率 × 25%            →    失業率 × 20%
信用スプレッド × 25%    →    信用スプレッド × 20%
Leading Index × 15%     →    Leading Index × 10%
                             Manufacturing Composite × 10%  ← NEW
                             Services Composite × 10%       ← NEW
```

---

## ⚠️ 絶対に守るルール

1. **verdict_liquidity.py には触らない**
2. **verdict_technical.py には触らない**
3. **verdict_sentiment.py には触らない**
4. **verdict_main.py の重み配分には触らない**（Cycle全体の25%は維持）
5. 既存の4指標のロジックは変更しない - **重みのみ調整**

---

## 実装ステップ

### Step 1: pages/13_verdict.py の修正

#### 1-1: prepare_verdict_data() の cycle_keys を拡張

場所: `prepare_verdict_data()` 関数内

```python
# 【変更前】
cycle_keys = ['T10Y2Y', 'UNRATE', 'Credit_Spread', 'Leading_Index', 'CFNAI']

# 【変更後】
cycle_keys = [
    'T10Y2Y', 'UNRATE', 'Credit_Spread', 'Leading_Index', 'CFNAI',
    # Regional Fed Manufacturing
    'Empire_State_Mfg', 'Philly_Fed_Mfg', 'Dallas_Fed_Mfg', 'Richmond_Fed_Mfg',
    # Regional Fed Services
    'NY_Fed_Services', 'Philly_Fed_Services', 'Dallas_Fed_Services', 'Richmond_Fed_Services',
]
```

#### 1-2: render_pillar_details() の indicator_names に追加

場所: `render_pillar_details()` 関数内の `indicator_names` 辞書

```python
# 既存の項目の後に追加
'mfg_composite': t('verdict_ind_mfg_composite'),
'svc_composite': t('verdict_ind_svc_composite'),
```

#### 1-3: render_pillar_details() の値フォーマット処理を追加

場所: 値表示の elif チェーン内

```python
elif key in ['mfg_composite', 'svc_composite']:
    val_str = f"{val:+.1f}" if val is not None else "-"
```

---

### Step 2: utils/verdict_cycle.py の修正

#### 2-1: 新しいスコア関数を追加（calculate_cycle_score の前に追加）

```python
def score_manufacturing_composite(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    地区連銀製造業指数のCompositeスコア
    
    各指数: 0超=拡大、0未満=縮小
    範囲: 約-40 ～ +40 を 0-100 にマップ
    """
    mfg_keys = ['Empire_State_Mfg', 'Philly_Fed_Mfg', 'Dallas_Fed_Mfg', 'Richmond_Fed_Mfg']
    values = []
    
    for key in mfg_keys:
        item = data.get(key)
        if item is None:
            continue
        if isinstance(item, pd.Series) and len(item) > 0:
            val = item.iloc[-1]
        elif isinstance(item, (int, float)):
            val = float(item)
        else:
            continue
        if not pd.isna(val):
            values.append(val)
    
    if len(values) == 0:
        return None, {'available': 0, 'average': None}
    
    avg = np.mean(values)
    # -40 ～ +40 を 0-100 にマップ（0 → 50）
    score = 50 + (avg / 40) * 50
    score = float(np.clip(score, 0, 100))
    
    return score, {'available': len(values), 'average': avg}


def score_services_composite(data: Dict[str, Any]) -> Tuple[Optional[float], Dict]:
    """
    地区連銀サービス業指数のCompositeスコア
    """
    svc_keys = ['NY_Fed_Services', 'Philly_Fed_Services', 'Dallas_Fed_Services', 'Richmond_Fed_Services']
    values = []
    
    for key in svc_keys:
        item = data.get(key)
        if item is None:
            continue
        if isinstance(item, pd.Series) and len(item) > 0:
            val = item.iloc[-1]
        elif isinstance(item, (int, float)):
            val = float(item)
        else:
            continue
        if not pd.isna(val):
            values.append(val)
    
    if len(values) == 0:
        return None, {'available': 0, 'average': None}
    
    avg = np.mean(values)
    score = 50 + (avg / 40) * 50
    score = float(np.clip(score, 0, 100))
    
    return score, {'available': len(values), 'average': avg}
```

#### 2-2: calculate_cycle_score() の details 辞書を修正

```python
# 【変更前】
details = {
    'yield_curve': {'value': None, 'score': None, 'weight': 0.35},
    'unemployment': {'value': None, 'score': None, 'weight': 0.25},
    'credit_spread': {'value': None, 'score': None, 'weight': 0.25},
    'leading_index': {'value': None, 'score': None, 'weight': 0.15},
    'components_available': 0,
    'data_quality': 'unknown'
}

# 【変更後】
details = {
    'yield_curve': {'value': None, 'score': None, 'weight': 0.30},
    'unemployment': {'value': None, 'score': None, 'weight': 0.20},
    'credit_spread': {'value': None, 'score': None, 'weight': 0.20},
    'leading_index': {'value': None, 'score': None, 'weight': 0.10},
    'mfg_composite': {'value': None, 'score': None, 'weight': 0.10},
    'svc_composite': {'value': None, 'score': None, 'weight': 0.10},
    'components_available': 0,
    'data_quality': 'unknown'
}
```

#### 2-3: 各セクションの重みを更新

```python
# yield_curve セクション
weighted_sum += score * 0.35  →  weighted_sum += score * 0.30
total_weight += 0.35          →  total_weight += 0.30

# unemployment セクション
weighted_sum += score * 0.25  →  weighted_sum += score * 0.20
total_weight += 0.25          →  total_weight += 0.20

# credit_spread セクション
weighted_sum += score * 0.25  →  weighted_sum += score * 0.20
total_weight += 0.25          →  total_weight += 0.20

# leading_index セクション
weighted_sum += score * 0.15  →  weighted_sum += score * 0.10
total_weight += 0.15          →  total_weight += 0.10
```

#### 2-4: 新しいセクションを追加（leading_index の後、総合スコア計算の前）

```python
    # --- 5. Manufacturing Composite (10%) ---
    mfg_score, mfg_info = score_manufacturing_composite(data)
    if mfg_score is not None:
        details['mfg_composite']['value'] = mfg_info['average']
        details['mfg_composite']['score'] = mfg_score
        details['mfg_composite']['available'] = mfg_info['available']
        weighted_sum += mfg_score * 0.10
        total_weight += 0.10
        details['components_available'] += 1
    
    # --- 6. Services Composite (10%) ---
    svc_score, svc_info = score_services_composite(data)
    if svc_score is not None:
        details['svc_composite']['value'] = svc_info['average']
        details['svc_composite']['score'] = svc_score
        details['svc_composite']['available'] = svc_info['available']
        weighted_sum += svc_score * 0.10
        total_weight += 0.10
        details['components_available'] += 1
```

---

### Step 3: utils/i18n.py に翻訳キーを追加

```python
'verdict_ind_mfg_composite': {'en': 'Manufacturing Composite', 'ja': '製造業総合'},
'verdict_ind_svc_composite': {'en': 'Services Composite', 'ja': 'サービス業総合'},
```

---

## 検証手順

1. アプリを起動
2. Market Verdict ページを開く
3. 🔄 Cycle の Breakdown を展開
4. 確認事項：
   - 6つの指標が表示されること
   - Manufacturing Composite と Services Composite が追加されていること
   - 重みが正しいこと（30%, 20%, 20%, 10%, 10%, 10%）
   - エラーが出ないこと
5. 他の柱（Liquidity, Technical, Sentiment）に影響がないこと

---

## ロールバック手順

問題が発生した場合：
```bash
git checkout -- utils/verdict_cycle.py
git checkout -- pages/13_verdict.py
git checkout -- utils/i18n.py
```

---

## 修正対象ファイル一覧

| ファイル | 修正内容 |
|---------|---------|
| pages/13_verdict.py | cycle_keys拡張、indicator_names追加、値フォーマット追加 |
| utils/verdict_cycle.py | 新関数2つ追加、details拡張、重み変更、新セクション追加 |
| utils/i18n.py | 翻訳キー2つ追加 |
