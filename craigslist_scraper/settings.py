"""
Scrapy settings for craigslist_scraper project
"""
import os

BOT_NAME = "craigslist_scraper"

SPIDER_MODULES = ["spiders"]
NEWSPIDER_MODULE = "spiders"

# Obey robots.txt
ROBOTSTXT_OBEY = True

# Configure concurrent requests
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Download delay
DOWNLOAD_DELAY = 2.5
RANDOMIZE_DOWNLOAD_DELAY = True

# Cookies
COOKIES_ENABLED = True

# Default user agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Enable logging
LOG_LEVEL = "INFO"

# Retry settings
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Item pipelines - Data Pipeline
ITEM_PIPELINES = {
    "pipelines.DataValidator": 100,
    "pipelines.CleaningPipeline": 200,
    "pipelines.LocationFilter": 250,
    "pipelines.DuplicateFilter": 300,
    "pipelines.ExportPipeline": 400,
}

# Database pipelines - Enable based on environment variables
ENABLE_POSTGRESQL = os.getenv('ENABLE_POSTGRESQL', 'false').lower() == 'true'
ENABLE_MYSQL = os.getenv('ENABLE_MYSQL', 'false').lower() == 'true'
ENABLE_MONGODB = os.getenv('ENABLE_MONGODB', 'false').lower() == 'true'

if ENABLE_POSTGRESQL:
    ITEM_PIPELINES["pipelines_database.PostgreSQLPipeline"] = 500
    print("✅ PostgreSQL storage enabled")

if ENABLE_MYSQL:
    ITEM_PIPELINES["pipelines_database.MySQLPipeline"] = 510
    print("✅ MySQL storage enabled")

if ENABLE_MONGODB:
    ITEM_PIPELINES["pipelines_database.MongoDBPipeline"] = 520
    print("✅ MongoDB storage enabled")
