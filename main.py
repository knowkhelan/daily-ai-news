"""
AI & Tech News Scraper with WhatsApp Integration
Author: Khelan
Description: Scrapes latest AI and tech news with summaries and sends daily updates via WhatsApp
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import feedparser
import os
from twilio.rest import Client
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

class NewsScraperBot:
    def __init__(self):
        """Initialize the news scraper with API credentials"""
        # Twilio credentials for WhatsApp
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')  # Format: whatsapp:+14155238886
        self.recipient_whatsapp_number = os.getenv('RECIPIENT_WHATSAPP_NUMBER')  # Format: whatsapp:+1234567890

        # Initialize Twilio client
        if self.twilio_account_sid and self.twilio_auth_token:
            self.client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.client = None
            print("⚠️  Warning: Twilio credentials not found. WhatsApp messaging disabled.")

        # News sources (RSS feeds)
        self.news_sources = {
            'TechCrunch AI': 'https://techcrunch.com/category/artificial-intelligence/feed/',
            'MIT Tech Review': 'https://www.technologyreview.com/feed/',
            'The Verge AI': 'https://www.theverge.com/rss/ai-artificial-intelligence/index.xml',
            'VentureBeat AI': 'https://venturebeat.com/category/ai/feed/',
            'Wired AI': 'https://www.wired.com/feed/category/science/artificial-intelligence/latest/rss',}

        self.articles = []

    def clean_summary(self, text):
        """Clean and truncate summary text"""
        if not text:
            return "No summary available."

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Truncate to ~200 characters
        if len(text) > 200:
            text = text[:197] + "..."

        return text

    def scrape_rss_feed(self, feed_url, source_name, max_articles=5):
        """Scrape articles with summaries from RSS feed"""
        try:
            print(f"  📡 Fetching from {source_name}...")
            feed = feedparser.parse(feed_url)
            articles = []

            for entry in feed.entries[:max_articles]:
                # Extract summary from various possible fields
                summary = ""
                if hasattr(entry, 'summary'):
                    summary = entry.summary
                elif hasattr(entry, 'description'):
                    summary = entry.description
                elif hasattr(entry, 'content'):
                    summary = entry.content[0].value if entry.content else ""

                article = {
                    'title': entry.title,
                    'link': entry.link,
                    'summary': self.clean_summary(summary),
                    'source': source_name,
                    'published': entry.get('published', 'N/A')
                }
                articles.append(article)
                print(f"    ✓ {entry.title[:60]}...")

            return articles
        except Exception as e:
            print(f"  ❌ Error scraping {source_name}: {str(e)}")
            return []

    def scrape_all_sources(self, max_per_source=5):
        """Scrape all configured news sources"""
        print(f"\n🔍 Starting news scrape from {len(self.news_sources)} sources...")
        print("━" * 60)

        for source_name, feed_url in self.news_sources.items():
            articles = self.scrape_rss_feed(feed_url, source_name, max_per_source)
            self.articles.extend(articles)
            time.sleep(1)  # Be respectful to servers

        print("━" * 60)
        print(f"✅ Successfully scraped {len(self.articles)} articles total\n")
        return self.articles

    def format_message(self):
        """Format articles into a WhatsApp-friendly message with summaries"""
        if not self.articles:
            return "No news articles found today."

        today = datetime.now().strftime("%B %d, %Y")
        messages = []
        current_message = f"🤖 *AI & Tech News Daily Update*\n📅 {today}\n"
        current_message += f"📊 {len(self.articles)} articles from {len(self.news_sources)} sources\n"
        current_message += "━" * 30 + "\n\n"

        article_count = 0

        for article in self.articles:
            article_count += 1

            article_text = f"*{article_count}. {article['title']}*\n"
            article_text += f"📰 Source: {article['source']}\n"
            article_text += f"📝 {article['summary']}\n"
            article_text += f"🔗 {article['link']}\n\n"

            # Check if adding this article would exceed WhatsApp's limit (~1600 chars)
            if len(current_message) + len(article_text) > 1500:
                # Finalize current message and start a new one
                messages.append(current_message)
                current_message = f"🤖 *AI & Tech News (continued...)*\n\n"

            current_message += article_text

        # Add footer to last message
        current_message += "━" * 30 + "\n"
        current_message += "💡 _Built with Python by Khelan_\n"
        current_message += "⏰ Next update in 24 hours"

        messages.append(current_message)

        return messages

    def send_whatsapp_messages(self, messages):
        """Send one or multiple messages via WhatsApp using Twilio"""
        if not self.client:
            print("❌ Twilio client not initialized. Cannot send WhatsApp message.")
            print("\n" + "=" * 60)
            print("📱 MESSAGE PREVIEW (would be sent via WhatsApp):")
            print("=" * 60)
            for i, msg in enumerate(messages, 1):
                if len(messages) > 1:
                    print(f"\n--- Part {i}/{len(messages)} ---\n")
                print(msg)
            print("=" * 60)
            return False

        try:
            print(f"📤 Sending {len(messages)} message(s) via WhatsApp...\n")

            for i, message in enumerate(messages, 1):
                msg = self.client.messages.create(
                    from_=self.twilio_whatsapp_number,
                    body=message if len(messages) == 1 else f"(Part {i}/{len(messages)})\n\n{message}",
                    to=self.recipient_whatsapp_number
                )
                print(f"  ✅ Message {i}/{len(messages)} sent - SID: {msg.sid}")

                # Small delay between messages
                if i < len(messages):
                    time.sleep(2)

            print(f"\n🎉 All messages sent successfully to {self.recipient_whatsapp_number}")
            return True

        except Exception as e:
            print(f"❌ Error sending WhatsApp message: {str(e)}")
            print("💡 Make sure you've joined the Twilio WhatsApp Sandbox")
            return False

    def save_to_file(self, filename="news_archive.txt"):
        """Save scraped articles to a text file for archival"""
        try:
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"News Update - {today}\n")
                f.write(f"{'='*80}\n\n")

                for i, article in enumerate(self.articles, 1):
                    f.write(f"{i}. {article['title']}\n")
                    f.write(f"   Source: {article['source']}\n")
                    f.write(f"   Summary: {article['summary']}\n")
                    f.write(f"   URL: {article['link']}\n")
                    f.write(f"   Published: {article['published']}\n\n")

            print(f"💾 Articles archived to {filename}")
            return True
        except Exception as e:
            print(f"⚠️  Could not save to file: {str(e)}")
            return False

    def run(self):
        """Main execution function"""
        print("\n" + "=" * 60)
        print("🚀 AI & TECH NEWS SCRAPER BOT")
        print("=" * 60)
        print(f"⏰ Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Scrape news from all sources
        self.scrape_all_sources(max_per_source=5)

        if not self.articles:
            print("❌ No articles found. Exiting.")
            return

        # Format messages
        messages = self.format_message()

        # Save to archive file
        self.save_to_file()

        # Send via WhatsApp
        self.send_whatsapp_messages(messages)

        print("\n" + "=" * 60)
        print("✨ SCRAPER RUN COMPLETE")
        print("=" * 60)


def main():
    """Entry point for daily news scraper"""
    bot = NewsScraperBot()
    bot.run()


if __name__ == "__main__":
    main()
