"""Main orchestrator for Daily AI Briefing."""

import sys
from datetime import datetime

from dotenv import load_dotenv

from src.utils import Config, setup_logging, get_logger
from src.collectors import RSSCollector, HackerNewsCollector, RedditCollector, ArxivCollector
from src.processors import Aggregator, Deduplicator, Ranker, Summarizer
from src.email import EmailFormatter, GmailSender
from config import RSS_FEEDS


def main():
    """Run the daily AI briefing pipeline."""
    # Load environment variables from .env file (for local development)
    load_dotenv()

    # Setup logging
    setup_logging()
    logger = get_logger(__name__)

    logger.info("=" * 50)
    logger.info("Starting Daily AI Briefing")
    logger.info("=" * 50)

    try:
        # Load configuration
        config = Config.from_env()
        config.validate()
        logger.info("Configuration loaded successfully")

        # Initialize collectors based on config
        collectors = []

        if config.include_rss:
            collectors.append(RSSCollector(RSS_FEEDS))
            logger.info(f"RSS collector enabled with {len(RSS_FEEDS)} feeds")

        if config.include_hackernews:
            collectors.append(HackerNewsCollector())
            logger.info("Hacker News collector enabled")

        if config.include_reddit and config.reddit_client_id:
            collectors.append(
                RedditCollector(
                    client_id=config.reddit_client_id,
                    client_secret=config.reddit_client_secret,
                    user_agent=config.reddit_user_agent,
                    subreddits=config.subreddits,
                )
            )
            logger.info(f"Reddit collector enabled for {len(config.subreddits)} subreddits")

        if config.include_arxiv:
            collectors.append(ArxivCollector())
            logger.info("ArXiv collector enabled")

        if not collectors:
            logger.error("No collectors enabled! Check your configuration.")
            sys.exit(1)

        # Collect articles from all sources
        logger.info("Collecting articles...")
        aggregator = Aggregator(collectors)
        all_articles = aggregator.collect_all(max_age_hours=config.max_age_hours)
        logger.info(f"Collected {len(all_articles)} articles from all sources")

        if not all_articles:
            logger.warning("No articles collected! Exiting.")
            sys.exit(0)

        # Deduplicate
        logger.info("Deduplicating articles...")
        deduplicator = Deduplicator()
        unique_articles = deduplicator.deduplicate(all_articles)
        logger.info(f"After deduplication: {len(unique_articles)} articles")

        # Rank articles
        logger.info("Ranking articles...")
        ranker = Ranker()
        ranked_articles = ranker.rank(unique_articles)

        # Limit to max articles
        final_articles = ranked_articles[: config.max_articles]
        logger.info(f"Final article count: {len(final_articles)}")

        # Generate AI summary (optional)
        summary = None
        if config.enable_ai_summary and config.openai_api_key:
            logger.info("Generating AI summary...")
            summarizer = Summarizer(config.openai_api_key)
            summary = summarizer.summarize_digest(final_articles)
            if summary:
                logger.info("AI summary generated successfully")

        # Format email
        logger.info("Formatting email...")
        formatter = EmailFormatter()
        today = datetime.now().strftime("%A, %B %d, %Y")
        html_content, text_content = formatter.format(
            articles=final_articles,
            date=today,
            summary=summary,
        )

        # Send email
        logger.info(f"Sending email to {config.recipient_email}...")
        sender = GmailSender(config.gmail_user, config.gmail_app_password)
        subject = f"Daily AI Briefing - {datetime.now().strftime('%B %d, %Y')}"

        success = sender.send(
            to_email=config.recipient_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

        if success:
            logger.info("=" * 50)
            logger.info("Daily AI Briefing sent successfully!")
            logger.info("=" * 50)
        else:
            logger.error("Failed to send email")
            sys.exit(1)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
