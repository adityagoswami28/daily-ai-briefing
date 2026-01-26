"""Deduplicator to remove duplicate articles."""

from difflib import SequenceMatcher
from typing import List
from urllib.parse import urlparse

from src.models import Article
from src.utils import get_logger

logger = get_logger(__name__)


class Deduplicator:
    """Removes duplicate articles using URL and title matching."""

    SIMILARITY_THRESHOLD = 0.85

    def deduplicate(self, articles: List[Article]) -> List[Article]:
        """
        Remove duplicate articles.

        Uses two-phase approach:
        1. Exact URL deduplication
        2. Fuzzy title matching

        Args:
            articles: List of articles to deduplicate.

        Returns:
            Deduplicated list of articles.
        """
        # Phase 1: URL deduplication
        url_unique = self._dedupe_by_url(articles)
        logger.info(f"After URL dedup: {len(url_unique)} (from {len(articles)})")

        # Phase 2: Title similarity
        final = self._dedupe_by_title(url_unique)
        logger.info(f"After title dedup: {len(final)}")

        return final

    def _dedupe_by_url(self, articles: List[Article]) -> List[Article]:
        """Remove articles with identical normalized URLs."""
        seen_urls = set()
        unique = []

        for article in articles:
            norm_url = self._normalize_url(article.url)
            if norm_url not in seen_urls:
                seen_urls.add(norm_url)
                unique.append(article)

        return unique

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison."""
        parsed = urlparse(url)

        # Remove www prefix
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        # Remove trailing slashes, query params for comparison
        path = parsed.path.rstrip("/").lower()

        return f"{netloc}{path}"

    def _dedupe_by_title(self, articles: List[Article]) -> List[Article]:
        """Remove articles with similar titles."""
        final = []

        for article in articles:
            is_duplicate = False
            title_lower = article.title.lower()

            for existing in final:
                similarity = SequenceMatcher(
                    None, title_lower, existing.title.lower()
                ).ratio()

                if similarity > self.SIMILARITY_THRESHOLD:
                    is_duplicate = True
                    # Keep the one with higher score
                    if (article.score or 0) > (existing.score or 0):
                        final.remove(existing)
                        final.append(article)
                    break

            if not is_duplicate:
                final.append(article)

        return final
