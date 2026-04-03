"""AI summarizer module: uses OpenAI to summarize and analyze news articles."""

from __future__ import annotations

import logging
from typing import List, Optional

from ia_news_report.news_fetcher import Article

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False


class AISummarizer:
    """Summarizes and analyzes news articles using the OpenAI API."""

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, api_key: str, model: Optional[str] = None):
        """Initialize the summarizer.

        Args:
            api_key: OpenAI API key.
            model: OpenAI model to use. Defaults to gpt-4o-mini.
        """
        if not _OPENAI_AVAILABLE:
            raise ImportError(
                "openai package is required. Install it with: pip install openai"
            )
        self.client = OpenAI(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL

    def summarize_article(self, article: Article) -> str:
        """Generate a concise summary for a single article.

        Args:
            article: Article to summarize.

        Returns:
            One-sentence summary of the article.
        """
        text = article.content or article.summary or article.title
        prompt = (
            f"Summarize the following news article in one concise sentence:\n\n"
            f"Title: {article.title}\n"
            f"Content: {text}"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            logger.error("Failed to summarize article '%s': %s", article.title, exc)
            return article.summary or article.title

    def generate_overview(self, articles: List[Article]) -> str:
        """Generate an executive overview of a collection of news articles.

        Args:
            articles: List of articles to summarize.

        Returns:
            Multi-paragraph overview of the top news.
        """
        if not articles:
            return "No articles available for overview."

        headlines = "\n".join(
            f"- {a.title} ({a.source})" for a in articles[:20]
        )
        prompt = (
            "You are a professional news editor. Based on the following headlines, "
            "write a brief executive overview (2-3 paragraphs) of today's top news stories. "
            "Group related stories and highlight the most important developments.\n\n"
            f"Headlines:\n{headlines}"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            logger.error("Failed to generate overview: %s", exc)
            return "Could not generate overview."
