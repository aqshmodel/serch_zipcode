# 郵便番号から住所を検索するPythonアプリ

[zipcloud 郵便番号検索API](https://zipcloud.ibsnet.co.jp/doc/api) を使い、7桁の郵便番号から都道府県・市区町村・町域を取得します。

## 動作環境

- Python 3.12 以降を推奨（3.12 / 3.13 でCIテスト）
- 追加のPythonパッケージは不要です（標準ライブラリのみ）。`pip install` / `pipenv install` も不要です。

## 実行方法

```bash
python app.py
```

他のコードから使用する場合：

```python
from app import search_address

print(search_address("0287405"))
print(search_address("028-7405"))
```

無効な郵便番号では `ValueError`、APIへの接続失敗・検索結果なし・異常な応答では `AddressLookupError` を返します。

## テスト

```bash
python -m unittest discover -s tests -v
```

テストはネットワークに接続せずに実行できます。GitHub ActionsでPython 3.12 / 3.13を検証します。

## セキュリティ

- API通信はHTTPSを使用し、証明書検証を無効化しません。リダイレクトも許可しません。
- 郵便番号を7桁の半角数字（または `123-4567`）に制限します。
- 通信タイムアウト（10秒）とレスポンスサイズ上限（64KiB）を設定しています。
- 旧版の `Pipfile` / `Pipfile.lock` と `requests` / `certifi` 依存を廃止しました。これにより [GHSA-6q48-6c7w-9gw2](https://github.com/advisories/GHSA-6q48-6c7w-9gw2) の脆弱な `certifi` がこのリポジトリから除去されます。
- 実行するOS/PythonのTLS信頼ストアは別途最新のセキュリティ更新を適用してください。以前の依存環境やコンテナを実際に使用している場合は再構築・再配備が必要です。GitHubのソースコード更新だけでは稼働中の環境は更新されません。
- CIのGitHub Actionsは検証済みコミットSHAで固定し、Dependabotで更新を監視します。
