"""
Daily Scheduler for News Scraper
This script runs the news scraper once per day at a specified time
"""

import schedule
import time
from datetime import datetime
from main import NewsScraperBot

def run_scraper():
    """Run the news scraper"""
    print(f"\n{'='*60}")
    print(f"🕐 Scheduled run triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    bot = NewsScraperBot()
    bot.run()

# Configure the schedule
# Run daily at 8:00 AM
schedule.every().day.at("08:00").do(run_scraper)

# Alternative schedules (uncomment the one you want):
# schedule.every().day.at("09:00").do(run_scraper)  # 9 AM
# schedule.every().day.at("18:00").do(run_scraper)  # 6 PM
# schedule.every(12).hours.do(run_scraper)  # Every 12 hours
# schedule.every().monday.at("08:00").do(run_scraper)  # Only Mondays

print("🤖 News Scraper Scheduler Started")
print(f"⏰ Next run scheduled for: {schedule.next_run()}")
print("Press Ctrl+C to stop\n")

# Run immediately on startup (optional - comment out if you don't want this)
print("🚀 Running initial scrape...")
run_scraper()

# Keep the scheduler running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
