# ia-news-report

AI-powered news report generator. Fetches the latest news from RSS feeds or [NewsAPI](https://newsapi.org/) and uses OpenAI to produce a concise executive overview and article summaries.

## Features

- 📰 Fetch news from popular **RSS feeds** (BBC, NYT, Reuters) or any custom feed
- 🔍 Fetch top headlines via **NewsAPI** with optional category and country filters
- 🤖 **AI-generated executive overview** using OpenAI (GPT-4o-mini by default)
- 📄 Output in **plain text** or **Markdown** format
- 💾 Save report to a file or print to stdout
- 🛠️ Fully configurable via CLI flags and environment variables

## Requirements

- Python 3.9+
- An [OpenAI API key](https://platform.openai.com/api-keys) (optional — skipped gracefully if not set)
- A [NewsAPI key](https://newsapi.org/register) (only required when using `--source=newsapi`)

## Installation

```bash
git clone https://github.com/frment/ia-news-report.git
cd ia-news-report
pip install -r requirements.txt
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

```dotenv
# .env
OPENAI_API_KEY=sk-...
NEWSAPI_KEY=your_newsapi_key_here
```

## Usage

```bash
# Generate a report from default RSS feeds (BBC, NYT, Reuters)
ia-news-report

# Use NewsAPI for top US headlines
ia-news-report --source=newsapi

# Use NewsAPI with a specific category
ia-news-report --source=newsapi --category=technology --country=gb

# Use custom RSS feeds
ia-news-report --feed=https://feeds.bbci.co.uk/news/technology/rss.xml \
               --feed=https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml

# Generate a Markdown report and save to a file
ia-news-report --format=markdown --output=report.md

# Disable AI summarization
ia-news-report --no-ai

# Show help
ia-news-report --help
```

### All Options

| Option | Default | Description |
|---|---|---|
| `--source` | `rss` | News source: `rss` or `newsapi` |
| `--feed` | BBC, NYT, Reuters | RSS feed URL(s), repeatable |
| `--category` | — | NewsAPI category (e.g. `technology`, `sports`) |
| `--country` | `us` | Country code for NewsAPI |
| `--max-articles` | `10` | Maximum articles to fetch |
| `--format` | `text` | Output format: `text` or `markdown` |
| `--output` / `-o` | stdout | Output file path |
| `--ai` / `--no-ai` | `--ai` | Enable/disable AI summarization |
| `--title` | — | Custom report title |
| `--verbose` / `-v` | off | Enable verbose logging |

## Project Structure

```
ia-news-report/
├── ia_news_report/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point (Click)
│   ├── news_fetcher.py     # RSS and NewsAPI fetchers
│   ├── ai_summarizer.py    # OpenAI summarization
│   └── report_generator.py # Text and Markdown report formatter
├── tests/
│   ├── test_news_fetcher.py
│   ├── test_ai_summarizer.py
│   └── test_report_generator.py
├── .env.example
├── requirements.txt
├── requirements-dev.txt
└── setup.py
```

## Development

```bash
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .

# Run tests
python -m pytest tests/ -v
```

## License

MIT