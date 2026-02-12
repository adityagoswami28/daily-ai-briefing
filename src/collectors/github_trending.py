"""GitHub Trending collector for popular repositories."""

from datetime import datetime, timezone
from typing import List, Optional
import re

import requests
from bs4 import BeautifulSoup

from src.collectors.base import BaseCollector
from src.models import Article
from src.utils import get_logger
from src.utils.github_history import GitHubHistoryManager

logger = get_logger(__name__)


class GitHubTrendingCollector(BaseCollector):
    """Collector for trending GitHub repositories."""

    # GitHub trending page URL
    TRENDING_URL = "https://github.com/trending"

    # AI-related keywords for optional filtering
    AI_KEYWORDS = [
        "ai", "llm", "gpt", "claude", "gemini", "llama",
        "machine learning", "deep learning", "neural",
        "transformer", "openai", "anthropic", "artificial intelligence",
        "chatgpt", "copilot", "diffusion", "generative",
        "language model", "foundation model", "agi",
        "ml", "nlp", "computer vision", "hugging face",
        "pytorch", "tensorflow", "keras", "scikit"
    ]

    def __init__(
        self,
        history_manager: Optional[GitHubHistoryManager] = None,
        filter_ai: bool = True,
        session: Optional[requests.Session] = None
    ):
        """
        Initialize GitHub Trending collector.

        Args:
            history_manager: Manager for tracking 30-day repo history
            filter_ai: Whether to filter for AI-related repos only
            session: Optional requests session
        """
        self.history_manager = history_manager or GitHubHistoryManager()
        self.filter_ai = filter_ai
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "DailyAIBriefing/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })

    @property
    def source_name(self) -> str:
        return "github"

    def collect(self, max_age_hours: int = 24) -> List[Article]:
        """
        Collect trending GitHub repositories.

        Args:
            max_age_hours: Not used for trending (always gets current trending)

        Returns:
            List of Article objects for trending repos
        """
        articles = []

        try:
            # Clean up old history entries
            removed = self.history_manager.cleanup_old_entries(days=30)
            if removed > 0:
                logger.debug(f"Cleaned up {removed} old repo entries from history")

            # Fetch trending repos
            trending_repos = self._scrape_trending_repos()
            logger.info(f"Fetched {len(trending_repos)} trending repositories")

            # Filter for AI-related repos if enabled
            if self.filter_ai:
                trending_repos = [
                    repo for repo in trending_repos
                    if self._is_ai_related(repo)
                ]
                logger.info(f"Filtered to {len(trending_repos)} AI-related repos")

            # Convert to articles and check history
            new_repos = 0
            skipped_repos = 0

            for repo in trending_repos:
                repo_id = self._get_repo_id(repo)

                # Check if we've shown this repo in the last 30 days
                if self.history_manager.is_seen_recently(repo_id, days=30):
                    skipped_repos += 1
                    logger.debug(f"Skipping {repo_id} (shown recently)")
                    continue

                article = self._to_article(repo)
                if article:
                    articles.append(article)
                    # Mark as shown
                    self.history_manager.mark_as_shown(repo_id)
                    new_repos += 1

            logger.info(
                f"GitHub trending: {new_repos} new repos, {skipped_repos} skipped (shown recently)"
            )

            # Log history stats
            stats = self.history_manager.get_stats()
            logger.debug(f"History stats: {stats}")

        except Exception as e:
            logger.error(f"Failed to collect GitHub trending repos: {e}")

        return articles

    def _scrape_trending_repos(self) -> List[dict]:
        """
        Scrape trending repositories from GitHub trending page.

        Returns:
            List of repository dictionaries
        """
        try:
            # Fetch the trending page
            resp = self.session.get(self.TRENDING_URL, timeout=10)
            resp.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(resp.text, 'html.parser')

            repos = []
            # Find all repo articles
            repo_articles = soup.find_all('article', class_='Box-row')

            for article in repo_articles[:25]:  # Limit to top 25
                try:
                    repo_data = self._parse_repo_article(article)
                    if repo_data:
                        repos.append(repo_data)
                except Exception as e:
                    logger.debug(f"Failed to parse repo article: {e}")
                    continue

            return repos

        except Exception as e:
            logger.error(f"Failed to scrape GitHub trending: {e}")
            return []

    def _parse_repo_article(self, article) -> Optional[dict]:
        """
        Parse a single repository article from the trending page.

        Args:
            article: BeautifulSoup article element

        Returns:
            Dictionary with repo information or None
        """
        try:
            # Get repo name and owner
            h2 = article.find('h2', class_='h3')
            if not h2:
                return None

            repo_link = h2.find('a')
            if not repo_link:
                return None

            repo_path = repo_link.get('href', '').strip('/')
            parts = repo_path.split('/')
            if len(parts) != 2:
                return None

            author, name = parts

            # Get description
            description_elem = article.find('p', class_='col-9')
            description = description_elem.get_text(strip=True) if description_elem else "No description available"

            # Get language
            language_elem = article.find('span', attrs={'itemprop': 'programmingLanguage'})
            language = language_elem.get_text(strip=True) if language_elem else ""

            # Get stars (total)
            stars = 0
            stars_link = article.find('a', href=re.compile(r'/stargazers$'))
            if stars_link:
                stars_text = stars_link.get_text(strip=True)
                # Remove commas and convert to int
                stars_text = stars_text.replace(',', '')
                try:
                    stars = int(stars_text)
                except (ValueError, TypeError):
                    stars = 0

            # Get stars today
            stars_today = 0
            stars_today_elem = article.find('span', class_='d-inline-block float-sm-right')
            if stars_today_elem:
                stars_today_text = stars_today_elem.get_text(strip=True)
                # Extract number from text like "1,234 stars today"
                match = re.search(r'([\d,]+)\s*stars?\s*today', stars_today_text)
                if match:
                    try:
                        stars_today = int(match.group(1).replace(',', ''))
                    except (ValueError, TypeError):
                        stars_today = 0

            return {
                'author': author,
                'name': name,
                'url': f"https://github.com/{repo_path}",
                'description': description,
                'language': language,
                'stars': stars,
                'currentPeriodStars': stars_today
            }

        except Exception as e:
            logger.debug(f"Error parsing repo article: {e}")
            return None

    def _is_ai_related(self, repo: dict) -> bool:
        """
        Check if a repository is AI-related.

        Args:
            repo: Repository dictionary from scraping

        Returns:
            True if repo is AI-related
        """
        name = repo.get("name", "").lower()
        description = repo.get("description", "").lower()
        language = repo.get("language", "").lower()

        # Combine searchable text
        text = f"{name} {description} {language}"

        # Check against AI keywords
        return any(keyword in text for keyword in self.AI_KEYWORDS)

    def _get_repo_id(self, repo: dict) -> str:
        """
        Generate a unique repository ID.

        Args:
            repo: Repository dictionary

        Returns:
            Unique ID string
        """
        author = repo.get("author", "unknown")
        name = repo.get("name", "unknown")
        return f"github_{author}_{name}".replace("/", "_").replace(" ", "_")

    def _to_article(self, repo: dict) -> Optional[Article]:
        """
        Convert GitHub repo to Article object.

        Args:
            repo: Repository dictionary from scraping

        Returns:
            Article object or None if conversion fails
        """
        try:
            author = repo.get("author", "")
            name = repo.get("name", "")
            description = repo.get("description", "No description available")
            url = repo.get("url", "")
            stars = repo.get("stars", 0)
            language = repo.get("language", "")
            current_period_stars = repo.get("currentPeriodStars", 0)

            # Create title with repo name and description
            title = f"{name}: {description}"

            # Create summary with additional metadata
            summary = f"{description}"
            if language:
                summary += f" | Language: {language}"
            if stars:
                summary += f" | Stars: {stars:,}"
            if current_period_stars:
                summary += f" | Today: +{current_period_stars}"

            # Truncate summary if too long
            if len(summary) > 500:
                summary = summary[:497] + "..."

            return Article(
                id=self._get_repo_id(repo),
                title=title,
                url=url,
                source="github",
                source_name="GitHub Trending",
                published_at=datetime.now(timezone.utc),  # Use current time
                summary=summary,
                score=stars,  # Use stars as score
                author=author,
                tags=[language] if language else []
            )

        except Exception as e:
            logger.warning(f"Failed to convert repo to article: {e}")
            return None
