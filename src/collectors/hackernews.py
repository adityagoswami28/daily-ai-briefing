"""Hacker News collector for AI-related stories."""

from datetime import datetime, timezone, timedelta
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from src.collectors.base import BaseCollector
from src.models import Article
from src.utils import get_logger

logger = get_logger(__name__)


class HackerNewsCollector(BaseCollector):
    """Collector for AI-related stories from Hacker News."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    AI_KEYWORDS = [
        "ai", "llm", "gpt", "claude", "gemini", "llama",
        "machine learning", "deep learning", "neural",
        "transformer", "openai", "anthropic", "artificial intelligence",
        "chatgpt", "copilot", "diffusion", "generative",
        "language model", "foundation model", "agi",
        "ml", "nlp", "computer vision", "hugging face",
    ]

    def __init__(self, session: Optional[requests.Session] = None):
        """Initialize Hacker News collector."""
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": "DailyAIBriefing/1.0"})

    @property
    def source_name(self) -> str:
        return "hackernews"

    def collect(self, max_age_hours: int = 24) -> List[Article]:
        """Collect AI-related stories from Hacker News."""
        articles = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        try:
            # Get top and best stories
            story_ids = self._get_story_ids()
            logger.info(f"Fetching {len(story_ids)} HN stories")

            # Fetch stories in parallel
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {
                    executor.submit(self._fetch_story, sid): sid
                    for sid in story_ids
                }

                for future in as_completed(futures):
                    try:
                        story = future.result()
                        if story and self._is_ai_related(story):
                            article = self._to_article(story, cutoff)
                            if article:
                                articles.append(article)
                    except Exception as e:
                        logger.debug(f"Error fetching story: {e}")

            logger.info(f"Collected {len(articles)} AI-related HN stories")

        except Exception as e:
            logger.error(f"Failed to collect HN stories: {e}")

        return articles

    def _get_story_ids(self) -> List[int]:
        """Get top and best story IDs."""
        ids = set()

        for endpoint in ["topstories", "beststories"]:
            try:
                resp = self.session.get(
                    f"{self.BASE_URL}/{endpoint}.json", timeout=10
                )
                resp.raise_for_status()
                ids.update(resp.json()[:100])  # Top 100 from each
            except Exception as e:
                logger.warning(f"Failed to get {endpoint}: {e}")

        return list(ids)[:150]  # Cap total

    def _fetch_story(self, story_id: int) -> Optional[dict]:
        """Fetch a single story."""
        try:
            resp = self.session.get(
                f"{self.BASE_URL}/item/{story_id}.json", timeout=5
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    def _is_ai_related(self, story: dict) -> bool:
        """Check if a story is AI-related."""
        title = story.get("title", "").lower()
        url = story.get("url", "").lower()
        text = f"{title} {url}"

        return any(kw in text for kw in self.AI_KEYWORDS)

    def _to_article(self, story: dict, cutoff: datetime) -> Optional[Article]:
        """Convert HN story to Article."""
        timestamp = story.get("time")
        if not timestamp:
            return None

        published = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        if published < cutoff:
            return None

        # Use HN discussion URL if no external URL
        url = story.get("url") or f"https://news.ycombinator.com/item?id={story['id']}"

        return Article(
            id=f"hn_{story['id']}",
            title=story.get("title", "Untitled"),
            url=url,
            source="hackernews",
            source_name="Hacker News",
            published_at=published,
            score=story.get("score", 0),
            author=story.get("by"),
        )
