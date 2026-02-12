"""Configuration management for Daily AI Briefing."""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    # Gmail SMTP
    gmail_user: str
    gmail_app_password: str
    recipient_email: str

    # Reddit API
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "DailyAIBriefing/1.0"

    # OpenAI API
    openai_api_key: str = ""

    # Settings
    timezone: str = "America/New_York"
    max_articles: int = 40
    max_age_hours: int = 24

    # Feature flags
    include_reddit: bool = True
    include_rss: bool = True
    include_hackernews: bool = True
    include_arxiv: bool = True
    include_github_trending: bool = True
    enable_ai_summary: bool = True

    # Topic filtering
    enable_topic_filtering: bool = False
    filter_topics: List[str] = field(default_factory=list)

    # GitHub settings
    github_history_days: int = 30

    # Reddit subreddits
    subreddits: List[str] = field(default_factory=lambda: [
        "MachineLearning",
        "artificial",
        "LocalLLaMA",
        "ChatGPT",
        "singularity",
        "OpenAI",
    ])

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        # Parse topic filtering list from comma-separated string
        topics_str = os.environ.get("FILTER_TOPICS", "")
        filter_topics = [t.strip() for t in topics_str.split(",") if t.strip()]

        return cls(
            # Required
            gmail_user=os.environ["GMAIL_USER"],
            gmail_app_password=os.environ["GMAIL_APP_PASSWORD"],
            recipient_email=os.environ.get("RECIPIENT_EMAIL", os.environ["GMAIL_USER"]),
            # Reddit
            reddit_client_id=os.environ.get("REDDIT_CLIENT_ID", ""),
            reddit_client_secret=os.environ.get("REDDIT_CLIENT_SECRET", ""),
            reddit_user_agent=os.environ.get("REDDIT_USER_AGENT", "DailyAIBriefing/1.0"),
            # OpenAI
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            # Settings
            timezone=os.environ.get("TIMEZONE", "America/New_York"),
            max_articles=int(os.environ.get("MAX_ARTICLES", "40")),
            max_age_hours=int(os.environ.get("MAX_AGE_HOURS", "24")),
            # Features
            include_reddit=os.environ.get("INCLUDE_REDDIT", "true").lower() == "true",
            include_rss=os.environ.get("INCLUDE_RSS", "true").lower() == "true",
            include_hackernews=os.environ.get("INCLUDE_HACKERNEWS", "true").lower() == "true",
            include_arxiv=os.environ.get("INCLUDE_ARXIV", "true").lower() == "true",
            include_github_trending=os.environ.get("INCLUDE_GITHUB_TRENDING", "true").lower() == "true",
            enable_ai_summary=os.environ.get("ENABLE_AI_SUMMARY", "true").lower() == "true",
            # Topic filtering
            enable_topic_filtering=os.environ.get("ENABLE_TOPIC_FILTERING", "false").lower() == "true",
            filter_topics=filter_topics,
            # GitHub settings
            github_history_days=int(os.environ.get("GITHUB_HISTORY_DAYS", "30")),
        )

    def validate(self) -> None:
        """Validate required configuration."""
        if not self.gmail_user:
            raise ValueError("GMAIL_USER is required")
        if not self.gmail_app_password:
            raise ValueError("GMAIL_APP_PASSWORD is required")
        if self.include_reddit and (not self.reddit_client_id or not self.reddit_client_secret):
            raise ValueError("Reddit credentials required when INCLUDE_REDDIT is true")
        if self.enable_ai_summary and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY required when ENABLE_AI_SUMMARY is true")
