from setuptools import setup, find_packages

setup(
    name="ia-news-report",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.31.0",
        "feedparser>=6.0.10",
        "python-dotenv>=1.0.0",
        "click>=8.1.7",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "ia-news-report=ia_news_report.cli:main",
        ],
    },
    python_requires=">=3.9",
    description="AI-powered news report generator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
