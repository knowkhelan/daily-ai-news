# GitHub Actions Setup Guide

This guide will help you deploy your news scraper to GitHub Actions so it runs automatically in the cloud every day.

## 📋 Prerequisites

- GitHub account
- Twilio credentials (Account SID, Auth Token, WhatsApp numbers)

## 🚀 Step-by-Step Setup

### Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ai-tech-news-scraper` (or your choice)
3. Choose **Public** or **Private**
4. **DO NOT** initialize with README (we already have one)
5. Click **Create repository**

### Step 2: Add Twilio Secrets to GitHub

Your Twilio credentials need to be stored securely in GitHub Secrets:

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add each of these:

| Secret Name | Value |
|-------------|-------|
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID (starts with AC...) |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token |
| `TWILIO_WHATSAPP_NUMBER` | `whatsapp:+14155238886` (Twilio sandbox number) |
| `RECIPIENT_WHATSAPP_NUMBER` | `whatsapp:+1234567890` (your WhatsApp number) |

**Important:** Never commit your `.env` file or expose these secrets!

### Step 3: Push Code to GitHub

Run these commands in your terminal:

```bash
# Navigate to the news-scrapper directory
cd /Users/khelan/Documents/coding/pm-triage-agent/news-scrapper

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: AI & Tech News Scraper

🤖 Features:
- Scrapes AI/tech news from 5 sources
- Extracts article summaries
- Sends daily WhatsApp updates via Twilio
- Automated with GitHub Actions

Built with ❤️ by Khelan"

# Add your GitHub repository as remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/ai-tech-news-scraper.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Verify GitHub Actions

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. You should see the workflow: "Daily AI & Tech News Scraper"
4. The workflow will run:
   - **Automatically** every day at 8:00 AM UTC
   - **Manually** by clicking "Run workflow" button

### Step 5: Test It Now

Don't wait for the scheduled time - test it immediately:

1. Go to **Actions** tab
2. Click on "Daily AI & Tech News Scraper" workflow
3. Click **Run workflow** → **Run workflow**
4. Watch the workflow run in real-time
5. Check your WhatsApp for the news update!

## ⏰ Customizing the Schedule

Edit [`.github/workflows/daily-scraper.yml`](../.github/workflows/daily-scraper.yml) and change the cron schedule:

```yaml
on:
  schedule:
    # Current: 8:00 AM UTC
    - cron: '0 8 * * *'
```

**Common Schedules:**

| Time | Cron Expression | Description |
|------|----------------|-------------|
| 8 AM UTC | `0 8 * * *` | Current setting |
| 8 AM EST (1 PM UTC) | `0 13 * * *` | US East Coast |
| 8 AM PST (4 PM UTC) | `0 16 * * *` | US West Coast |
| 9 AM IST (3:30 AM UTC) | `30 3 * * *` | India |
| Twice daily | `0 8,20 * * *` | 8 AM and 8 PM UTC |

**Cron format:** `minute hour day month day-of-week`

## 📊 Monitoring

### View Workflow Runs
1. Go to **Actions** tab
2. Click on any workflow run to see logs
3. Check each step for success/failure

### View Logs
- GitHub stores logs for each run
- Logs are available for 90 days (free tier)
- Download logs from the Actions tab

### Troubleshooting

**Workflow not running?**
- Check that secrets are set correctly (case-sensitive names)
- Verify the cron schedule syntax
- GitHub Actions can have ~10 minute delays

**WhatsApp not receiving messages?**
- Verify you've joined the Twilio Sandbox
- Check secrets are configured properly
- Look at workflow logs for error messages

**Scraper failing?**
- Check the workflow run logs in Actions tab
- Verify RSS feed URLs are still active
- Check if any dependencies need updating

## 💡 Benefits of GitHub Actions

✅ **Free:** 2,000 minutes/month on free tier (more than enough)
✅ **Reliable:** Runs even if your computer is off
✅ **No Maintenance:** GitHub handles infrastructure
✅ **Logs:** Built-in logging and monitoring
✅ **Manual Triggers:** Run anytime with one click

## 🔒 Security Notes

- ✅ Secrets are encrypted and never exposed in logs
- ✅ `.env` file is ignored by git (see `.gitignore`)
- ✅ Never commit credentials to the repository
- ⚠️  Free tier has public logs (but secrets are hidden)

## 📝 Next Steps

1. ⭐ Star your repository
2. 📧 Enable GitHub notifications for workflow failures
3. 🔧 Customize news sources in `main.py`
4. 📱 Share with friends!

---

**Built with Python by Khelan**
Need help? Check the [main README](README.md) or open an issue!
