
"""
Unit tests for data pipelines
"""
import pytest
from scrapy.exceptions import DropItem
from craigslist_scraper.pipelines import (
    CleanDataPipeline, 
    ValidationPipeline, 
    DuplicateFilterPipeline,
    JsonExportPipeline
)
from craigslist_scraper.items import PropertyItem


class TestCleanDataPipeline:
    """Test data cleaning functionality"""
    
    def setup_method(self):
        self.pipeline = CleanDataPipeline()
    
    def test_clean_price(self):
        """Test price cleaning"""
        item = PropertyItem()
        item['price'] = '$250,000'
        item['title'] = 'Test Listing'
        item['listing_url'] = 'https://test.com'
        
        processed = self.pipeline.process_item(item, None)
        assert processed['price'] == 250000
    
    def test_clean_title(self):
        """Test title cleaning"""
        item = PropertyItem()
        item['title'] = '  Beautiful   Home  '
        item['price'] = 250000
        item['listing_url'] = 'https://test.com'
        
        processed = self.pipeline.process_item(item, None)
        assert processed['title'] == 'Beautiful Home'
    
    def test_clean_description(self):
        """Test description cleaning"""
        item = PropertyItem()
        item['title'] = 'Test'
        item['price'] = 100000
        item['listing_url'] = 'https://test.com'
        item['description'] = '  This is a  great   property.  '
        
        processed = self.pipeline.process_item(item, None)
        assert processed['description'] == 'This is a great property.'
    
    def test_generate_unique_id(self):
        """Test unique ID generation"""
        item = PropertyItem()
        item['listing_url'] = 'https://test.com/123'
        item['price'] = 250000
        item['title'] = 'Test'
        
        processed = self.pipeline.process_item(item, None)
        assert 'unique_id' in processed
        assert len(processed['unique_id']) > 5
    
    def test_clean_address(self):
        """Test address cleaning"""
        item = PropertyItem()
        item['title'] = 'Test'
        item['price'] = 100000
        item['listing_url'] = 'https://test.com'
        item['address'] = '  123 Main St  (downtown)  '
        
        processed = self.pipeline.process_item(item, None)
        assert processed['address'] == '123 Main St'


class TestValidationPipeline:
    """Test data validation"""
    
    def setup_method(self):
        self.pipeline = ValidationPipeline()
    
    def test_valid_item(self):
        """Test valid item passes"""
        item = PropertyItem()
        item['listing_url'] = 'https://test.com'
        item['price'] = 250000
        item['title'] = 'Test'
        
        processed = self.pipeline.process_item(item, None)
        assert processed is not None
    
    def test_missing_url(self):
        """Test item without URL is dropped"""
        item = PropertyItem()
        item['price'] = 250000
        item['title'] = 'Test'
        
        with pytest.raises(DropItem):
            self.pipeline.process_item(item, None)
    
    def test_missing_title(self):
        """Test item without title is dropped"""
        item = PropertyItem()
        item['listing_url'] = 'https://test.com'
        item['price'] = 250000
        
        with pytest.raises(DropItem):
            self.pipeline.process_item(item, None)
    
    def test_zero_price(self):
        """Test item with zero price is dropped"""
        item = PropertyItem()
        item['listing_url'] = 'https://test.com'
        item['price'] = 0
        item['title'] = 'Test'
        
        with pytest.raises(DropItem):
            self.pipeline.process_item(item, None)


class TestDuplicateFilterPipeline:
    """Test duplicate detection"""
    
    def setup_method(self):
        self.pipeline = DuplicateFilterPipeline()
    
    def test_duplicate_detection(self):
        """Test duplicate items are filtered out"""
        # Create two identical items
        item1 = PropertyItem()
        item1['unique_id'] = 'abc123'
        item1['listing_url'] = 'https://test.com/1'
        item1['price'] = 250000
        item1['title'] = 'Test'
        
        item2 = PropertyItem()
        item2['unique_id'] = 'abc123'
        item2['listing_url'] = 'https://test.com/2'
        item2['price'] = 200000
        item2['title'] = 'Test 2'
        
        # First one should pass
        self.pipeline.process_item(item1, None)
        
        # Second one should be dropped
        with pytest.raises(DropItem):
            self.pipeline.process_item(item2, None)
    
    def test_unique_items_pass(self):
        """Test unique items pass through"""
        item1 = PropertyItem()
        item1['unique_id'] = 'abc123'
        item1['listing_url'] = 'https://test.com/1'
        item1['price'] = 250000
        item1['title'] = 'Test'
        
        item2 = PropertyItem()
        item2['unique_id'] = 'def456'
        item2['listing_url'] = 'https://test.com/2'
        item2['price'] = 200000
        item2['title'] = 'Test 2'
        
        # Both should pass
        self.pipeline.process_item(item1, None)
        processed = self.pipeline.process_item(item2, None)
        assert processed is not None