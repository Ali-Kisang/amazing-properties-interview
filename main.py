
"""
Main entry point for the assessment
"""
import sys
import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO"
)

def run_scraper():
    """Run the Craigslist scraper"""
    logger.info(" Starting Craigslist scraper...")
    
    from scrapy.cmdline import execute
    
    # Change to the craigslist_scraper directory
    project_root = Path(__file__).parent
    scraper_dir = project_root / "craigslist_scraper"
    
    if not scraper_dir.exists():
        logger.error(f" Scraper directory not found: {scraper_dir}")
        return
    
    # Change to scraper directory
    os.chdir(scraper_dir)
    logger.info(f" Changed to directory: {os.getcwd()}")
    
    # Build command
    sys.argv = [
        'scrapy',
        'crawl',
        'cl',
        '-a', 'cities=milwaukee,columbus',
        '-a', 'min_price=50000',
        '-a', 'max_price=250000',
        '-o', '../data/listings.json'
    ]
    
    try:
        execute()
        logger.info(" Scraper completed successfully!")
    except Exception as e:
        logger.error(f" Scraper failed: {e}")
        raise

def run_facebook():
    """Run Facebook automation"""
    logger.info(" Starting Facebook automation...")
    
    try:
        from fb_automation.facebook_api import run
        run()
        logger.info(" Facebook automation completed!")
    except Exception as e:
        logger.error(f" Facebook automation failed: {e}")
        raise

def main():
    """Main entry point"""
    print("=" * 60)
    print(" AMAZING PROPERTIES - ASSESSMENT")
    print("=" * 60)
    print("1. Run Craigslist Scraper")
    print("2. Run Facebook Automation")
    print("3. Run All")
    print("4. Exit")
    print("=" * 60)
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == '1':
        run_scraper()
    elif choice == '2':
        run_facebook()
    elif choice == '3':
        run_scraper()
        run_facebook()
    else:
        print(" Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
