"""GitHub repository history tracking for 30-day deduplication."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from src.utils import get_logger

logger = get_logger(__name__)


class GitHubHistoryManager:
    """Manages 30-day history of shown GitHub repositories."""

    def __init__(self, storage_path: str = ".temp/github_history.json"):
        """
        Initialize the history manager.

        Args:
            storage_path: Path to JSON file for storing history.
        """
        self.storage_path = storage_path
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        """Create storage directory if it doesn't exist."""
        storage_dir = os.path.dirname(self.storage_path)
        if storage_dir:
            Path(storage_dir).mkdir(parents=True, exist_ok=True)

    def _create_empty_history(self) -> dict:
        """Create an empty history structure."""
        return {
            "schema_version": "1.0",
            "last_cleanup": datetime.utcnow().isoformat() + "Z",
            "repositories": {}
        }

    def _load_history(self) -> dict:
        """
        Load history from JSON file.

        Returns:
            History dictionary or empty history if file doesn't exist/is corrupt.
        """
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    logger.debug(f"Loaded history with {len(history.get('repositories', {}))} repos")
                    return history
            else:
                logger.info("No history file found, creating new one")
                return self._create_empty_history()
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load history file: {e}. Creating new history.")
            return self._create_empty_history()

    def _save_history(self, history: dict) -> None:
        """
        Save history to JSON file.

        Args:
            history: History dictionary to save.
        """
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved history with {len(history.get('repositories', {}))} repos")
        except IOError as e:
            logger.error(f"Failed to save history: {e}")

    def is_seen_recently(self, repo_id: str, days: int = 30) -> bool:
        """
        Check if a repository was shown in the last N days.

        Args:
            repo_id: Repository identifier (e.g., "github_openai_gpt-4")
            days: Number of days to look back

        Returns:
            True if repo was shown recently, False otherwise
        """
        history = self._load_history()
        repositories = history.get("repositories", {})

        if repo_id not in repositories:
            return False

        last_shown_str = repositories[repo_id].get("last_shown")
        if not last_shown_str:
            return False

        try:
            # Parse ISO format datetime (with or without 'Z')
            last_shown_str = last_shown_str.rstrip('Z')
            last_shown = datetime.fromisoformat(last_shown_str)
            cutoff = datetime.utcnow() - timedelta(days=days)

            is_recent = last_shown > cutoff
            if is_recent:
                logger.debug(f"Repo {repo_id} was shown recently (last: {last_shown_str})")
            return is_recent
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid date format for {repo_id}: {e}")
            return False

    def mark_as_shown(self, repo_id: str) -> None:
        """
        Record that a repository was shown today.

        Args:
            repo_id: Repository identifier to mark as shown
        """
        history = self._load_history()
        repositories = history.get("repositories", {})

        now = datetime.utcnow().isoformat() + "Z"

        if repo_id in repositories:
            # Update existing entry
            repositories[repo_id]["last_shown"] = now
            repositories[repo_id]["show_count"] = repositories[repo_id].get("show_count", 0) + 1
        else:
            # Create new entry
            repositories[repo_id] = {
                "first_seen": now,
                "last_shown": now,
                "show_count": 1
            }

        history["repositories"] = repositories
        self._save_history(history)
        logger.debug(f"Marked {repo_id} as shown")

    def cleanup_old_entries(self, days: int = 30) -> int:
        """
        Remove entries older than N days.

        Args:
            days: Remove entries not shown in last N days

        Returns:
            Number of entries removed
        """
        history = self._load_history()
        repositories = history.get("repositories", {})

        cutoff = datetime.utcnow() - timedelta(days=days)
        before_count = len(repositories)

        # Filter out old entries
        repositories = {
            repo_id: data
            for repo_id, data in repositories.items()
            if self._parse_datetime(data.get("last_shown")) > cutoff
        }

        removed_count = before_count - len(repositories)

        if removed_count > 0:
            history["repositories"] = repositories
            history["last_cleanup"] = datetime.utcnow().isoformat() + "Z"
            self._save_history(history)
            logger.info(f"Cleaned up {removed_count} old repository entries")

        return removed_count

    def _parse_datetime(self, date_str: Optional[str]) -> datetime:
        """
        Parse datetime string safely.

        Args:
            date_str: ISO format datetime string

        Returns:
            Parsed datetime or epoch if parsing fails
        """
        if not date_str:
            return datetime.min

        try:
            date_str = date_str.rstrip('Z')
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            return datetime.min

    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about the history.

        Returns:
            Dictionary with statistics (total_repos, shown_recently, etc.)
        """
        history = self._load_history()
        repositories = history.get("repositories", {})

        recent_count = sum(
            1 for repo_id in repositories.keys()
            if self.is_seen_recently(repo_id, days=30)
        )

        return {
            "total_repos": len(repositories),
            "shown_recently": recent_count,
            "last_cleanup": history.get("last_cleanup", "Never"),
            "schema_version": history.get("schema_version", "unknown")
        }
