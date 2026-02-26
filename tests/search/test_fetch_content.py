"""fetch_content 节点和 _fetch_one 函数测试。"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

if "trafilatura" not in sys.modules:
    sys.modules["trafilatura"] = MagicMock()

from ai_hub_agents.search.nodes.fetch_content import _fetch_one, make_fetch_content


class TestFetchContentNode:

    def test_empty_or_missing_results(self):
        node = make_fetch_content()
        assert node({"search_results": []})["search_fetched"] == []
        assert node({})["search_fetched"] == []

    @patch("ai_hub_agents.search.nodes.fetch_content._fetch_one")
    def test_mock_fetch_success(self, mock_fetch):
        mock_fetch.return_value = {"url": "https://a.com", "markdown": "content"}
        node = make_fetch_content()
        state = {"search_results": [{"url": "https://a.com"}]}
        result = node(state)
        assert len(result["search_fetched"]) == 1
        assert result["search_fetched"][0]["markdown"] == "content"

    @patch("ai_hub_agents.search.nodes.fetch_content._fetch_one")
    def test_failure_skip(self, mock_fetch):
        mock_fetch.return_value = None
        node = make_fetch_content()
        state = {"search_results": [{"url": "https://a.com"}, {"url": "https://b.com"}]}
        result = node(state)
        assert result["search_fetched"] == []

    @patch("ai_hub_agents.search.nodes.fetch_content._fetch_one")
    def test_partial_success(self, mock_fetch):
        mock_fetch.side_effect = [
            {"url": "https://a.com", "markdown": "ok"},
            None,
            {"url": "https://c.com", "markdown": "also ok"},
        ]
        node = make_fetch_content()
        state = {"search_results": [
            {"url": "https://a.com"},
            {"url": "https://b.com"},
            {"url": "https://c.com"},
        ]}
        result = node(state)
        assert len(result["search_fetched"]) == 2


class TestFetchOne:

    @patch("trafilatura.extract", return_value="# Title\n\nContent")
    @patch("requests.get")
    def test_normal_fetch(self, mock_get, mock_extract):
        mock_resp = MagicMock()
        mock_resp.text = "<html>test</html>"
        mock_get.return_value = mock_resp

        result = _fetch_one("https://example.com", timeout=8, max_chars=4000)
        assert result is not None
        assert result["url"] == "https://example.com"
        assert result["markdown"] == "# Title\n\nContent"

    @patch("trafilatura.extract", return_value="x" * 10000)
    @patch("requests.get")
    def test_long_content_truncated(self, mock_get, mock_extract):
        mock_resp = MagicMock()
        mock_resp.text = "<html>test</html>"
        mock_get.return_value = mock_resp

        result = _fetch_one("https://example.com", timeout=8, max_chars=100)
        assert result is not None
        assert len(result["markdown"]) == 100

    @patch("requests.get", side_effect=ConnectionError("timeout"))
    def test_network_error_returns_none(self, mock_get):
        result = _fetch_one("https://example.com", timeout=8, max_chars=4000)
        assert result is None

    @patch("trafilatura.extract", return_value=None)
    @patch("requests.get")
    def test_extract_empty_returns_none(self, mock_get, mock_extract):
        mock_resp = MagicMock()
        mock_resp.text = "<html>empty</html>"
        mock_get.return_value = mock_resp

        result = _fetch_one("https://example.com", timeout=8, max_chars=4000)
        assert result is None
