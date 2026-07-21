
"""
Configuration for Facebook automation
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FacebookConfig:
    """Configuration for Facebook automation"""
    
    # Facebook Graph API settings
    ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
    USER_ID = os.getenv('FACEBOOK_USER_ID')
    PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
    
    # Graph API endpoints
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    # Rate limiting 
    MIN_DELAY = 60  
    MAX_DELAY = 180  
    
    # Search settings
    MAX_POSTS_TO_SCRAPE = 10
    SEARCH_QUERY = os.getenv('FACEBOOK_SEARCH_QUERY', 'real estate investment Milwaukee')
    
    # Comment templates
    COMMENT_TEMPLATES = [
        "Great insights on real estate investing! Thanks for sharing.",
        "Interesting perspective on the Milwaukee market.",
        "This is really helpful for investors looking at Midwest properties.",
        "Love the detailed analysis!",
        "Thanks for sharing this valuable information.",
        "Real estate investing in the Midwest is a great opportunity.",
        "This aligns perfectly with what we're seeing in the market.",
        "Very informative! Thanks for posting."
    ]
    
    @classmethod
    def validate_config(cls):
        """Check if required config variables are set"""
        if not cls.ACCESS_TOKEN:
            print(" WARNING: FACEBOOK_ACCESS_TOKEN not set in .env file")
            return False
        return True