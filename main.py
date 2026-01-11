"""
AI & Tech News Scraper with WhatsApp Integration
Author: Khelan
Description: Scrapes latest AI and tech news with summaries and sends daily updates via WhatsApp
"""

from datetime import datetime, timedelta
import feedparser
import os
from twilio.rest import Client
from dotenv import load_dotenv
import time
import re
from email.utils import parsedate_to_datetime


load_dotenv()

class NewsScraperBot:
    def __init__(self):
        """Initialize the news scraper with API credentials"""
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

        # Funding & startup sources
        self.funding_sources = {
            'TechCrunch Funding': 'https://techcrunch.com/category/startups/feed/',
            'Crunchbase News': 'https://news.crunchbase.com/feed/',
        }

        self.articles = []
        self.funding_news = []

    def clean_summary(self, text):
        """Clean and truncate summary text"""
        if not text:
            return "No summary available."

        text = re.sub(r'<[^>]+>', '', text)

        text = ' '.join(text.split())

        if len(text) > 200:
            text = text[:197] + "..."

        return text

    def is_within_24_hours(self, published_date):
        """Check if article was published within the last 24 hours"""
        try:
            if isinstance(published_date, str):
                article_time = parsedate_to_datetime(published_date)
            else:
                return False

            now = datetime.now(article_time.tzinfo)
            twenty_four_hours_ago = now - timedelta(hours=24)

            return article_time >= twenty_four_hours_ago
        except Exception as e:
            return True

    def scrape_rss_feed(self, feed_url, source_name, max_articles=5):
        """Scrape articles with summaries from RSS feed, only from last 24 hours"""
        try:
            print(f"  📡 Fetching from {source_name}...")
            feed = feedparser.parse(feed_url)
            articles = []
            checked_count = 0

            # Check more entries to ensure we get enough recent articles
            for entry in feed.entries[:max_articles * 3]:
                checked_count += 1

                # Get published date
                published = entry.get('published', entry.get('updated', ''))

                # Check if article is from last 24 hours
                if published and not self.is_within_24_hours(published):
                    continue

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
                    'published': published
                }
                articles.append(article)
                print(f"    ✓ {entry.title[:60]}...")

                # Stop if we have enough recent articles
                if len(articles) >= max_articles:
                    break

            if articles:
                print(f"    📊 Found {len(articles)} articles from last 24 hours")
            else:
                print(f"   No articles from last 24 hours")
            return articles
        except Exception as e:
            print(f" Error scraping {source_name}: {str(e)}")
            return []

    def is_funding_related(self, title, summary):
        """Check if article is about funding/investment"""
        funding_keywords = [
            'raised', 'raises', 'funding', 'million', 'billion', 'investment',
            'series', 'seed round', 'venture capital', 'vc', 'invested',
            'investors', 'valuation', 'round', 'capital', 'fundraise',
            'pre-seed', 'angel', 'acquisition', 'acquired', 'ipo'
        ]
        text = (title + ' ' + summary).lower()
        return any(keyword in text for keyword in funding_keywords)

    def scrape_all_sources(self, max_per_source=5):
        """Scrape all configured news sources"""
        print(f"\n🔍 Starting news scrape from {len(self.news_sources)} sources...")
        print("━" * 60)

        for source_name, feed_url in self.news_sources.items():
            articles = self.scrape_rss_feed(feed_url, source_name, max_per_source)
            self.articles.extend(articles)
            time.sleep(1)  # Be respectful to servers

        print("━" * 60)
        print(f"Successfully scraped {len(self.articles)} articles total\n")
        return self.articles

    def scrape_funding_sources(self, max_per_source=10):
        """Scrape funding-related news"""
        print(f"\n💰 Starting funding news scrape from {len(self.funding_sources)} sources...")
        print("━" * 60)

        for source_name, feed_url in self.funding_sources.items():
            articles = self.scrape_rss_feed(feed_url, source_name, max_per_source)
            # Filter only funding-related articles
            funding_articles = [
                article for article in articles
                if self.is_funding_related(article['title'], article['summary'])
            ]
            self.funding_news.extend(funding_articles)
            print(f"    💵 {len(funding_articles)} funding articles found")
            time.sleep(1)

        print("━" * 60)
        print(f"✅ Successfully scraped {len(self.funding_news)} funding announcements\n")
        return self.funding_news

    def format_message(self):
        """Format articles into a WhatsApp-friendly message with summaries"""
        if not self.articles:
            return "No news articles found today."

        today = datetime.now().strftime("%B %d, %Y")
        messages = []
        current_message = f"🤖 *AI & Tech News Daily Update*\n📅 {today}\n"
        current_message += f"📊 {len(self.articles)} new articles (last 24 hours)\n"
        current_message += "━" * 30 + "\n\n"

        article_count = 0

        for article in self.articles:
            article_count += 1

            article_text = f"*{article_count}. {article['title']}*\n"
            article_text += f"📝 {article['summary']}\n\n"

            # Check if adding this article would exceed WhatsApp's limit (~1600 chars)
            if len(current_message) + len(article_text) > 1500:
                # Finalize current message and start a new one
                messages.append(current_message)
                current_message = f"🤖 *AI & Tech News (continued...)*\n\n"

            current_message += article_text

        messages.append(current_message)

        return messages

    def format_funding_message(self):
        """Format funding announcements into a WhatsApp-friendly message"""
        if not self.funding_news:
            return []

        today = datetime.now().strftime("%B %d, %Y")
        messages = []
        current_message = f"💰 *Startup Funding Roundup*\n📅 {today}\n"
        current_message += f"📊 {len(self.funding_news)} funding rounds (last 24 hours)\n"
        current_message += "━" * 30 + "\n\n"

        funding_count = 0

        for article in self.funding_news:
            funding_count += 1

            article_text = f"*{funding_count}. {article['title']}*\n"
            article_text += f"📝 {article['summary']}\n\n"

            # Check if adding this article would exceed WhatsApp's limit
            if len(current_message) + len(article_text) > 1500:
                messages.append(current_message)
                current_message = f"💰 *Startup Funding (continued...)*\n\n"

            current_message += article_text

        # Add footer to last message
        current_message += "━" * 30 + "\n"
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

        # Scrape tech news from all sources
        self.scrape_all_sources(max_per_source=5)

        # Scrape funding news
        self.scrape_funding_sources(max_per_source=10)

        # Check if we have any content
        if not self.articles and not self.funding_news:
            print("❌ No articles or funding news found in the last 24 hours.")
            no_news_msg = f"ℹ️ *Daily News Update*\n📅 {datetime.now().strftime('%B %d, %Y')}\n\n"
            no_news_msg += "No new AI/tech articles or funding announcements found in the last 24 hours.\n\n"
            no_news_msg += "✅ Scraper ran successfully at {}\n".format(datetime.now().strftime('%I:%M %p %Z'))
            no_news_msg += "🔄 Will check again tomorrow!"
            self.send_whatsapp_messages([no_news_msg])
            print("📤 Sent 'no news' notification to WhatsApp")
            return

        # Format and send tech news
        if self.articles:
            print("\n📤 Preparing tech news messages...")
            tech_messages = self.format_message()
            self.send_whatsapp_messages(tech_messages)
        else:
            print("⚠️  No tech news from last 24 hours")

        # Format and send funding news separately
        if self.funding_news:
            print("\n📤 Preparing funding news messages...")
            funding_messages = self.format_funding_message()
            time.sleep(3)  # Brief delay between news types
            self.send_whatsapp_messages(funding_messages)
        else:
            print("⚠️  No funding news from last 24 hours")

        # Save to archive file
        self.save_to_file()

        print("\n" + "=" * 60)
        print("✨ SCRAPER RUN COMPLETE")
        print("=" * 60)


def main():
    """Entry point for daily news scraper"""
    bot = NewsScraperBot()
    bot.run()


if __name__ == "__main__":
    main()
