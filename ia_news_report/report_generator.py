"""Report generator module: formats articles into a readable news report."""

from __future__ import annotations

import datetime
import textwrap
from typing import List, Optional

from ia_news_report.news_fetcher import Article


class ReportGenerator:
    """Formats a collection of articles into a structured news report."""

    LINE_WIDTH = 80

    def generate(
        self,
        articles: List[Article],
        overview: Optional[str] = None,
        title: Optional[str] = None,
    ) -> str:
        """Generate a formatted text news report.

        Args:
            articles: List of articles to include in the report.
            overview: Optional AI-generated executive overview.
            title: Optional report title.

        Returns:
            Formatted news report as a string.
        """
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%A, %B %d, %Y – %H:%M UTC")
        report_title = title or "AI News Report"

        lines: List[str] = []
        lines.append("=" * self.LINE_WIDTH)
        lines.append(report_title.center(self.LINE_WIDTH))
        lines.append(now.center(self.LINE_WIDTH))
        lines.append("=" * self.LINE_WIDTH)
        lines.append("")

        if overview:
            lines.append("EXECUTIVE OVERVIEW")
            lines.append("-" * self.LINE_WIDTH)
            for para in overview.split("\n"):
                wrapped = textwrap.fill(para, width=self.LINE_WIDTH)
                if wrapped:
                    lines.append(wrapped)
            lines.append("")

        lines.append("TOP STORIES")
        lines.append("-" * self.LINE_WIDTH)

        for i, article in enumerate(articles, start=1):
            lines.append(f"\n[{i}] {article.title}")
            lines.append(f"    Source: {article.source}")
            if article.published:
                lines.append(f"    Published: {article.published}")
            if article.summary:
                wrapped = textwrap.fill(
                    article.summary,
                    width=self.LINE_WIDTH - 4,
                    initial_indent="    ",
                    subsequent_indent="    ",
                )
                lines.append(wrapped)
            if article.url:
                lines.append(f"    URL: {article.url}")

        lines.append("")
        lines.append("=" * self.LINE_WIDTH)
        lines.append(f"Total articles: {len(articles)}".center(self.LINE_WIDTH))
        lines.append("=" * self.LINE_WIDTH)

        return "\n".join(lines)

    def generate_markdown(
        self,
        articles: List[Article],
        overview: Optional[str] = None,
        title: Optional[str] = None,
    ) -> str:
        """Generate a Markdown-formatted news report.

        Args:
            articles: List of articles to include in the report.
            overview: Optional AI-generated executive overview.
            title: Optional report title.

        Returns:
            Markdown-formatted news report as a string.
        """
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%A, %B %d, %Y – %H:%M UTC")
        report_title = title or "AI News Report"

        lines: List[str] = []
        lines.append(f"# {report_title}")
        lines.append(f"*Generated: {now}*")
        lines.append("")

        if overview:
            lines.append("## Executive Overview")
            lines.append("")
            lines.append(overview)
            lines.append("")

        lines.append("## Top Stories")
        lines.append("")

        for i, article in enumerate(articles, start=1):
            lines.append(f"### {i}. {article.title}")
            lines.append(f"**Source:** {article.source}")
            if article.published:
                lines.append(f"**Published:** {article.published}")
            if article.summary:
                lines.append("")
                lines.append(article.summary)
            if article.url:
                lines.append("")
                lines.append(f"[Read more]({article.url})")
            lines.append("")

        lines.append("---")
        lines.append(f"*Total articles: {len(articles)}*")

        return "\n".join(lines)
