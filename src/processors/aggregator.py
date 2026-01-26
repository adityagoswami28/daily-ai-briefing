"""Aggregator to collect articles from all sources."""

from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.collectors.base import BaseCollector
from src.models import Article
from src.utils import get_logger

logger = get_logger(__name__)


class Aggregator:
    """Aggregates articles from multiple collectors."""

    def __init__(self, collectors: List[BaseCollector]):
        """
        Initialize aggregator.

        Args:
            collectors: List of data source collectors.
        """
        self.collectors = collectors

    def collect_all(self, max_age_hours: int = 24) -> List[Article]:
        """
        Collect articles from all sources in parallel.

        Args:
            max_age_hours: Maximum age of articles to collect.

        Returns:
            Combined list of articles from all sources.
        """
        all_articles = []

        # Run collectors in parallel
        with ThreadPoolExecutor(max_workers=len(self.collectors)) as executor:
            futures = {
                executor.submit(c.collect, max_age_hours): c.source_name
                for c in self.collectors
            }

            for future in as_completed(futures):
                source = futures[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                    logger.info(f"Collected {len(articles)} articles from {source}")
                except Exception as e:
                    logger.error(f"Failed to collect from {source}: {e}")

        logger.info(f"Total articles collected: {len(all_articles)}")
        return all_articles
