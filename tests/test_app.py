"""ネットワークに接続せず郵便番号検索アプリをテストする。"""

import json
import unittest
from unittest.mock import patch
from urllib import error, parse, request

import app


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self, limit):
        return self.content[:limit]


class TestSearchAddress(unittest.TestCase):
    @staticmethod
    def success_response():
        payload = {
            "status": 200,
            "message": None,
            "results": [{"address1": "岩手県", "address2": "八幡平市", "address3": "大更"}],
        }
        return FakeResponse(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def test_success_uses_https_with_timeout(self):
        with patch.object(app._OPENER, "open", return_value=self.success_response()) as mock_open:
            address = app.search_address("0287405")
        self.assertEqual(address, "岩手県八幡平市大更")
        request_arg = mock_open.call_args.args[0]
        parsed = parse.urlsplit(request_arg.full_url)
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.hostname, "zipcloud.ibsnet.co.jp")
        self.assertEqual(parse.parse_qs(parsed.query), {"zipcode": ["0287405"], "limit": ["1"]})
        self.assertEqual(mock_open.call_args.kwargs["timeout"], 10)
        self.assertEqual(request_arg.get_header("Accept"), "application/json")

    def test_hyphenated_zipcode(self):
        with patch.object(app._OPENER, "open", return_value=self.success_response()) as mock_open:
            self.assertEqual(app.search_address("028-7405"), "岩手県八幡平市大更")
        self.assertIn("zipcode=0287405", mock_open.call_args.args[0].full_url)

    def test_invalid_zipcodes_are_rejected_without_network(self):
        for zipcode in ["", "123", "12345678", "１２３４５６７", "0287-405", "028--7405", "1234567&limit=999", 1234567, None]:
            with self.subTest(zipcode=zipcode):
                with patch.object(app._OPENER, "open") as mock_open:
                    with self.assertRaises(ValueError):
                        app.search_address(zipcode)
                mock_open.assert_not_called()

    def test_no_matching_result(self):
        payload = {"status": 200, "message": None, "results": None}
        with patch.object(app._OPENER, "open", return_value=FakeResponse(json.dumps(payload).encode())):
            with self.assertRaisesRegex(app.AddressLookupError, "見つかりません"):
                app.search_address("0000000")

    def test_api_error(self):
        payload = {"status": 400, "message": "invalid", "results": None}
        with patch.object(app._OPENER, "open", return_value=FakeResponse(json.dumps(payload).encode())):
            with self.assertRaisesRegex(app.AddressLookupError, "エラー"):
                app.search_address("0287405")

    def test_unexpected_results(self):
        for payload in [
            {"status": 200, "results": "not-a-list"},
            {"status": 200, "results": [None]},
            {"status": 200, "results": [{"address1": "岩手県"}]},
        ]:
            with self.subTest(payload=payload):
                with patch.object(app._OPENER, "open", return_value=FakeResponse(json.dumps(payload).encode())):
                    with self.assertRaises(app.AddressLookupError):
                        app.search_address("0287405")

    def test_malformed_json(self):
        with patch.object(app._OPENER, "open", return_value=FakeResponse(b"not json")):
            with self.assertRaisesRegex(app.AddressLookupError, "不正"):
                app.search_address("0287405")

    def test_oversized_response(self):
        with patch.object(app._OPENER, "open", return_value=FakeResponse(b"x" * (app.MAX_RESPONSE_BYTES + 1))):
            with self.assertRaisesRegex(app.AddressLookupError, "大きすぎ"):
                app.search_address("0287405")

    def test_connection_error(self):
        with patch.object(app._OPENER, "open", side_effect=error.URLError("connection refused")):
            with self.assertRaisesRegex(app.AddressLookupError, "接続"):
                app.search_address("0287405")

    def test_redirect_is_rejected(self):
        handler = app._NoRedirectHandler()
        with self.assertRaises(error.HTTPError):
            handler.redirect_request(
                request.Request(app.API_URL), None, 302, "Moved", {}, "http://evil.example/"
            )


if __name__ == "__main__":
    unittest.main()
