"""AI-powered summarizer using OpenAI."""

from typing import List, Optional

from openai import OpenAI

from src.models import Article
from src.utils import get_logger

logger = get_logger(__name__)


class Summarizer:
    """Generates AI-powered summaries of the daily digest."""

    def __init__(self, api_key: str):
        """
        Initialize summarizer.

        Args:
            api_key: OpenAI API key.
        """
        self.client = OpenAI(api_key=api_key)

    def summarize_digest(
        self, articles: List[Article], max_articles: int = 15
    ) -> Optional[str]:
        """
        Generate an executive summary of top articles.

        Args:
            articles: List of top articles to summarize.
            max_articles: Maximum number of articles to include.

        Returns:
            Summary text or None if generation fails.
        """
        try:
            # Prepare article titles for summarization
            top_articles = articles[:max_articles]
            article_list = "\n".join(
                f"- [{a.source_name}] {a.title}" for a in top_articles
            )

            prompt = f"""Here are today's top AI news headlines and updates:

{article_list}

Please provide a brief 3-4 sentence executive summary highlighting the most significant developments and themes. Focus on what's most impactful or noteworthy for someone following AI developments. Be concise and informative."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )

            summary = response.choices[0].message.content.strip()
            logger.info("Generated AI summary")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return None
