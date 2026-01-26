# Daily AI Briefing

Automated system to aggregate AI news from multiple sources and deliver a curated email digest daily at 8:00 AM EST.

## Project Structure

```
daily_ai_briefing/
├── .github/workflows/daily_briefing.yml  # GitHub Actions scheduler
├── src/
│   ├── main.py                           # Entry point
│   ├── models.py                         # Article dataclass
│   ├── collectors/                       # Data source collectors
│   ├── processors/                       # Content processing
│   ├── email/                            # Email formatting/sending
│   └── utils/                            # Config & logging
├── templates/                            # Jinja2 email templates
├── config/                               # RSS feed configuration
└── requirements.txt
```

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the briefing
python -m src.main
```

## Required API Keys

1. **Gmail App Password**: Google Account > Security > App passwords
2. **OpenAI API**: https://platform.openai.com/api-keys

## Optional API Keys

1. **Reddit API**: https://www.reddit.com/prefs/apps (create "script" app)
   - Can be disabled by setting `INCLUDE_REDDIT=false` in `.env`

## GitHub Actions Deployment

1. Push repo to GitHub
2. Add secrets in Settings > Secrets and variables > Actions:
   - `GMAIL_USER`
   - `GMAIL_APP_PASSWORD`
   - `RECIPIENT_EMAIL`
   - `OPENAI_API_KEY`
   - `REDDIT_CLIENT_ID` (optional, only if `INCLUDE_REDDIT=true`)
   - `REDDIT_CLIENT_SECRET` (optional, only if `INCLUDE_REDDIT=true`)
3. Workflow runs daily at 8:00 AM EST (13:00 UTC)

## Key Commands

- `python -m src.main` - Run the briefing manually
- Trigger GitHub Action manually via "Run workflow" button

## Recent Changes

### Migration from Anthropic to OpenAI (2026-01-26)

The project was updated to use OpenAI instead of Anthropic for AI-powered summaries:

**Changed files:**
- `requirements.txt`: Replaced `anthropic>=0.40.0` with `openai>=1.58.1`
- `.env.example` and `.env`: Changed `ANTHROPIC_API_KEY` to `OPENAI_API_KEY`
- `src/utils/config.py`: Updated config to use `openai_api_key` field
- `src/processors/summarizer.py`: Replaced Anthropic client with OpenAI client, using `gpt-4o-mini` model
- `src/main.py`: Updated to pass `openai_api_key` to summarizer

**Migration steps for existing installations:**
1. Update dependencies: `pip install -r requirements.txt`
2. Replace `ANTHROPIC_API_KEY` with `OPENAI_API_KEY` in your `.env` file
3. Get OpenAI API key from https://platform.openai.com/api-keys

### Reddit Made Optional

Reddit integration is now optional and can be disabled:
- Set `INCLUDE_REDDIT=false` in `.env` to disable Reddit collection
- When disabled, no Reddit API credentials are required
- The system will still collect from RSS feeds, Hacker News, and arXiv
