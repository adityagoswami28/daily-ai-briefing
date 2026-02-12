# Daily AI Briefing

An automated system that aggregates AI news from multiple sources and delivers a curated email digest daily at 8:00 AM EST. Stay informed with the latest developments in artificial intelligence without the noise.

## Features

- **Multi-Source Aggregation**: Collects AI news from:
  - Hacker News (40+ articles daily)
  - ArXiv research papers (30 papers daily)
  - GitHub Trending repositories (5-10 trending AI repos)
  - RSS feeds from major tech blogs (optional, many blocked by Cloudflare)
  - Reddit AI communities (optional)

- **Smart Content Curation**:
  - Deduplication to remove repeated articles
  - Intelligent ranking based on score and recency
  - Topic-based filtering for precise content targeting
  - 30-day repository history to prevent duplicate GitHub trending items

- **AI-Powered Summaries**: GPT-4o-mini generates executive summaries of daily highlights

- **Customizable Filtering**: Configure specific topics to follow (e.g., "OpenAI", "Claude", "MCP Framework")

- **Automated Delivery**: GitHub Actions runs the briefing daily and emails you the digest

- **Beautiful Email Format**: Clean, responsive HTML emails optimized for all devices

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Running Locally](#running-locally)
  - [GitHub Actions Deployment](#github-actions-deployment)
- [Project Structure](#project-structure)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Recent Updates](#recent-updates)

## Prerequisites

Before setting up the Daily AI Briefing, ensure you have:

- **Python 3.11+**: Download from [python.org](https://www.python.org/downloads/)
- **pip**: Python package installer (included with Python)
- **Git**: For version control and GitHub Actions deployment
- **A Gmail account**: For sending emails via SMTP

### Required API Keys

1. **Gmail App Password** (Required)
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Factor Authentication if not already enabled
   - Navigate to "App passwords"
   - Generate a new app password for "Mail"
   - Save the 16-character password

2. **OpenAI API Key** (Required for AI summaries)
   - Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Note: Uses gpt-4o-mini model (cost-effective, ~$0.01 per digest)

### Optional API Keys

3. **Reddit API Credentials** (Optional, only if `INCLUDE_REDDIT=true`)
   - Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
   - Click "Create App" or "Create Another App"
   - Choose "script" type
   - Fill in name and redirect URI (can be http://localhost:8080)
   - Save the client ID and client secret

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/daily_ai_briefing.git
cd daily_ai_briefing
```

### 2. Set Up Python Environment

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your favorite text editor and add your credentials. See [Configuration](#configuration) section for details.

## Configuration

The `.env` file controls all aspects of the briefing system. Here's a complete breakdown:

### Gmail SMTP Configuration (Required)

```bash
# Your Gmail address
GMAIL_USER=your_email@gmail.com

# Gmail App Password (NOT your regular Gmail password)
GMAIL_APP_PASSWORD=your_16_char_app_password

# Email recipient (defaults to GMAIL_USER if not set)
RECIPIENT_EMAIL=your_email@gmail.com
```

### OpenAI API (Required for AI Summaries)

```bash
# Get your key at: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-api-key
```

### Reddit API (Optional)

```bash
# Only needed if INCLUDE_REDDIT=true
# Create app at: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=DailyAIBriefing/1.0
```

### Content Settings

```bash
# Timezone for scheduling (default: America/New_York)
TIMEZONE=America/New_York

# Maximum number of articles in the email (default: 40)
MAX_ARTICLES=40

# Maximum age of articles in hours (default: 72 for 3 days)
# Recommended: 72 for better coverage, 24 for only recent news
MAX_AGE_HOURS=72
```

### Feature Flags

Control which sources to include:

```bash
# RSS feeds (many are blocked by Cloudflare - recommend: false)
INCLUDE_RSS=false

# Hacker News (highly recommended - primary news source)
INCLUDE_HACKERNEWS=true

# Reddit AI communities (optional)
INCLUDE_REDDIT=false

# ArXiv research papers (recommended)
INCLUDE_ARXIV=true

# GitHub trending repositories (recommended)
INCLUDE_GITHUB_TRENDING=true

# AI-powered summary generation
ENABLE_AI_SUMMARY=true
```

### Topic Filtering (Advanced)

Filter articles to only include specific topics:

```bash
# Enable strict topic-based filtering
ENABLE_TOPIC_FILTERING=true

# Comma-separated list of topics to track
# Supports exact words (e.g., "OpenAI") and phrases (e.g., "MCP Framework")
FILTER_TOPICS=OpenAI,Claude,Google Gemini,NotebookLM,Apple,MCP Framework,Claude Skills

# Days to track GitHub repos before allowing repeats (default: 30)
GITHUB_HISTORY_DAYS=30
```

**How Topic Filtering Works**:
- Articles are matched if they contain ANY of the configured topics
- Single words use exact word boundary matching ("Claude" matches "Claude 3.5" but not "Claudette")
- Phrases match anywhere in the text ("MCP Framework" matches any occurrence)
- Searches across article title, URL, and summary
- Falls back to top 5 articles if no matches found (prevents empty emails)

### Recommended Configuration

For optimal results with current source availability:

```bash
# Content Sources (based on what works reliably)
INCLUDE_RSS=false              # Most RSS feeds blocked by Cloudflare
INCLUDE_HACKERNEWS=true        # 40+ articles daily - primary source
INCLUDE_ARXIV=true             # 30 papers daily - research updates
INCLUDE_GITHUB_TRENDING=true   # 5-10 repos daily - trending projects
INCLUDE_REDDIT=false           # Optional, requires API credentials

# Content Settings
MAX_AGE_HOURS=72               # 3 days for better coverage
MAX_ARTICLES=40                # Generous limit

# AI Features
ENABLE_AI_SUMMARY=true         # GPT-4o-mini summary
ENABLE_TOPIC_FILTERING=true    # Focus on specific topics
```

## Usage

### Running Locally

Once configured, run the briefing manually:

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the briefing
python -m src.main
```

**What happens**:
1. Collects articles from enabled sources (Hacker News, ArXiv, GitHub, etc.)
2. Deduplicates and filters content based on your topics
3. Ranks articles by relevance and popularity
4. Generates AI summary (if enabled)
5. Formats a beautiful HTML email
6. Sends the email to your configured recipient

**Expected output**:
```
==================================================
Starting Daily AI Briefing
==================================================
Configuration loaded successfully
Hacker News collector enabled
ArXiv collector enabled
GitHub Trending collector enabled
Collecting articles...
Collected 87 articles from all sources
After deduplication: 82 articles
Topic filtering enabled with 7 topics
After topic filtering: 34 articles
Ranking articles...
Final article count: 34
Generating AI summary...
AI summary generated successfully
Formatting email...
Sending email to your_email@gmail.com...
==================================================
Daily AI Briefing sent successfully!
==================================================
```

### GitHub Actions Deployment

Automate the daily briefing using GitHub Actions:

#### 1. Push to GitHub

```bash
git add .
git commit -m "Initial setup"
git remote add origin https://github.com/yourusername/daily_ai_briefing.git
git push -u origin main
```

#### 2. Add Secrets to GitHub

Go to your repository on GitHub:
1. Click **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret** for each of the following:

**Required Secrets**:
- `GMAIL_USER`: Your Gmail address
- `GMAIL_APP_PASSWORD`: Your Gmail app password (16 characters)
- `RECIPIENT_EMAIL`: Email address to receive the briefing
- `OPENAI_API_KEY`: Your OpenAI API key

**Optional Secrets** (only if `INCLUDE_REDDIT=true`):
- `REDDIT_CLIENT_ID`: Your Reddit app client ID
- `REDDIT_CLIENT_SECRET`: Your Reddit app client secret

#### 3. Configure Workflow

The workflow is already configured in `.github/workflows/daily_briefing.yml`:

```yaml
# Runs daily at 8:00 AM EST (13:00 UTC)
schedule:
  - cron: '0 13 * * *'
```

To change the schedule time:
- 8:00 AM EST = `'0 13 * * *'`
- 9:00 AM EST = `'0 14 * * *'`
- 6:00 AM EST = `'0 11 * * *'`

**Note**: Adjust for Daylight Saving Time if needed (EDT = UTC-4, EST = UTC-5)

#### 4. Test the Workflow

Manually trigger a test run:
1. Go to **Actions** tab in your GitHub repository
2. Select "Daily AI Briefing" workflow
3. Click **Run workflow** button
4. Check your email for the briefing

#### 5. Monitor Runs

View workflow execution logs:
- Go to **Actions** tab
- Click on any workflow run to see detailed logs
- Failed runs will upload error logs as artifacts

## Project Structure

```
daily_ai_briefing/
├── .github/
│   └── workflows/
│       └── daily_briefing.yml    # GitHub Actions workflow for scheduling
├── config/
│   ├── __init__.py
│   └── feeds.py                  # RSS feed URLs (many blocked by Cloudflare)
├── src/
│   ├── main.py                   # Entry point - orchestrates entire pipeline
│   ├── models.py                 # Article dataclass definition
│   ├── collectors/               # Data source collectors
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract base collector class
│   │   ├── rss.py               # RSS feed collector
│   │   ├── hackernews.py        # Hacker News API collector
│   │   ├── reddit.py            # Reddit API collector
│   │   ├── arxiv.py             # ArXiv research paper collector
│   │   └── github_trending.py   # GitHub trending repositories scraper
│   ├── processors/               # Content processing pipeline
│   │   ├── __init__.py
│   │   ├── aggregator.py        # Combines articles from all sources
│   │   ├── deduplicator.py      # Removes duplicate articles
│   │   ├── ranker.py            # Ranks articles by score/recency
│   │   ├── topic_filter.py      # Filters articles by configured topics
│   │   └── summarizer.py        # Generates AI summaries with GPT-4o-mini
│   ├── email/                    # Email generation and delivery
│   │   ├── __init__.py
│   │   ├── formatter.py         # Formats HTML/text email content
│   │   └── sender.py            # Sends email via Gmail SMTP
│   └── utils/                    # Utilities and configuration
│       ├── __init__.py
│       ├── config.py            # Configuration management from .env
│       ├── logger.py            # Logging setup
│       └── github_history.py    # 30-day GitHub repo tracking
├── templates/
│   ├── email.html               # Jinja2 HTML email template
│   └── email.txt                # Plain text email template
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

### Key Components

**Data Collection Pipeline**:
1. `collectors/` - Fetch articles from various sources
2. `processors/aggregator.py` - Combine all articles
3. `processors/deduplicator.py` - Remove duplicates based on URLs
4. `processors/topic_filter.py` - Filter by configured topics
5. `processors/ranker.py` - Score and rank by relevance
6. `processors/summarizer.py` - Generate AI summary

**Email Generation**:
1. `email/formatter.py` - Render Jinja2 templates with article data
2. `email/sender.py` - Send via Gmail SMTP

**Configuration & Storage**:
- `.env` - Environment variables and API keys
- `utils/config.py` - Validates and loads configuration
- `.temp/github_history.json` - Tracks shown GitHub repos (auto-created)

## Customization

### Adding Custom RSS Feeds

Edit `/Users/adityagoswami/Documents/MacBook/Personal_Projetcs/3_Experimental/daily_ai_briefing/config/feeds.py`:

```python
RSS_FEEDS = {
    "Your Blog Name": "https://yourblog.com/feed.xml",
    "Another Source": "https://example.com/rss",
}
```

**Note**: Many major tech sites (TechCrunch, The Verge, etc.) are protected by Cloudflare and will return 0 articles.

### Customizing Reddit Subreddits

Edit `/Users/adityagoswami/Documents/MacBook/Personal_Projetcs/3_Experimental/daily_ai_briefing/src/utils/config.py`:

```python
subreddits: List[str] = field(default_factory=lambda: [
    "MachineLearning",
    "artificial",
    "LocalLLaMA",
    # Add your custom subreddits here
])
```

### Modifying Email Template

Edit `/Users/adityagoswami/Documents/MacBook/Personal_Projetcs/3_Experimental/daily_ai_briefing/templates/email.html` to customize:
- Colors and styling (currently uses amber/orange theme)
- Layout and sections
- Header and footer content

The template uses Jinja2 syntax and receives:
- `date`: Formatted date string
- `article_count`: Number of articles
- `source_count`: Number of sources
- `summary`: AI-generated summary (optional)
- `sections`: Grouped articles by source

### Adjusting Topic Matching

Modify `/Users/adityagoswami/Documents/MacBook/Personal_Projetcs/3_Experimental/daily_ai_briefing/src/processors/topic_filter.py` to customize:
- Matching algorithm (currently uses word boundaries + phrase matching)
- Fallback behavior (currently returns top 5 if no matches)
- Logging verbosity

## Troubleshooting

### No Articles Collected

**Problem**: "Collected 0 articles from all sources"

**Solutions**:
1. **RSS Feeds Blocked**: Most major sites block automated access. Set `INCLUDE_RSS=false`
2. **Check Network**: Ensure you have internet connectivity
3. **Increase MAX_AGE_HOURS**: Try `MAX_AGE_HOURS=72` for 3-day lookback
4. **Enable More Sources**: Set `INCLUDE_HACKERNEWS=true`, `INCLUDE_ARXIV=true`

### Gmail Authentication Failed

**Problem**: "Failed to send email" or authentication errors

**Solutions**:
1. **Verify App Password**: Must be 16 characters from Google App Passwords (not your regular password)
2. **Enable 2FA**: Gmail App Passwords require 2-Factor Authentication
3. **Check GMAIL_USER**: Must be complete email address (e.g., `user@gmail.com`)
4. **Firewall/Network**: Ensure port 587 is not blocked

### OpenAI API Errors

**Problem**: "Failed to generate summary"

**Solutions**:
1. **Check API Key**: Verify key is correct and active at [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Account Credits**: Ensure you have available API credits
3. **Disable Summaries**: Set `ENABLE_AI_SUMMARY=false` to skip AI summaries
4. **Rate Limits**: If hitting limits, wait a few minutes and retry

### Topic Filtering Returns No Results

**Problem**: "No articles matched any topics! Returning top 5 articles"

**Solutions**:
1. **Broaden Topics**: Add more general terms to `FILTER_TOPICS`
2. **Check Spelling**: Ensure topic names match actual article content
3. **Disable Filtering**: Set `ENABLE_TOPIC_FILTERING=false` to see all articles
4. **Review Logs**: Check which topics are matching in console output

### Reddit API Issues

**Problem**: Reddit collector fails or returns errors

**Solutions**:
1. **Verify Credentials**: Check `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`
2. **App Type**: Must be "script" type in Reddit app settings
3. **Disable Reddit**: Set `INCLUDE_REDDIT=false` if not needed
4. **Rate Limits**: Reddit has strict rate limits; wait before retrying

### GitHub Actions Not Running

**Problem**: Workflow doesn't trigger at scheduled time

**Solutions**:
1. **Check Repository Activity**: GitHub may disable workflows on inactive repos
2. **Verify Secrets**: All required secrets must be added to repository settings
3. **Workflow Enabled**: Ensure workflow is enabled in Actions tab
4. **Cron Syntax**: Verify cron expression in workflow file
5. **Manual Trigger**: Use "Run workflow" button to test

### Empty Emails

**Problem**: Email arrives but has no articles

**Solutions**:
1. **Increase MAX_AGE_HOURS**: Try `72` or higher for more coverage
2. **Check Topic Filters**: May be filtering out all articles
3. **Enable More Sources**: Turn on additional collectors
4. **Review Logs**: Check console output for filtering statistics

## Recent Updates

### February 12, 2026 - Topic Filtering & GitHub Trending

**New Features**:
- **Topic-Based Filtering**: Strict filtering to show only articles about configured topics
  - Supports exact word matching ("OpenAI") and phrase matching ("MCP Framework")
  - Filters across title, URL, and summary
  - Prevents empty emails by returning top 5 articles if no matches found

- **GitHub Trending Collector**: Fetches popular AI repositories
  - Scrapes GitHub trending page for top repositories
  - Filters for AI-related repos automatically
  - 30-day deduplication to prevent showing same repo repeatedly

- **30-Day Repo History**: JSON-based tracking in `.temp/github_history.json`
  - Automatically cleans up old entries
  - Designed for future database migration

**Configuration Changes**:
```bash
ENABLE_TOPIC_FILTERING=true
FILTER_TOPICS=OpenAI,Claude,Google Gemini,NotebookLM
INCLUDE_GITHUB_TRENDING=true
GITHUB_HISTORY_DAYS=30
```

**Note on RSS Feeds**: Most major tech company RSS feeds are protected by Cloudflare and return 0 articles. Recommended configuration uses Hacker News, ArXiv, and GitHub Trending as primary sources.

### January 26, 2026 - Migration from Anthropic to OpenAI

**Breaking Changes**:
- Replaced Anthropic Claude API with OpenAI GPT-4o-mini
- Changed environment variable: `ANTHROPIC_API_KEY` → `OPENAI_API_KEY`
- Updated dependency: `anthropic>=0.40.0` → `openai>=1.58.1`

**Migration Steps for Existing Users**:
1. Update dependencies: `pip install -r requirements.txt`
2. Get OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
3. Replace `ANTHROPIC_API_KEY` with `OPENAI_API_KEY` in `.env`
4. Update GitHub Actions secrets if deployed

**Why the Change**: Cost optimization and broader API compatibility

### Earlier Updates

- **Reddit Made Optional**: Can disable Reddit integration with `INCLUDE_REDDIT=false`
- **Configurable Sources**: All collectors can be individually enabled/disabled
- **Enhanced Logging**: Better visibility into collection and filtering process

## Contributing

Contributions are welcome! If you'd like to improve the Daily AI Briefing:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Areas for Contribution**:
- Additional news sources (APIs that aren't Cloudflare-protected)
- Improved topic matching algorithms
- Alternative email delivery methods
- Database storage for article history
- Web dashboard for configuration
- Support for other AI models (Claude, Gemini, etc.)

## License

This project is provided as-is for personal use. Feel free to modify and adapt for your needs.

## Credits

Created by Aditya Goswami

**Technologies Used**:
- Python 3.11+
- OpenAI GPT-4o-mini for summaries
- Gmail SMTP for email delivery
- GitHub Actions for automation
- BeautifulSoup for web scraping
- Jinja2 for templating

---

**Questions or Issues?** Open an issue on GitHub or reach out to the maintainer.

**Enjoy your daily AI briefing!**
