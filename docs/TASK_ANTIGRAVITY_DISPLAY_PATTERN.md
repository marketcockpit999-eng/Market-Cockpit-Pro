# Antigravity タスク指示書
# display_pattern プロパティの一括追加

## ⚠️ 重要な注意事項

**絶対にやってはいけないこと：**
- 既存のプロパティを削除・変更しない
- ファイル構造を変更しない
- 新しいファイルを作成しない（このタスクでは）
- 指示にない項目を追加しない

**やること：**
- `utils/indicators.py` の各項目に `'display_pattern': 'xxx',` を1行追加するだけ

---

## タスク概要

`utils/indicators.py` の INDICATORS 辞書内の100項目すべてに `display_pattern` プロパティを追加する。

---

## パターン割り当て一覧

### パターン1: `mom_yoy` （6項目）
MoM%/YoY%計算が必要な項目。`display_macro_card()`で表示。

```
CPI
CPICore
CorePCE
PPI
RetailSales
ConsumerSent
```

### パターン2: `manual_calc` （6項目）
個別計算ロジックが必要な項目。`st.metric`直接使用。

```
NFP
UNRATE
AvgHourlyEarnings
ICSA
RealGDP
ADP
```

### パターン3: `web_scrape` （2項目）
Webスクレイピングで取得。source='WEB'の項目。

```
Richmond_Fed_Mfg
Richmond_Fed_Services
```

### パターン4: `calculated` （1項目）
複数指標から計算。source='CALCULATED'の項目。

```
Global_Liquidity_Proxy
```

### パターン5: `api` （12項目）
外部API経由で取得。`df_stored: False`の項目。

```
SP500_PE
NASDAQ_PE
BTC_Funding_Rate
BTC_Open_Interest
BTC_Long_Short_Ratio
ETH_Funding_Rate
ETH_Open_Interest
Stablecoin_Total
Treasury_TVL
Gold_TVL
Crypto_Fear_Greed
CNN_Fear_Greed
```

### パターン6: `standard` （残り73項目）
上記以外のすべての項目。`show_metric_with_sparkline()`で表示。

---

## 実装方法

### 推奨：Pythonスクリプトで一括追加

```python
# add_display_pattern.py
import re

PATTERN_MAP = {
    # mom_yoy (6)
    'CPI': 'mom_yoy',
    'CPICore': 'mom_yoy',
    'CorePCE': 'mom_yoy',
    'PPI': 'mom_yoy',
    'RetailSales': 'mom_yoy',
    'ConsumerSent': 'mom_yoy',
    
    # manual_calc (6)
    'NFP': 'manual_calc',
    'UNRATE': 'manual_calc',
    'AvgHourlyEarnings': 'manual_calc',
    'ICSA': 'manual_calc',
    'RealGDP': 'manual_calc',
    'ADP': 'manual_calc',
    
    # web_scrape (2)
    'Richmond_Fed_Mfg': 'web_scrape',
    'Richmond_Fed_Services': 'web_scrape',
    
    # calculated (1)
    'Global_Liquidity_Proxy': 'calculated',
    
    # api (12)
    'SP500_PE': 'api',
    'NASDAQ_PE': 'api',
    'BTC_Funding_Rate': 'api',
    'BTC_Open_Interest': 'api',
    'BTC_Long_Short_Ratio': 'api',
    'ETH_Funding_Rate': 'api',
    'ETH_Open_Interest': 'api',
    'Stablecoin_Total': 'api',
    'Treasury_TVL': 'api',
    'Gold_TVL': 'api',
    'Crypto_Fear_Greed': 'api',
    'CNN_Fear_Greed': 'api',
}

def get_pattern(name):
    return PATTERN_MAP.get(name, 'standard')

def add_display_patterns(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    current_indicator = None
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 指標名を検出: '指標名': {
        match = re.match(r"(\s+)'([A-Za-z0-9_]+)':\s*\{", line)
        if match:
            current_indicator = match.group(2)
        
        # 閉じ括弧を検出: },
        if line.strip() == '},' and current_indicator:
            # 前の行にdisplay_patternがなければ追加
            if 'display_pattern' not in new_lines[-1]:
                pattern = get_pattern(current_indicator)
                new_lines.append(f"        'display_pattern': '{pattern}',")
            current_indicator = None
        
        new_lines.append(line)
        i += 1
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

if __name__ == '__main__':
    filepath = r'C:\Users\81802\.gemini\antigravity\scratch\market_monitor\utils\indicators.py'
    add_display_patterns(filepath)
    print("完了")
```

---

## 検証方法

追加後、以下のスクリプトで検証：

```python
# verify_display_pattern.py
from utils.indicators import INDICATORS

# 全項目にdisplay_patternがあるか確認
missing = []
for name, info in INDICATORS.items():
    if 'display_pattern' not in info:
        missing.append(name)

if missing:
    print(f"❌ display_pattern未設定: {len(missing)}項目")
    for name in missing:
        print(f"  - {name}")
else:
    print(f"✅ 全{len(INDICATORS)}項目にdisplay_pattern設定済み")

# パターン別集計
from collections import Counter
patterns = Counter(v.get('display_pattern') for v in INDICATORS.values())
print("\nパターン別集計:")
for pattern, count in sorted(patterns.items()):
    print(f"  {pattern}: {count}")
```

### 期待される出力

```
✅ 全100項目にdisplay_pattern設定済み

パターン別集計:
  api: 12
  calculated: 1
  manual_calc: 6
  mom_yoy: 6
  standard: 73
  web_scrape: 2
```

---

## 完了条件

1. `utils/indicators.py` の100項目すべてに `display_pattern` がある
2. 検証スクリプトが期待通りの出力を返す
3. 既存のプロパティが変更されていない
4. アプリが正常に起動する（`streamlit run market_app_nav.py`）

---

## 補足：既に追加済みの項目

Claudeが途中まで手動で追加した項目があります（約9項目）。
スクリプトは「既にdisplay_patternがある場合はスキップ」するので問題ありません。
