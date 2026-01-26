"""Email formatter using Jinja2 templates."""

import os
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.models import Article
from src.utils import get_logger

logger = get_logger(__name__)


class EmailFormatter:
    """Formats articles into HTML and plain text emails."""

    SECTION_CONFIG = [
        {"key": "top", "title": "Top Stories", "icon": "🔥", "limit": 10},
        {"key": "research", "title": "Research & Papers", "icon": "📚", "sources": ["arxiv"]},
        {"key": "reddit", "title": "Reddit Discussions", "icon": "💬", "sources": ["reddit"]},
        {"key": "news", "title": "Industry News", "icon": "📰", "sources": ["rss"]},
    ]

    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize formatter.

        Args:
            template_dir: Path to templates directory.
        """
        if template_dir is None:
            # Default to templates/ in project root
            template_dir = Path(__file__).parent.parent.parent / "templates"

        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
        )

    def format(
        self,
        articles: List[Article],
        date: str,
        summary: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Format articles into email content.

        Args:
            articles: Ranked list of articles.
            date: Formatted date string.
            summary: Optional AI-generated summary.

        Returns:
            Tuple of (html_content, text_content).
        """
        # Organize articles into sections
        sections = self._organize_sections(articles)

        # Count unique sources
        sources = set(a.source_name for a in articles)

        # Prepare template context
        context = {
            "date": date,
            "summary": summary,
            "sections": sections,
            "article_count": len(articles),
            "source_count": len(sources),
        }

        # Render templates
        html_template = self.env.get_template("email.html")
        text_template = self.env.get_template("email.txt")

        html_content = html_template.render(**context)
        text_content = text_template.render(**context)

        logger.info(f"Formatted email with {len(articles)} articles in {len(sections)} sections")
        return html_content, text_content

    def _organize_sections(self, articles: List[Article]) -> List[dict]:
        """Organize articles into sections."""
        sections = []
        used_ids = set()

        for config in self.SECTION_CONFIG:
            section_articles = []

            if config["key"] == "top":
                # Top stories - take highest ranked regardless of source
                limit = config.get("limit", 10)
                for article in articles:
                    if article.id not in used_ids:
                        section_articles.append(self._format_article(article))
                        used_ids.add(article.id)
                        if len(section_articles) >= limit:
                            break
            else:
                # Source-specific sections
                sources = config.get("sources", [])
                for article in articles:
                    if article.id not in used_ids and article.source in sources:
                        section_articles.append(self._format_article(article))
                        used_ids.add(article.id)
                        if len(section_articles) >= 8:
                            break

            if section_articles:
                sections.append({
                    "title": config["title"],
                    "icon": config.get("icon", ""),
                    "articles": section_articles,
                })

        return sections

    def _format_article(self, article: Article) -> dict:
        """Format article for template."""
        return {
            "title": article.title,
            "url": article.url,
            "source_name": article.source_name,
            "score": article.score,
            "time_ago": self._time_ago(article.published_at),
        }

    def _time_ago(self, dt: datetime) -> str:
        """Format datetime as relative time."""
        now = datetime.now(timezone.utc)
        diff = now - dt

        hours = int(diff.total_seconds() / 3600)
        if hours < 1:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m ago"
        elif hours < 24:
            return f"{hours}h ago"
        else:
            days = hours // 24
            return f"{days}d ago"
