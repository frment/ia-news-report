"""Tests for the AI summarizer module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ia_news_report.news_fetcher import Article


class TestAISummarizer:
    """Tests for AISummarizer."""

    def _make_mock_client(self, content: str):
        mock_choice = MagicMock()
        mock_choice.message.content = content
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client

    def test_summarize_article(self):
        from ia_news_report.ai_summarizer import AISummarizer

        mock_client = self._make_mock_client("This is a summary.")

        with patch("ia_news_report.ai_summarizer.OpenAI", return_value=mock_client):
            summarizer = AISummarizer(api_key="test_key")
            article = Article(
                title="Test Article",
                url="http://example.com",
                source="Test",
                content="Full article content.",
            )
            result = summarizer.summarize_article(article)

        assert result == "This is a summary."

    def test_summarize_article_uses_content_over_summary(self):
        from ia_news_report.ai_summarizer import AISummarizer

        mock_client = self._make_mock_client("Content-based summary.")

        with patch("ia_news_report.ai_summarizer.OpenAI", return_value=mock_client):
            summarizer = AISummarizer(api_key="test_key")
            article = Article(
                title="Test",
                url="http://example.com",
                source="Test",
                summary="A short summary",
                content="A longer article content",
            )
            summarizer.summarize_article(article)

        call_args = mock_client.chat.completions.create.call_args
        prompt = call_args[1]["messages"][0]["content"]
        assert "A longer article content" in prompt

    def test_summarize_article_falls_back_on_error(self):
        from ia_news_report.ai_summarizer import AISummarizer

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")

        with patch("ia_news_report.ai_summarizer.OpenAI", return_value=mock_client):
            summarizer = AISummarizer(api_key="test_key")
            article = Article(
                title="Fallback Title",
                url="http://example.com",
                source="Test",
                summary="Fallback summary",
            )
            result = summarizer.summarize_article(article)

        assert result == "Fallback summary"

    def test_generate_overview(self):
        from ia_news_report.ai_summarizer import AISummarizer

        mock_client = self._make_mock_client("Overview paragraph 1.\n\nOverview paragraph 2.")

        with patch("ia_news_report.ai_summarizer.OpenAI", return_value=mock_client):
            summarizer = AISummarizer(api_key="test_key")
            articles = [
                Article(title=f"Article {i}", url=f"http://example.com/{i}", source="Test")
                for i in range(5)
            ]
            result = summarizer.generate_overview(articles)

        assert "Overview paragraph 1." in result

    def test_generate_overview_empty_articles(self):
        from ia_news_report.ai_summarizer import AISummarizer

        mock_client = MagicMock()

        with patch("ia_news_report.ai_summarizer.OpenAI", return_value=mock_client):
            summarizer = AISummarizer(api_key="test_key")
            result = summarizer.generate_overview([])

        assert result == "No articles available for overview."
        mock_client.chat.completions.create.assert_not_called()

    def test_generate_overview_error_returns_fallback(self):
        from ia_news_report.ai_summarizer import AISummarizer

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")

        with patch("ia_news_report.ai_summarizer.OpenAI", return_value=mock_client):
            summarizer = AISummarizer(api_key="test_key")
            articles = [
                Article(title="Article 1", url="http://example.com", source="Test")
            ]
            result = summarizer.generate_overview(articles)

        assert result == "Could not generate overview."

    def test_uses_custom_model(self):
        from ia_news_report.ai_summarizer import AISummarizer

        mock_client = self._make_mock_client("Summary")

        with patch("ia_news_report.ai_summarizer.OpenAI", return_value=mock_client):
            summarizer = AISummarizer(api_key="test_key", model="gpt-4o")
            assert summarizer.model == "gpt-4o"

    def test_default_model(self):
        from ia_news_report.ai_summarizer import AISummarizer

        mock_client = MagicMock()

        with patch("ia_news_report.ai_summarizer.OpenAI", return_value=mock_client):
            summarizer = AISummarizer(api_key="test_key")
            assert summarizer.model == AISummarizer.DEFAULT_MODEL
