"""
Crawl scheduler - manages the scraping workflow
"""
import time
from datetime import datetime
from loguru import logger

class CrawlScheduler:
    """Schedule and manage scraping tasks"""
    
    def __init__(self):
        self.start_time = datetime.now()  # Initialize immediately
        self.end_time = None
        self.stats = {
            'total_urls_found': 0,
            'total_properties_scraped': 0,
            'duplicates_filtered': 0,
            'errors': 0,
            'cities_processed': []
        }
    
    def start(self):
        """Start the crawling process"""
        logger.info("🚀 Starting crawl scheduler...")
        self.start_time = datetime.now()
    
    def log_progress(self, city: str, page: int, items_found: int):
        """Log progress of the crawl"""
        logger.info(f"📍 {city.title()} - Page {page}: Found {items_found} listings")
        self.stats['cities_processed'].append(city)
    
    def log_item_scraped(self, item):
        """Log when an item is successfully scraped"""
        self.stats['total_properties_scraped'] += 1
        if self.stats['total_properties_scraped'] % 10 == 0:
            logger.info(f"📊 Progress: {self.stats['total_properties_scraped']} listings scraped")
    
    def log_duplicate(self, url: str):
        """Log duplicate detection"""
        self.stats['duplicates_filtered'] += 1
    
    def log_error(self, error: str, url: str = None):
        """Log errors"""
        self.stats['errors'] += 1
        logger.error(f"❌ Error: {error}")
    
    def finish(self):
        """Finish the crawl and generate summary"""
        self.end_time = datetime.now()
        if self.start_time:
            duration = (self.end_time - self.start_time).total_seconds()
        else:
            duration = 0
        
        logger.info("=" * 60)
        logger.info("📊 CRAWL SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Total properties scraped: {self.stats['total_properties_scraped']}")
        logger.info(f"♻️ Duplicates filtered: {self.stats['duplicates_filtered']}")
        logger.info(f"❌ Errors encountered: {self.stats['errors']}")
        logger.info(f"⏱️ Duration: {duration:.2f} seconds")
        logger.info("=" * 60)
        
        return self.stats
