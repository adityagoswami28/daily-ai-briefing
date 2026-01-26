"""RSS feed collector for AI news sources."""

import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

import feedparser
from dateutil import parser as date_parser

from src.collectors.base import BaseCollector
from src.models import Article
from src.utils import get_logger

logger = get_logger(__name__)


class RSSCollector(BaseCollector):
    """Collector for RSS feeds from various AI news sources."""

    def __init__(self, feeds: Dict[str, str]):
        """
        Initialize RSS collector.

        Args:
            feeds: Dictionary mapping feed names to URLs.
        """
        self.feeds = feeds

    @property
    def source_name(self) -> str:
        return "rss"

    def collect(self, max_age_hours: int = 24) -> List[Article]:
        """Collect articles from all configured RSS feeds."""
        articles = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        for feed_name, feed_url in self.feeds.items():
            try:
                feed_articles = self._parse_feed(feed_name, feed_url, cutoff)
                articles.extend(feed_articles)
                logger.info(f"Collected {len(feed_articles)} articles from {feed_name}")
            except Exception as e:
                logger.warning(f"Failed to parse {feed_name}: {e}")

        return articles

    def _parse_feed(
        self, feed_name: str, feed_url: str, cutoff: datetime
    ) -> List[Article]:
        """Parse a single RSS feed."""
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries[:15]:  # Limit per feed
            published = self._parse_date(entry)
            if published and published < cutoff:
                continue

            article = Article(
                id=self._generate_id(entry),
                title=self._clean_title(entry.get("title", "Untitled")),
                url=entry.get("link", ""),
                source="rss",
                source_name=feed_name,
                published_at=published or datetime.now(timezone.utc),
                summary=self._get_summary(entry),
                author=entry.get("author"),
            )
            articles.append(article)

        return articles

    def _parse_date(self, entry) -> Optional[datetime]:
        """Parse publication date from feed entry."""
        date_str = entry.get("published") or entry.get("updated")
        if not date_str:
            return None

        try:
            dt = date_parser.parse(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            return None

    def _generate_id(self, entry) -> str:
        """Generate unique ID for an entry."""
        unique_str = entry.get("id") or entry.get("link") or entry.get("title", "")
        return f"rss_{hashlib.md5(unique_str.encode()).hexdigest()[:12]}"

    def _clean_title(self, title: str) -> str:
        """Clean up title string."""
        return title.strip().replace("\n", " ")

    def _get_summary(self, entry) -> Optional[str]:
        """Extract summary from feed entry."""
        summary = entry.get("summary") or entry.get("description", "")
        if summary:
            # Remove HTML tags (basic)
            import re
            summary = re.sub(r"<[^>]+>", "", summary)
            return summary[:500] if len(summary) > 500 else summary
        return None
