"""Ranker to score and sort articles by relevance."""

from datetime import datetime, timezone
from typing import List

from src.models import Article
from src.utils import get_logger

logger = get_logger(__name__)


class Ranker:
    """Scores and ranks articles by relevance and importance."""

    # Source reputation weights
    SOURCE_WEIGHTS = {
        # Company blogs (high authority)
        "OpenAI Blog": 5.0,
        "Anthropic Blog": 5.0,
        "Google AI Blog": 4.5,
        "DeepMind Blog": 4.5,
        "Meta AI Blog": 4.0,
        "Microsoft AI Blog": 4.0,
        "Hugging Face Blog": 4.0,

        # Research
        "BAIR Blog": 4.0,
        "MIT News AI": 3.5,
        "Stanford HAI": 3.5,

        # ArXiv
        "arxiv": 3.5,

        # Hacker News
        "Hacker News": 3.0,

        # Reddit (varies by subreddit)
        "r/MachineLearning": 3.5,
        "r/LocalLLaMA": 3.0,
        "r/artificial": 2.5,
        "r/OpenAI": 2.5,
        "r/ChatGPT": 2.0,
        "r/singularity": 2.0,

        # News
        "VentureBeat AI": 2.5,
        "TechCrunch AI": 2.5,
        "The Verge AI": 2.0,
        "Ars Technica": 2.0,
        "Wired AI": 2.0,
    }

    def rank(self, articles: List[Article]) -> List[Article]:
        """
        Score and rank articles.

        Args:
            articles: List of articles to rank.

        Returns:
            Sorted list with highest scored articles first.
        """
        for article in articles:
            article.computed_score = self._compute_score(article)

        ranked = sorted(articles, key=lambda x: x.computed_score, reverse=True)
        logger.info(f"Ranked {len(ranked)} articles")
        return ranked

    def _compute_score(self, article: Article) -> float:
        """Compute relevance score for an article."""
        score = 0.0

        # Engagement score (upvotes, points)
        if article.score:
            # Logarithmic scale to avoid domination by viral posts
            import math
            score += min(math.log10(article.score + 1) * 2, 8)

        # Source reputation
        source_weight = self._get_source_weight(article)
        score += source_weight

        # Recency bonus
        score += self._recency_bonus(article.published_at)

        return score

    def _get_source_weight(self, article: Article) -> float:
        """Get source reputation weight."""
        # Check exact source name first
        if article.source_name in self.SOURCE_WEIGHTS:
            return self.SOURCE_WEIGHTS[article.source_name]

        # Check source type
        if article.source in self.SOURCE_WEIGHTS:
            return self.SOURCE_WEIGHTS[article.source]

        # Check if it's an ArXiv category
        if article.source == "arxiv":
            return 3.5

        # Default weight
        return 1.0

    def _recency_bonus(self, published_at: datetime) -> float:
        """Calculate recency bonus."""
        now = datetime.now(timezone.utc)
        age_hours = (now - published_at).total_seconds() / 3600

        if age_hours < 3:
            return 4.0
        elif age_hours < 6:
            return 3.0
        elif age_hours < 12:
            return 2.0
        elif age_hours < 24:
            return 1.0
        return 0.0
