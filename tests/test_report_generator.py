"""Tests for the report generator module."""

from __future__ import annotations

import pytest

from ia_news_report.news_fetcher import Article
from ia_news_report.report_generator import ReportGenerator


@pytest.fixture
def articles():
    return [
        Article(
            title="First Article",
            url="http://example.com/1",
            source="BBC",
            summary="Summary of the first article.",
            published="Mon, 01 Jan 2024",
        ),
        Article(
            title="Second Article",
            url="http://example.com/2",
            source="Reuters",
            summary="Summary of the second article.",
            published="Mon, 01 Jan 2024",
        ),
    ]


class TestReportGenerator:
    def test_generate_text_contains_title(self, articles):
        gen = ReportGenerator()
        report = gen.generate(articles, title="My News Report")
        assert "My News Report" in report

    def test_generate_text_contains_articles(self, articles):
        gen = ReportGenerator()
        report = gen.generate(articles)
        assert "First Article" in report
        assert "Second Article" in report

    def test_generate_text_contains_sources(self, articles):
        gen = ReportGenerator()
        report = gen.generate(articles)
        assert "BBC" in report
        assert "Reuters" in report

    def test_generate_text_contains_overview(self, articles):
        gen = ReportGenerator()
        report = gen.generate(articles, overview="This is today's overview.")
        assert "EXECUTIVE OVERVIEW" in report
        assert "This is today's overview." in report

    def test_generate_text_no_overview(self, articles):
        gen = ReportGenerator()
        report = gen.generate(articles)
        assert "EXECUTIVE OVERVIEW" not in report

    def test_generate_text_article_count(self, articles):
        gen = ReportGenerator()
        report = gen.generate(articles)
        assert "Total articles: 2" in report

    def test_generate_text_default_title(self, articles):
        gen = ReportGenerator()
        report = gen.generate(articles)
        assert "AI News Report" in report

    def test_generate_text_empty_articles(self):
        gen = ReportGenerator()
        report = gen.generate([])
        assert "Total articles: 0" in report

    def test_generate_markdown_contains_title(self, articles):
        gen = ReportGenerator()
        report = gen.generate_markdown(articles, title="MD Report")
        assert "# MD Report" in report

    def test_generate_markdown_contains_articles(self, articles):
        gen = ReportGenerator()
        report = gen.generate_markdown(articles)
        assert "First Article" in report
        assert "Second Article" in report

    def test_generate_markdown_contains_overview(self, articles):
        gen = ReportGenerator()
        report = gen.generate_markdown(articles, overview="Overview text here.")
        assert "## Executive Overview" in report
        assert "Overview text here." in report

    def test_generate_markdown_links(self, articles):
        gen = ReportGenerator()
        report = gen.generate_markdown(articles)
        assert "[Read more](http://example.com/1)" in report
        assert "[Read more](http://example.com/2)" in report

    def test_generate_markdown_no_overview(self, articles):
        gen = ReportGenerator()
        report = gen.generate_markdown(articles)
        assert "## Executive Overview" not in report

    def test_generate_markdown_article_count(self, articles):
        gen = ReportGenerator()
        report = gen.generate_markdown(articles)
        assert "Total articles: 2" in report
