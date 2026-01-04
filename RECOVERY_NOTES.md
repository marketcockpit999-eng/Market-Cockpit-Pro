# Market Cockpit Pro - 開発状況メモ

## 🎯 現在の状況（2025-12-29 22:31）

### ✅ 完成している機能
すべてのメトリクスで**統一されたレイアウト**を実装済み：
- **最新値** + 前日比（メトリック表示）
- **短期トレンド**（60日間のスパークライン）
- **長期トレンド**（2年間のチャート）

完成済みセクション：
- ✅ Net Liquidity vs S&P 500
- ✅ ON RRP, Reserves, TGA
- ✅ Market Plumbing (SRF, SOFR, FIMA, EFFR-IORB)
- ✅ SOMA (Total, Bills, Bills Ratio)
- ✅ Emergency Loans (Total Loans, Primary Credit)
- ✅ Private Banking (Bank Cash, Lending Standards)
- ✅ M2 (Nominal) - 名目通貨供給量
- ⚠️ M2 (Real) - **現在問題あり**

---

## 🔴 M2 (Real) の問題

### 症状
- 画面表示: **0.1 B**（間違い）
- 正しい値: **21.3 B**（21.3兆ドル、インフレ調整後）

### 原因
M2 (Real)は計算が必要な指標：
```python
# market_app.py Line 212-216
if all(c in df.columns for c in ['M2SL', 'CPI']):
    cpi_base = df['CPI'].iloc[0] if not pd.isna(df['CPI'].iloc[0]) else 1
    df['US_Real_M2_Index'] = (df['M2SL'] / df['CPI']) * cpi_base
```

### データ検証結果
実際のFREDデータ（2025-11-01時点）：
- M2SL（名目）: 22,322.4 million → **22.3 B**（千単位変換後） ✅
- CPI: 325.031
- US_Real_M2_Index（計算後）: **21.3 B** ✅

### 修正履歴
1. ✅ Line 752: 単位を "pt" から "B" に修正
2. ✅ Line 752: explanation_key を "M2_Real" に追加
3. ✅ Line 753-755: 長期トレンドチャート追加

### 未解決の問題
**Streamlitキャッシュが古いデータを保持している可能性**

---

## 🛠️ 次回再起動時の対処手順

### 1. M2 (Real)がまだ0.1 Bの場合

#### Step 1: Streamlitキャッシュをクリア
```bash
streamlit run market_app.py
# アプリ起動後、サイドバーの "Force Update" ボタンをクリック
```

#### Step 2: データを直接確認
```bash
python -c "import pandas as pd; import pandas_datareader.data as web; import datetime; end = datetime.datetime.now(); start = end - datetime.timedelta(days=730); m2 = web.DataReader('M2SL', 'fred', start, end, api_key='4e9f89c09658e42a4362d1251d9a3d05'); cpi = web.DataReader('CPIAUCSL', 'fred', start, end, api_key='4e9f89c09658e42a4362d1251d9a3d05'); df = pd.concat([m2, cpi], axis=1).sort_index(); df.columns = ['M2SL', 'CPI']; df['M2SL'] = df['M2SL'] / 1000; cpi_base = df['CPI'].dropna().iloc[0]; df['US_Real_M2_Index'] = (df['M2SL'] / df['CPI'].ffill()) * cpi_base; print('最新のM2データ:'); print(df[['M2SL', 'CPI', 'US_Real_M2_Index']].tail(3))"
```

期待される出力：
```
               M2SL      CPI  US_Real_M2_Index
DATE                                          
2025-09-01  22.2124  324.368         21.214387
2025-10-01  22.2980      NaN         21.296141
2025-11-01  22.3224  325.031         21.275957
```

#### Step 3: 計算ロジックを確認
`market_app.py` の Line 212-216 を確認：
```python
# Calculate Real M2 (M2 adjusted for CPI)
if all(c in df.columns for c in ['M2SL', 'CPI']):
    # Normalize CPI to base 100 at earliest date
    cpi_base = df['CPI'].iloc[0] if not pd.isna(df['CPI'].iloc[0]) else 1
    df['US_Real_M2_Index'] = (df['M2SL'] / df['CPI']) * cpi_base
```

**重要:** M2SLは既にLine 203でBillionsに変換されている：
```python
# Line 202-206
mil_to_bil = ['Fed_Assets', 'TGA', 'Reserves', 'SOMA_Total', 'Bank_Cash', 'SRF', 'FIMA', 'Primary_Credit', 'Total_Loans', 'SOMA_Bills', 'M2SL']
for col in mil_to_bil:
    if col in df.columns:
        df[col] = df[col] / 1000
```

#### Step 4: 表示コード確認
`market_app.py` Line 750-755:
```python
# M2 Real
st.markdown("#### M2 (Real)")
show_metric_with_sparkline("M2 (Real)", df.get('US_Real_M2_Index'), 'US_Real_M2_Index', "B", "M2_Real", notes="インフレ調整後")
if 'US_Real_M2_Index' in df.columns and not df.get('US_Real_M2_Index', pd.Series()).isna().all():
    st.markdown("###### Long-term Trend (過去2年間)")
    st.line_chart(df[['US_Real_M2_Index']], height=200)
```

### 2. デバッグ用スクリプト

`debug_m2_real.py` を作成して実行：
```python
import pandas as pd
import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"
end = datetime.datetime.now()
start = end - datetime.timedelta(days=730)

# Fetch data
m2 = web.DataReader('M2SL', 'fred', start, end, api_key=FRED_API_KEY)
cpi = web.DataReader('CPIAUCSL', 'fred', start, end, api_key=FRED_API_KEY)

# Combine
df = pd.concat([m2, cpi], axis=1).sort_index()
df.columns = ['M2SL', 'CPI']

print("=== 元のデータ（Millions） ===")
print(df.tail(3))
print(f"\nM2SL 最新値: {df['M2SL'].iloc[-1]:,.1f} million")

# Unit conversion (millions to billions)
df['M2SL'] = df['M2SL'] / 1000

print("\n=== 単位変換後（Billions） ===")
print(df.tail(3))
print(f"\nM2SL 最新値: {df['M2SL'].iloc[-1]:.4f} B")

# Calculate Real M2
cpi_base = df['CPI'].dropna().iloc[0]
print(f"\nCPI Base（2年前の値）: {cpi_base:.3f}")

df['US_Real_M2_Index'] = (df['M2SL'] / df['CPI'].ffill()) * cpi_base

print("\n=== Real M2計算後 ===")
print(df[['M2SL', 'CPI', 'US_Real_M2_Index']].tail(3))
print(f"\nUS_Real_M2_Index 最新値: {df['US_Real_M2_Index'].iloc[-1]:.4f} B")

# Verify calculation
latest_m2 = df['M2SL'].iloc[-1]
latest_cpi = df['CPI'].ffill().iloc[-1]
expected_real = (latest_m2 / latest_cpi) * cpi_base
print(f"\n=== 計算検証 ===")
print(f"M2SL: {latest_m2:.4f} B")
print(f"CPI: {latest_cpi:.3f}")
print(f"Real M2 = ({latest_m2:.4f} / {latest_cpi:.3f}) * {cpi_base:.3f}")
print(f"Real M2 = {expected_real:.4f} B")
```

---

## 📊 重要な仕様

### M2の単位
- **M2 (Nominal)**: Billions（B）
- **M2 (Real)**: Billions（B）- インフレ調整後も同じ単位

### 計算式
```
Real M2 = (M2_nominal / CPI_current) × CPI_base
```
- M2_nominal: 名目M2（Billions）
- CPI_current: 現在のCPI
- CPI_base: 2年前（データ開始時点）のCPI

### 期待値（2025年11月時点）
- M2 (Nominal): 22.3 B
- M2 (Real): 21.3 B（約5%のインフレ影響）

---

## 🔧 トラブルシューティング

### 問題: M2 (Real)が0.1 Bと表示される

#### 可能性1: キャッシュ問題
**解決策:** Force Updateボタンをクリック、またはStreamlitを再起動

#### 可能性2: CPI データ取得失敗
**確認方法:**
```python
# Python で直接確認
import pandas_datareader.data as web
import datetime
cpi = web.DataReader('CPIAUCSL', 'fred', datetime.datetime(2023,1,1), datetime.datetime.now(), api_key='4e9f89c09658e42a4362d1251d9a3d05')
print(cpi.tail(5))
```

#### 可能性3: 計算順序の問題
**確認ポイント:**
1. M2SLの単位変換（Line 203-206）が先に実行される
2. その後、Real M2計算（Line 212-216）が実行される
3. forward fill（Line 264）が最後に実行される

---

## 📝 次回のために

エラーが再発したら：
1. このファイル（`RECOVERY_NOTES.md`）を開く
2. "次回再起動時の対処手順" のStep 1から実行
3. `debug_m2_real.py` を実行してデータを確認
4. 問題が解決しない場合は、`market_app.py` Line 212-216 の計算ロジックをデバッグ

**重要:** M2 (Real)は複雑な計算が必要な指標なので、データ取得とキャッシュのタイミングに注意！
