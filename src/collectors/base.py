"""Base collector interface for data sources."""

from abc import ABC, abstractmethod
from typing import List

from src.models import Article


class BaseCollector(ABC):
    """Abstract base class for all data source collectors."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this data source."""
        pass

    @abstractmethod
    def collect(self, max_age_hours: int = 24) -> List[Article]:
        """
        Collect articles from the data source.

        Args:
            max_age_hours: Maximum age of articles to collect in hours.

        Returns:
            List of Article objects.
        """
        pass
