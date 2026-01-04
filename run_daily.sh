#!/bin/bash
# Daily runner script for news scraper
# This can be used with cron for scheduled execution

cd "$(dirname "$0")"

# Activate virtual environment if you're using one
# source venv/bin/activate

# Run the scraper
python3 main.py

# Log the execution
echo "News scraper run completed at $(date)" >> scraper.log
