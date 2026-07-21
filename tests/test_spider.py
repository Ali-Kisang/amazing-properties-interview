
"""
Unit tests for spider
"""
import pytest
from craigslist_scraper.spiders.craigslist_spider import CraigslistSpider
from craigslist_scraper.items import PropertyItem


class TestCraigslistSpider:
    """Test spider parsing logic"""
    
    def setup_method(self):
        self.spider = CraigslistSpider()
    
    def test_spider_name(self):
        """Test spider name"""
        assert self.spider.name == 'craigslist'
    
    def test_cities_loaded(self):
        """Test cities are loaded from config"""
        assert 'milwaukee' in self.spider.cities
        assert 'columbus' in self.spider.cities
    
    def test_price_range(self):
        """Test price range is set correctly"""
        assert self.spider.min_price == 50000
        assert self.spider.max_price == 250000
    
    def test_start_requests(self):
        """Test start requests are generated"""
        requests = list(self.spider.start_requests())
        assert len(requests) >= 2  # At least Milwaukee and Columbus
        
        # Check first request URL
        first_req = requests[0]
        assert 'milwaukee' in first_req.url or 'columbus' in first_req.url
        assert 'search/rea' in first_req.url
        assert 'min_price=50000' in first_req.url
        assert 'max_price=250000' in first_req.url


class TestPropertyItem:
    """Test PropertyItem functionality"""
    
    def test_item_fields(self):
        """Test all fields are present"""
        item = PropertyItem()
        
        # Set all fields
        item['title'] = 'Test'
        item['price'] = 250000
        item['address'] = '123 Main St'
        item['bedrooms'] = 3
        item['bathrooms'] = 2
        item['square_feet'] = 1800
        item['listing_url'] = 'https://test.com'
        item['description'] = 'Test description'
        item['posted_date'] = '2026-07-17'
        item['city'] = 'milwaukee'
        item['listing_id'] = '12345'
        
        # Verify all fields
        assert item['title'] == 'Test'
        assert item['price'] == 250000
        assert item['address'] == '123 Main St'
        assert item['bedrooms'] == 3
        assert item['bathrooms'] == 2
        assert item['square_feet'] == 1800
        assert item['listing_url'] == 'https://test.com'
        assert item['description'] == 'Test description'
        assert item['posted_date'] == '2026-07-17'
        assert item['city'] == 'milwaukee'
        assert item['listing_id'] == '12345'