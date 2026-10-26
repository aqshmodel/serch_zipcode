"""郵便番号から住所を検索する（外部Pythonパッケージ不要）。"""

import json
import re
from urllib import error, parse, request


API_URL = "https://zipcloud.ibsnet.co.jp/api/search"
REQUEST_TIMEOUT_SECONDS = 10
MAX_RESPONSE_BYTES = 64 * 1024


class AddressLookupError(Exception):
    """住所検索APIから住所を取得できなかった場合の例外。"""


class _NoRedirectHandler(request.HTTPRedirectHandler):
    """HTTPSからHTTPへのダウングレード等を防ぐため、転送を許可しない。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise error.HTTPError(req.full_url, code, "APIのリダイレクトは許可されていません", headers, fp)


_OPENER = request.build_opener(_NoRedirectHandler())


def search_address(zipcode: str) -> str:
    """7桁の郵便番号から都道府県・市区町村・町域を返す。

    郵便番号が不正な場合はValueError、検索に失敗した場合は
    AddressLookupErrorを送出する。
    """
    if not isinstance(zipcode, str) or not re.fullmatch(r"(?:[0-9]{7}|[0-9]{3}-[0-9]{4})", zipcode):
        raise ValueError("郵便番号は7桁の数字（または123-4567形式）で入力してください")

    normalized = zipcode.replace("-", "")
    query = parse.urlencode({"zipcode": normalized, "limit": 1})
    api_request = request.Request(
        f"{API_URL}?{query}", headers={"Accept": "application/json"}
    )

    try:
        with _OPENER.open(api_request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            response_bytes = response.read(MAX_RESPONSE_BYTES + 1)
    except (error.URLError, TimeoutError) as exc:
        raise AddressLookupError("住所検索APIに安全に接続できませんでした") from exc

    if len(response_bytes) > MAX_RESPONSE_BYTES:
        raise AddressLookupError("住所検索APIのレスポンスが大きすぎます")

    try:
        payload = json.loads(response_bytes)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise AddressLookupError("住所検索APIのレスポンスが不正です") from exc

    if not isinstance(payload, dict) or payload.get("status") != 200:
        raise AddressLookupError("住所検索APIがエラーを返しました")

    results = payload.get("results")
    if results is None or results == []:
        raise AddressLookupError("該当する住所が見つかりませんでした")
    if not isinstance(results, list) or not isinstance(results[0], dict):
        raise AddressLookupError("住所検索APIの検索結果が不正です")

    address = results[0]
    address_fields = (address.get("address1"), address.get("address2"), address.get("address3"))
    if not all(isinstance(value, str) for value in address_fields):
        raise AddressLookupError("住所検索APIの住所データが不正です")

    return "".join(address_fields)


def main() -> None:
    zipcode = "0287405"
    print(search_address(zipcode))


if __name__ == "__main__":
    try:
        main()
    except (AddressLookupError, ValueError) as exc:
        raise SystemExit(f"エラー: {exc}") from exc
