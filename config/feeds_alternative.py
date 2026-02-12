"""Alternative RSS feed URLs that are more accessible (not Cloudflare-protected)."""

# These feeds are more likely to work without being blocked
ALTERNATIVE_RSS_FEEDS = {
    # Academic & Research (usually open)
    "arXiv AI": "http://export.arxiv.org/rss/cs.AI",
    "arXiv ML": "http://export.arxiv.org/rss/cs.LG",

    # Open source & community (usually accessible)
    "Python Weekly": "https://www.pythonweekly.com/rss/",
    "Import AI": "https://jack-clark.net/feed/",  # Miles Brundage's newsletter

    # Alternative news sources (less likely blocked)
    "Ars Technica Science": "https://feeds.arstechnica.com/arstechnica/science",
    "MIT Technology Review AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed",

    # Blog aggregators
    "Hacker News Best": "https://hnrss.org/best",  # Alternative HN feed
    "Lobsters AI": "https://lobste.rs/t/ai.rss",

    # Individual researcher blogs (usually open)
    "Andrej Karpathy": "http://karpathy.github.io/feed.xml",
    "Distill.pub": "https://distill.pub/rss.xml",

    # Company engineering blogs (often more accessible)
    "Netflix Tech Blog": "https://netflixtechblog.com/feed",
    "Uber Engineering": "https://eng.uber.com/feed/",
    "Airbnb Engineering": "https://medium.com/feed/airbnb-engineering",
}

# Note: You can replace RSS_FEEDS in config/feeds.py with these
# or create a hybrid approach using both
