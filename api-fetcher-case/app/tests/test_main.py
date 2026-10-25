import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import requests


spec = importlib.util.spec_from_file_location("api_fetcher", Path(__file__).parents[1] / "main.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ApiFetcherTests(unittest.TestCase):
    def setUp(self):
        self.url = "https://example.com/posts"
        self.env = patch.dict(os.environ, {"API_URL": self.url})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.client = module.app.test_client()
        self.response = Mock(status_code=200)
        self.response.json.return_value = [{"id": 1}]
        self.get = patch.object(module.requests, "get", return_value=self.response).start()
        self.addCleanup(patch.stopall)

    def test_fetches_configured_url_with_timeout_and_no_redirects(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"id": 1}])
        self.get.assert_called_once_with(self.url, timeout=(3.05, 10), allow_redirects=False)

    def test_rejects_other_destinations_without_requesting_them(self):
        for url in ("http://127.0.0.1/", "http://169.254.169.254/", "file:///etc/passwd", "https://other.example/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get("/", query_string={"api_url": url}).status_code, 400)
        self.get.assert_not_called()

    def test_allows_matching_legacy_query(self):
        self.assertEqual(self.client.get("/", query_string={"api_url": self.url}).status_code, 200)

    def test_rejects_conflicting_duplicate_query_values(self):
        response = self.client.get("/", query_string=[("api_url", self.url), ("api_url", "http://localhost/")])
        self.assertEqual(response.status_code, 400)
        self.get.assert_not_called()

    def test_caller_cannot_supply_missing_configuration(self):
        os.environ.pop("API_URL")
        self.assertEqual(self.client.get("/", query_string={"api_url": self.url}).status_code, 400)
        self.get.assert_not_called()

    def test_rejects_invalid_configured_urls(self):
        for url in ("file:///etc/passwd", "https://user:password@example.com", "https://example.com:bad", "https://[invalid", "https://example.com/#fragment"):
            with self.subTest(url=url):
                os.environ["API_URL"] = url
                self.assertEqual(self.client.get("/").status_code, 500)
        self.get.assert_not_called()

    def test_rejects_redirect_instead_of_following_it(self):
        self.response.status_code = 302
        self.assertEqual(self.client.get("/").status_code, 502)
        self.response.json.assert_not_called()

    def test_timeout_returns_gateway_timeout(self):
        self.get.side_effect = requests.exceptions.Timeout()
        self.assertEqual(self.client.get("/").status_code, 504)

    def test_upstream_failure_does_not_expose_url_or_credentials(self):
        self.get.side_effect = requests.exceptions.ConnectionError("secret upstream details")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 502)
        self.assertNotIn(b"secret upstream details", response.data)

    def test_non_json_response_returns_bad_gateway(self):
        self.response.json.side_effect = requests.exceptions.JSONDecodeError("invalid", "text", 0)
        self.assertEqual(self.client.get("/").status_code, 502)

    def test_upstream_http_error_returns_bad_gateway(self):
        self.response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        self.assertEqual(self.client.get("/").status_code, 502)


if __name__ == "__main__":
    unittest.main()
