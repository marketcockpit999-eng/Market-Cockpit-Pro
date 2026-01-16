# Market Cockpit Pro - Regression Test Framework

## 概要

このテストフレームワークは3つの目標を達成します：

1. ✅ **意図しない変更の検出** - コード修正時のリグレッションを防止
2. ✅ **API呼び出しなしで即座に実行** - オフラインテストで高速フィードバック
3. ✅ **指標数・必須列・計算式の検証** - データ整合性を保証

## ファイル構成

```
tests/
├── specs/
│   ├── __init__.py
│   └── expected_indicators.py   # マスター定義（変更時は要コメント）
├── __init__.py
├── validate_structure.py        # 構造検証（API不要・即座に完了）
├── test_calculations.py         # 計算ロジック検証（API不要）
└── test_indicator_count.py      # 実データ検証（API必要）

run_tests.py                     # 統合テストランナー
pytest.ini                       # pytest設定
```

## 実行方法

### オフラインテスト（推奨・高速）

```bash
# 全オフラインテスト実行
python run_tests.py

# 個別実行
python tests/validate_structure.py
python tests/test_calculations.py

# pytestで実行
python -m pytest tests/validate_structure.py tests/test_calculations.py -v
```

### 実データテスト（API必要）

```bash
# APIテストも含む全テスト
python run_tests.py --all

# APIテストのみ
python run_tests.py --api

# 個別実行
python tests/test_indicator_count.py
```

## テスト内容

### 1. validate_structure.py（オフライン）

- `constants.py`の定義数チェック（FRED/Yahoo指標）
- 期待されるキーの存在確認
- `pages/`ディレクトリのファイル存在確認
- `utils/`モジュールのインポート確認
- Net Liquidity計算式のコード内検証
- `DATA_FRESHNESS_RULES`の完全性検証

### 2. test_calculations.py（オフライン）

- モックデータを使用した計算ロジック検証
- Net Liquidity計算: `Fed_Assets - TGA - ON_RRP - SRF - FIMA`
- Bills Ratio計算: `(SOMA_Bills / SOMA_Total) * 100`
- エッジケース（ゼロ値）の検証
- 計算結果の型・NaN/Inf検証

### 3. test_indicator_count.py（API必要）

- 実データでの必須列存在確認
- 指標数の期待値チェック
- Net Liquidity/Bills Ratio計算値の検証

## マスター定義の更新

`tests/specs/expected_indicators.py`を変更する場合：

1. **変更履歴にコメントを追加**
   ```python
   # 2026-01-16: v1.2 - 新指標追加（理由）
   ```

2. **期待値を更新**
   ```python
   EXPECTED_INDICATOR_COUNT = 70  # 2026-01-16: 3指標追加
   ```

3. **テストを実行して検証**
   ```bash
   python run_tests.py --all
   ```

## トラブルシューティング

### ImportError: No module named 'utils'

プロジェクトルートから実行してください：
```bash
cd market_monitor
python tests/validate_structure.py
```

### API呼び出しエラー

- キャッシュファイル `.market_data_cache.pkl` が古い場合は削除
- FRED APIキーの有効性を確認

### テスト失敗時

1. `❌ FAIL`のメッセージを確認
2. 意図した変更なら `expected_indicators.py` を更新
3. 意図しない変更ならコードを修正

## CI/CD統合

GitHubActionsなどでの自動テスト例：

```yaml
- name: Run offline tests
  run: |
    python run_tests.py
```

フルテスト（API含む）：

```yaml
- name: Run all tests
  env:
    FRED_API_KEY: ${{ secrets.FRED_API_KEY }}
  run: |
    python run_tests.py --all
```
