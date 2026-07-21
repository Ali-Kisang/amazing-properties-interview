
"""
Entry point for running the Craigslist scraper
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapy.cmdline import execute
from config.settings import Config

def main():
    """Run the Craigslist spider"""
    
    # Build command
    cmd = [
        'scrapy',
        'crawl',
        'craigslist',
        '-a', f'cities={",".join(Config.CITIES)}',
        '-a', f'min_price={Config.MIN_PRICE}',
        '-a', f'max_price={Config.MAX_PRICE}',
        '-o', f'../data/listings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    ]
    
    # Run the spider
    sys.argv = cmd
    execute()

if __name__ == "__main__":
    from datetime import datetime
    main()