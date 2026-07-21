"""
Item definitions for property listings
"""
import scrapy
from scrapy.loader import ItemLoader
import re


def clean_price(value):
    """Clean price field"""
    if not value:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    cleaned = re.sub(r'[$,]', '', str(value))
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def clean_text(value):
    """Clean text fields"""
    if value:
        return str(value).strip()
    return None


def extract_bedrooms(value):
    """Extract bedroom count"""
    if not value:
        return None
    match = re.search(r'(\d+)\s*(?:br|bed|bedroom)', str(value).lower())
    if match:
        return int(match.group(1))
    return None


def extract_bathrooms(value):
    """Extract bathroom count"""
    if not value:
        return None
    match = re.search(r'(\d+\.?\d*)\s*(?:ba|bath|bathroom)', str(value).lower())
    if match:
        return float(match.group(1))
    return None


class PropertyItem(scrapy.Item):
    """Property listing item"""
    
    # Required fields
    title = scrapy.Field()
    price = scrapy.Field()
    address = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    square_feet = scrapy.Field()
    listing_url = scrapy.Field()
    description = scrapy.Field()
    posted_date = scrapy.Field()
    
    # Metadata
    city = scrapy.Field()
    listing_id = scrapy.Field()
    unique_id = scrapy.Field()
    scraped_at = scrapy.Field()
