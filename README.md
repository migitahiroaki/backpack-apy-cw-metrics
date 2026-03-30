# Backpack APY CW Metrics

## Lambda デプロイ手順

### ローカルテスト用の依存関係インストール

ローカルでのテストには、開発依存関係をインストールしてください。

```bash
pip install -r requirements-dev.txt
```

### 1. ZIP ファイルの作成

本番デプロイでは、Lambda のデフォルトライブラリのみを使用するため、依存関係のインストールは不要です。`src/` ディレクトリ自身を含めて ZIP 化し、`__pycache__` は除外します。

- スクリプト `package_python_lambda.sh` を利用する場合:
  - 実行権限を付与: `chmod +x ./package_python_lambda.sh`
  - 実行: `./package_python_lambda.sh`

### 2. Lambda コンソールでの設定

1. AWS Lambda コンソールを開きます。
2. 新しい関数を作成するか、既存の関数を選択します。
3. **ランタイム** を Python 3.x (例: Python 3.13) に設定します。
4. **ハンドラー** を `src.app.lambda_handler` に設定します。
   - これにより、ZIP ファイル内の `src/app.py` の `lambda_handler` 関数がエントリポイントとして使用されます。
5. ZIP ファイルをアップロードします。
6. 環境変数を設定します。 BORROW_SYMBOLS と LEND_SYMBOLS 少なくともどちらか一方を設定してください。メトリクス数に比例してCWのか金額が上がるので注意してください。
   - `BORROW_SYMBOLS`: 借入対象の通貨シンボル（カンマ区切り、例: "BTC,ETH"）
   - `LEND_SYMBOLS`: 貸出対象の通貨シンボル（カンマ区切り、例: "USDC,USDT"）
   - `API_URL`: Backpack API エンドポイント（オプション、デフォルト: "https://api.backpack.exchange/api/v1/borrowLend/apy"）
   - `CLOUDWATCH_NAMESPACE`: CloudWatch メトリクス名前空間（オプション、デフォルト: "Backpack/Lending"）
7. 関数を保存してテストします。

### 注意事項

- `src/` ディレクトリ内のファイルのみを ZIP に含めてください。
- 本番デプロイでは Lambda のデフォルトライブラリのみを使用するため、追加の依存関係インストールは不要です。
- ローカルテストでは `requirements-dev.txt` の依存関係をインストールしてください。
- Lambda のタイムアウトやメモリ設定を適切に調整してください。