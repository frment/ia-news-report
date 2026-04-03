"""News fetcher module: retrieves articles from RSS feeds and NewsAPI."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional

import feedparser
import requests

logger = logging.getLogger(__name__)


@dataclass
class Article:
    """Represents a single news article."""

    title: str
    url: str
    source: str
    summary: str = ""
    published: str = ""
    content: str = ""


class RSSFetcher:
    """Fetches news articles from RSS feeds."""

    def __init__(self, feeds: List[str]):
        self.feeds = feeds

    def fetch(self, max_per_feed: int = 5) -> List[Article]:
        """Fetch articles from all configured RSS feeds.

        Args:
            max_per_feed: Maximum number of articles to fetch per feed.

        Returns:
            List of Article objects.
        """
        articles: List[Article] = []
        for feed_url in self.feeds:
            try:
                parsed = feedparser.parse(feed_url)
                source = parsed.feed.get("title", feed_url)
                for entry in parsed.entries[:max_per_feed]:
                    article = Article(
                        title=entry.get("title", ""),
                        url=entry.get("link", ""),
                        source=source,
                        summary=entry.get("summary", ""),
                        published=entry.get("published", ""),
                        content=entry.get("content", [{}])[0].get("value", "")
                        if entry.get("content")
                        else entry.get("summary", ""),
                    )
                    articles.append(article)
                    logger.debug("Fetched article: %s", article.title)
            except Exception as exc:
                logger.warning("Failed to fetch feed %s: %s", feed_url, exc)
        return articles


class NewsAPIFetcher:
    """Fetches news articles from the NewsAPI service."""

    BASE_URL = "https://newsapi.org/v2/top-headlines"

    def __init__(self, api_key: str, country: str = "us", category: Optional[str] = None):
        self.api_key = api_key
        self.country = country
        self.category = category

    def fetch(self, max_articles: int = 10) -> List[Article]:
        """Fetch top headlines from NewsAPI.

        Args:
            max_articles: Maximum number of articles to return.

        Returns:
            List of Article objects.
        """
        params: dict = {
            "apiKey": self.api_key,
            "country": self.country,
            "pageSize": max_articles,
        }
        if self.category:
            params["category"] = self.category

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.error("NewsAPI request failed: %s", exc)
            return []

        articles: List[Article] = []
        for item in data.get("articles", []):
            article = Article(
                title=item.get("title", ""),
                url=item.get("url", ""),
                source=item.get("source", {}).get("name", "Unknown"),
                summary=item.get("description", ""),
                published=item.get("publishedAt", ""),
                content=item.get("content", "") or item.get("description", ""),
            )
            articles.append(article)
            logger.debug("Fetched article: %s", article.title)

        return articles


DEFAULT_RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://feeds.reuters.com/reuters/topNews",
]
