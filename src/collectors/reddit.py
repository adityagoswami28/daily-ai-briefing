"""Reddit collector for AI-related subreddits."""

from datetime import datetime, timezone, timedelta
from typing import List, Optional

import praw
from praw.models import Submission

from src.collectors.base import BaseCollector
from src.models import Article
from src.utils import get_logger

logger = get_logger(__name__)


class RedditCollector(BaseCollector):
    """Collector for posts from AI-related subreddits."""

    DEFAULT_SUBREDDITS = [
        "MachineLearning",
        "artificial",
        "LocalLLaMA",
        "ChatGPT",
        "singularity",
        "OpenAI",
    ]

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str = "DailyAIBriefing/1.0",
        subreddits: Optional[List[str]] = None,
    ):
        """
        Initialize Reddit collector.

        Args:
            client_id: Reddit API client ID.
            client_secret: Reddit API client secret.
            user_agent: User agent string.
            subreddits: List of subreddits to monitor.
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        self.subreddits = subreddits or self.DEFAULT_SUBREDDITS

    @property
    def source_name(self) -> str:
        return "reddit"

    def collect(self, max_age_hours: int = 24) -> List[Article]:
        """Collect posts from configured subreddits."""
        articles = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        for sub_name in self.subreddits:
            try:
                sub_articles = self._collect_subreddit(sub_name, cutoff)
                articles.extend(sub_articles)
                logger.info(f"Collected {len(sub_articles)} posts from r/{sub_name}")
            except Exception as e:
                logger.warning(f"Failed to collect from r/{sub_name}: {e}")

        return articles

    def _collect_subreddit(
        self, sub_name: str, cutoff: datetime
    ) -> List[Article]:
        """Collect posts from a single subreddit."""
        articles = []
        subreddit = self.reddit.subreddit(sub_name)

        # Get hot posts (good balance of recent + popular)
        for post in subreddit.hot(limit=30):
            article = self._to_article(post, sub_name, cutoff)
            if article:
                articles.append(article)

        return articles

    def _to_article(
        self, post: Submission, sub_name: str, cutoff: datetime
    ) -> Optional[Article]:
        """Convert Reddit submission to Article."""
        published = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)

        # Filter by age
        if published < cutoff:
            return None

        # Filter by minimum score (reduce noise)
        if post.score < 20:
            return None

        # Skip removed/deleted posts
        if post.removed_by_category or post.selftext == "[removed]":
            return None

        # Determine URL (external link or Reddit discussion)
        if post.is_self:
            url = f"https://reddit.com{post.permalink}"
        else:
            url = post.url

        return Article(
            id=f"reddit_{post.id}",
            title=post.title,
            url=url,
            source="reddit",
            source_name=f"r/{sub_name}",
            published_at=published,
            summary=self._get_summary(post),
            score=post.score,
            author=str(post.author) if post.author else None,
        )

    def _get_summary(self, post: Submission) -> Optional[str]:
        """Extract summary from post."""
        if post.is_self and post.selftext:
            text = post.selftext
            if len(text) > 500:
                return text[:500] + "..."
            return text
        return None
