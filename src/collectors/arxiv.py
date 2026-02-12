"""ArXiv collector for recent AI/ML papers."""

from datetime import datetime, timezone, timedelta
from typing import List

import arxiv

from src.collectors.base import BaseCollector
from src.models import Article
from src.utils import get_logger

logger = get_logger(__name__)


class ArxivCollector(BaseCollector):
    """Collector for recent AI/ML papers from ArXiv."""

    CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE"]

    def __init__(self, max_results: int = 30):
        """
        Initialize ArXiv collector.

        Args:
            max_results: Maximum number of papers to fetch.
        """
        self.max_results = max_results

    @property
    def source_name(self) -> str:
        return "arxiv"

    def collect(self, max_age_hours: int = 48) -> List[Article]:
        """
        Collect recent papers from ArXiv.

        Note: ArXiv updates are typically daily, so we use a longer window.
        """
        articles = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

        try:
            # Build query for AI-related categories
            category_query = " OR ".join(f"cat:{cat}" for cat in self.CATEGORIES)

            search = arxiv.Search(
                query=category_query,
                max_results=self.max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )

            client = arxiv.Client()

            for result in client.results(search):
                article = self._to_article(result, cutoff)
                if article:
                    articles.append(article)

            logger.info(f"Collected {len(articles)} papers from ArXiv")

        except Exception as e:
            logger.error(f"Failed to collect ArXiv papers: {e}")

        return articles

    def _to_article(self, result, cutoff: datetime) -> Article | None:
        """Convert ArXiv result to Article."""
        # ArXiv uses naive datetime, assume UTC
        published = result.published
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)

        if published < cutoff:
            return None

        # Get primary category
        primary_cat = result.primary_category

        # Extract category tags - handle both string and object types
        tags = []
        for cat in result.categories[:3]:
            if isinstance(cat, str):
                tags.append(cat)
            elif hasattr(cat, 'term'):
                tags.append(cat.term)
            else:
                tags.append(str(cat))

        return Article(
            id=f"arxiv_{result.entry_id.split('/')[-1]}",
            title=result.title.replace("\n", " "),
            url=result.entry_id,
            source="arxiv",
            source_name=f"ArXiv [{primary_cat}]",
            published_at=published,
            summary=self._truncate_summary(result.summary),
            author=self._format_authors(result.authors),
            tags=tags,
        )

    def _truncate_summary(self, summary: str) -> str:
        """Truncate summary to reasonable length."""
        summary = summary.replace("\n", " ").strip()
        if len(summary) > 500:
            return summary[:497] + "..."
        return summary

    def _format_authors(self, authors: list) -> str:
        """Format author list."""
        names = [str(a) for a in authors[:3]]
        if len(authors) > 3:
            names.append(f"et al. (+{len(authors) - 3})")
        return ", ".join(names)
