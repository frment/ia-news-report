"""CLI entry point for ia-news-report."""

from __future__ import annotations

import logging
import os
import sys
from typing import List, Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from ia_news_report.ai_summarizer import AISummarizer
from ia_news_report.news_fetcher import DEFAULT_RSS_FEEDS, NewsAPIFetcher, RSSFetcher
from ia_news_report.report_generator import ReportGenerator

load_dotenv()
console = Console()


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


@click.command()
@click.option(
    "--source",
    type=click.Choice(["rss", "newsapi"], case_sensitive=False),
    default="rss",
    show_default=True,
    help="News source to use.",
)
@click.option(
    "--feed",
    "feeds",
    multiple=True,
    help="RSS feed URL(s). Can be specified multiple times. Defaults to major news feeds.",
)
@click.option(
    "--category",
    default=None,
    help="News category for NewsAPI (e.g. technology, sports, business).",
)
@click.option(
    "--country",
    default="us",
    show_default=True,
    help="Country code for NewsAPI top headlines.",
)
@click.option(
    "--max-articles",
    default=10,
    show_default=True,
    type=int,
    help="Maximum number of articles to fetch.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "markdown"], case_sensitive=False),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path. If not specified, prints to stdout.",
)
@click.option(
    "--ai/--no-ai",
    default=True,
    show_default=True,
    help="Enable or disable AI summarization.",
)
@click.option(
    "--title",
    default=None,
    help="Custom report title.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Enable verbose logging.",
)
def main(
    source: str,
    feeds: tuple,
    category: Optional[str],
    country: str,
    max_articles: int,
    output_format: str,
    output: Optional[str],
    ai: bool,
    title: Optional[str],
    verbose: bool,
) -> None:
    """Generate an AI-powered news report from RSS feeds or NewsAPI."""
    _setup_logging(verbose)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        # Fetch articles
        task = progress.add_task("Fetching news articles...", total=None)
        articles = _fetch_articles(source, feeds, country, category, max_articles)
        progress.update(task, completed=True)

        if not articles:
            console.print("[red]No articles found. Check your configuration.[/red]")
            sys.exit(1)

        console.print(f"[green]Fetched {len(articles)} articles.[/green]")

        # AI summarization
        overview: Optional[str] = None
        if ai:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                console.print(
                    "[yellow]OPENAI_API_KEY not set – skipping AI summarization.[/yellow]"
                )
            else:
                task = progress.add_task("Generating AI overview...", total=None)
                try:
                    summarizer = AISummarizer(api_key=api_key)
                    overview = summarizer.generate_overview(articles)
                except Exception as exc:
                    console.print(f"[yellow]AI summarization failed: {exc}[/yellow]")
                progress.update(task, completed=True)

        # Generate report
        generator = ReportGenerator()
        if output_format == "markdown":
            report = generator.generate_markdown(articles, overview=overview, title=title)
        else:
            report = generator.generate(articles, overview=overview, title=title)

    # Output report
    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(report)
        console.print(f"[green]Report saved to {output}[/green]")
    else:
        if output_format == "markdown":
            console.print(Markdown(report))
        else:
            console.print(report)


def _fetch_articles(
    source: str,
    feeds: tuple,
    country: str,
    category: Optional[str],
    max_articles: int,
) -> list:
    if source == "newsapi":
        api_key = os.environ.get("NEWSAPI_KEY")
        if not api_key:
            console.print(
                "[red]NEWSAPI_KEY environment variable is required for the newsapi source.[/red]"
            )
            sys.exit(1)
        fetcher = NewsAPIFetcher(api_key=api_key, country=country, category=category)
        return fetcher.fetch(max_articles=max_articles)
    else:
        feed_list = list(feeds) if feeds else DEFAULT_RSS_FEEDS
        fetcher = RSSFetcher(feeds=feed_list)
        return fetcher.fetch(max_per_feed=max_articles)


if __name__ == "__main__":
    main()
