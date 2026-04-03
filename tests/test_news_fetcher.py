"""Tests for the news fetcher module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ia_news_report.news_fetcher import Article, NewsAPIFetcher, RSSFetcher


class TestArticle:
    def test_article_defaults(self):
        article = Article(title="Test", url="http://example.com", source="Test Source")
        assert article.title == "Test"
        assert article.url == "http://example.com"
        assert article.source == "Test Source"
        assert article.summary == ""
        assert article.published == ""
        assert article.content == ""

    def test_article_full(self):
        article = Article(
            title="Breaking News",
            url="http://example.com/news",
            source="BBC",
            summary="A summary",
            published="Mon, 01 Jan 2024",
            content="Full content here",
        )
        assert article.title == "Breaking News"
        assert article.content == "Full content here"


class TestRSSFetcher:
    def test_fetch_returns_articles(self):
        mock_feed = MagicMock()
        mock_feed.feed.get.return_value = "Test Feed"
        mock_entry = MagicMock()
        mock_entry.get.side_effect = lambda key, default="": {
            "title": "Test Article",
            "link": "http://example.com/1",
            "summary": "A test summary",
            "published": "Mon, 01 Jan 2024",
            "content": None,
        }.get(key, default)
        mock_feed.entries = [mock_entry]

        with patch("ia_news_report.news_fetcher.feedparser.parse", return_value=mock_feed):
            fetcher = RSSFetcher(feeds=["http://fake-feed.com/rss"])
            articles = fetcher.fetch(max_per_feed=5)

        assert len(articles) == 1
        assert articles[0].title == "Test Article"
        assert articles[0].url == "http://example.com/1"
        assert articles[0].source == "Test Feed"

    def test_fetch_respects_max_per_feed(self):
        mock_feed = MagicMock()
        mock_feed.feed.get.return_value = "Feed"

        entries = []
        for i in range(10):
            e = MagicMock()
            e.get.side_effect = lambda key, default="", i=i: {
                "title": f"Article {i}",
                "link": f"http://example.com/{i}",
                "summary": "",
                "published": "",
                "content": None,
            }.get(key, default)
            entries.append(e)
        mock_feed.entries = entries

        with patch("ia_news_report.news_fetcher.feedparser.parse", return_value=mock_feed):
            fetcher = RSSFetcher(feeds=["http://fake-feed.com/rss"])
            articles = fetcher.fetch(max_per_feed=3)

        assert len(articles) == 3

    def test_fetch_handles_feed_error(self):
        with patch(
            "ia_news_report.news_fetcher.feedparser.parse",
            side_effect=Exception("Network error"),
        ):
            fetcher = RSSFetcher(feeds=["http://broken-feed.com/rss"])
            articles = fetcher.fetch()

        assert articles == []

    def test_fetch_multiple_feeds(self):
        def make_feed(name, n):
            feed = MagicMock()
            feed.feed.get.return_value = name
            entries = []
            for i in range(n):
                e = MagicMock()
                e.get.side_effect = lambda key, default="", name=name, i=i: {
                    "title": f"{name} Article {i}",
                    "link": f"http://example.com/{name}/{i}",
                    "summary": "",
                    "published": "",
                    "content": None,
                }.get(key, default)
                entries.append(e)
            feed.entries = entries
            return feed

        feeds_data = {
            "http://feed1.com/rss": make_feed("Feed1", 2),
            "http://feed2.com/rss": make_feed("Feed2", 3),
        }

        with patch(
            "ia_news_report.news_fetcher.feedparser.parse",
            side_effect=lambda url: feeds_data[url],
        ):
            fetcher = RSSFetcher(feeds=list(feeds_data.keys()))
            articles = fetcher.fetch(max_per_feed=5)

        assert len(articles) == 5


class TestNewsAPIFetcher:
    def test_fetch_returns_articles(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "API Article",
                    "url": "http://example.com/api",
                    "source": {"name": "Reuters"},
                    "description": "An API description",
                    "publishedAt": "2024-01-01T12:00:00Z",
                    "content": "Full API content",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("ia_news_report.news_fetcher.requests.get", return_value=mock_response):
            fetcher = NewsAPIFetcher(api_key="test_key", country="us")
            articles = fetcher.fetch(max_articles=5)

        assert len(articles) == 1
        assert articles[0].title == "API Article"
        assert articles[0].source == "Reuters"
        assert articles[0].content == "Full API content"

    def test_fetch_handles_request_error(self):
        import requests as req

        with patch(
            "ia_news_report.news_fetcher.requests.get",
            side_effect=req.RequestException("Connection error"),
        ):
            fetcher = NewsAPIFetcher(api_key="test_key")
            articles = fetcher.fetch()

        assert articles == []

    def test_fetch_with_category(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"articles": []}
        mock_response.raise_for_status = MagicMock()

        with patch("ia_news_report.news_fetcher.requests.get", return_value=mock_response) as mock_get:
            fetcher = NewsAPIFetcher(api_key="test_key", country="us", category="technology")
            fetcher.fetch()

        call_kwargs = mock_get.call_args
        assert call_kwargs[1]["params"]["category"] == "technology"
