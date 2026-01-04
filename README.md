# AI & Tech News Scraper 🤖📰

A Python web scraper that sends daily AI and tech news updates directly to your WhatsApp.

## Features

- 📡 Scrapes news from multiple trusted sources (TechCrunch, MIT Tech Review, The Verge, etc.)
- 📝 Extracts article summaries automatically from RSS feeds
- 📱 Sends formatted updates via WhatsApp using Twilio API
- 🔗 Includes title, summary, source, and URL for each article
- 💾 Archives all articles to a local text file
- 🔄 RSS feed parsing for reliable content extraction
- ⚙️ Configurable news sources and article limits
- 📅 Daily automated updates (with scheduler or cron)

## 🚀 Quick Start with GitHub Actions (Recommended)

For automated daily updates running in the cloud (no laptop needed):

👉 **See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for complete setup guide**

## Local Setup Instructions

### 1. Install Dependencies

```bash
cd news-scrapper
pip install -r requirements.txt
```

### 2. Set Up Twilio WhatsApp

1. Sign up for a free Twilio account: https://www.twilio.com/try-twilio
2. Go to the [Twilio Console](https://console.twilio.com/)
3. Navigate to **Messaging > Try it out > Send a WhatsApp message**
4. Follow the instructions to join the Twilio Sandbox for WhatsApp
   - Send "join <your-sandbox-code>" to the Twilio WhatsApp number from your phone
5. Get your credentials:
   - **Account SID** (found on Console dashboard)
   - **Auth Token** (found on Console dashboard)
   - **Twilio WhatsApp Number** (e.g., `whatsapp:+14155238886`)
   - **Your WhatsApp Number** (e.g., `whatsapp:+1234567890`)

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
TWILIO_ACCOUNT_SID=your_actual_account_sid
TWILIO_AUTH_TOKEN=your_actual_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
RECIPIENT_WHATSAPP_NUMBER=whatsapp:+1234567890
```

### 4. Run the Script (Local Testing)

**Test locally before deploying to GitHub:**
```bash
python main.py
```

## Customization

### Add More News Sources

Edit `main.py` and add RSS feed URLs to `self.news_sources`:

```python
self.news_sources = {
    'Your Source': 'https://example.com/feed/',
    # Add more sources here
}
```

### Adjust Article Count

Modify the `max_per_source` parameter in the `run()` method:

```python
self.scrape_all_sources(max_per_source=5)  # Get 5 articles per source
```

## Troubleshooting

- **WhatsApp not receiving messages**: Ensure you've joined the Twilio Sandbox by sending the join code
- **API errors**: Verify your Twilio credentials in `.env`
- **No articles scraped**: Check your internet connection and RSS feed URLs

## Credits

Built with ❤️ by **Khelan**

## License

MIT License - Feel free to use and modify!
