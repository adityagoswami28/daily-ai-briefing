"""Topic-based article filtering for Daily AI Briefing."""

import re
from typing import List, Dict, Set
from collections import defaultdict

from src.models import Article
from src.utils import get_logger

logger = get_logger(__name__)


class TopicFilter:
    """Filters articles based on configured topics using smart keyword matching."""

    def __init__(self, topics: List[str]):
        """
        Initialize the topic filter.

        Args:
            topics: List of topics to filter for (e.g., ["OpenAI", "Claude", "MCP Framework"])
        """
        self.topics = topics
        self.exact_topics = []  # Single-word topics
        self.phrase_topics = []  # Multi-word topics
        self._preprocess_topics()

    def _preprocess_topics(self) -> None:
        """Preprocess topics into exact words and phrases for efficient matching."""
        for topic in self.topics:
            topic = topic.strip()
            if not topic:
                continue

            # Multi-word topics are treated as phrases
            if ' ' in topic:
                self.phrase_topics.append(topic)
            else:
                self.exact_topics.append(topic)

        logger.debug(
            f"Preprocessed topics: {len(self.exact_topics)} exact, {len(self.phrase_topics)} phrases"
        )

    def _matches_any_topic(self, article: Article) -> List[str]:
        """
        Check if article matches any configured topics.

        Args:
            article: Article to check

        Returns:
            List of matched topic names (empty if no matches)
        """
        # Combine searchable text from article
        searchable_text = " ".join([
            article.title or "",
            article.url or "",
            article.summary or "",
        ])
        text_lower = searchable_text.lower()

        matched_topics = []

        # Check exact word matches (with word boundaries)
        for topic in self.exact_topics:
            # Use word boundary regex to avoid false positives
            # e.g., "Claude" matches "Claude 3" but not "Claude Shannon"
            pattern = r'\b' + re.escape(topic.lower()) + r'\b'
            if re.search(pattern, text_lower):
                matched_topics.append(topic)

        # Check phrase matches
        for topic in self.phrase_topics:
            if topic.lower() in text_lower:
                matched_topics.append(topic)

        return matched_topics

    def filter(self, articles: List[Article]) -> List[Article]:
        """
        Filter articles to only include those matching configured topics.

        Args:
            articles: List of articles to filter

        Returns:
            Filtered list of articles that match at least one topic
        """
        if not self.topics:
            logger.warning("No topics configured for filtering, returning all articles")
            return articles

        if not articles:
            logger.warning("No articles to filter")
            return []

        matched_articles = []
        topic_match_counts = defaultdict(int)
        filtered_out_count = 0

        for article in articles:
            matched_topics = self._matches_any_topic(article)

            if matched_topics:
                matched_articles.append(article)
                # Track which topics matched for analytics
                for topic in matched_topics:
                    topic_match_counts[topic] += 1
            else:
                filtered_out_count += 1

        # Log filtering effectiveness
        logger.info(
            f"Topic filtering: {len(matched_articles)} matched, {filtered_out_count} filtered out"
        )

        if topic_match_counts:
            match_summary = ", ".join(
                f"{topic} ({count})" for topic, count in sorted(
                    topic_match_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            )
            logger.info(f"Topics matched: {match_summary}")

        # Handle edge case: no matches
        if not matched_articles:
            logger.warning(
                "No articles matched any topics! Returning top 5 articles to prevent empty email."
            )
            return articles[:5]

        return matched_articles

    def get_topic_stats(self, articles: List[Article]) -> Dict[str, int]:
        """
        Get statistics on topic matches across articles.

        Args:
            articles: Articles to analyze

        Returns:
            Dictionary mapping topic to match count
        """
        topic_counts = defaultdict(int)

        for article in articles:
            matched_topics = self._matches_any_topic(article)
            for topic in matched_topics:
                topic_counts[topic] += 1

        return dict(topic_counts)
