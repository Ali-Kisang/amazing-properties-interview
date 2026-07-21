
"""
Central configuration manager for the scraper
"""
import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()

class Config:
    """Main configuration class"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    LOGS_DIR = BASE_DIR / 'logs'
    
    # Craigslist settings
    CITIES = ['milwaukee', 'columbus']
    MIN_PRICE = 50000
    MAX_PRICE = 250000
    MAX_PAGES_PER_CITY = 10
    TARGET_LISTINGS = 50
    
    # Search queries
    SEARCH_QUERIES = [
        'single family home',
        'duplex',
        'multi-family',
        'investment',
        'rental'
    ]
    
    # Scraping settings
    DOWNLOAD_DELAY = 2.5
    CONCURRENT_REQUESTS = 2
    RETRY_TIMES = 3
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    # Facebook settings
    FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
    FACEBOOK_USER_ID = os.getenv('FACEBOOK_USER_ID')
    FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
    FACEBOOK_SEARCH_QUERY = 'real estate investment Milwaukee'
    FACEBOOK_MAX_POSTS = 10
    FACEBOOK_MIN_DELAY = 60 
    FACEBOOK_MAX_DELAY = 180
    
    
    EXPORT_FORMATS = ['json', 'csv']
    JSON_INDENT = 2
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}'
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.FACEBOOK_ACCESS_TOKEN:
            print("  Warning: FACEBOOK_ACCESS_TOKEN not set")
            return False
        return True
    
    @classmethod
    def get_city_urls(cls):
        """Generate search URLs for each city"""
        urls = []
        base_url = 'https://{city}.craigslist.org/search/rea'
        for city in cls.CITIES:
            url = base_url.format(city=city)
            params = {
                'query': '|'.join(cls.SEARCH_QUERIES),
                'min_price': cls.MIN_PRICE,
                'max_price': cls.MAX_PRICE
            }
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            urls.append(f"{url}?{query_string}")
        return urls