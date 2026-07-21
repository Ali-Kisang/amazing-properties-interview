
"""
Facebook automation using Graph API
"""
import requests
import time
import random
from datetime import datetime
from loguru import logger
from config.settings import Config


class FacebookAutomation:
    """Facebook automation handler"""
    
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.posted_comments = set()
        
        # Setup headers
        self.session.headers.update({
            'User-Agent': self.config.USER_AGENTS[0],
            'Accept': 'application/json',
        })
        
        # Validate config
        if not self.config.FACEBOOK_ACCESS_TOKEN:
            logger.warning(" Facebook access token not configured")
    
    def search_posts(self, query, limit=10):
        """Search for posts on Facebook"""
        if not self.config.FACEBOOK_ACCESS_TOKEN:
            logger.error("No access token provided")
            return []
        
        try:
            url = "https://graph.facebook.com/v18.0/search"
            params = {
                'q': query,
                'type': 'post',
                'limit': limit,
                'access_token': self.config.FACEBOOK_ACCESS_TOKEN,
                'fields': 'id,message,created_time,from,permalink_url'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('data', [])
            logger.info(f" Found {len(posts)} posts matching '{query}'")
            return posts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching posts: {e}")
            return []
    
    def post_comment(self, post_id, comment_text):
        """Post a comment to a Facebook post"""
        if not self.config.FACEBOOK_ACCESS_TOKEN:
            logger.error("No access token provided")
            return False
        
        # Check for duplicate
        comment_key = f"{post_id}_{comment_text[:50]}"
        if comment_key in self.posted_comments:
            logger.info(f" Already commented on post {post_id}")
            return True
        
        try:
            # Human-like delay
            delay = random.randint(
                self.config.FACEBOOK_MIN_DELAY,
                self.config.FACEBOOK_MAX_DELAY
            )
            logger.info(f" Waiting {delay}s before posting...")
            time.sleep(delay)
            
            url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
            params = {
                'message': comment_text,
                'access_token': self.config.FACEBOOK_ACCESS_TOKEN
            }
            
            response = self.session.post(url, params=params, timeout=30)
            response.raise_for_status()
            
            logger.info(f" Posted comment to {post_id}")
            self.posted_comments.add(comment_key)
            
            # Additional delay
            time.sleep(random.randint(5, 15))
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error posting comment: {e}")
            return False
    
    def run_demo(self):
        """Run the Facebook automation demo"""
        logger.info(" Starting Facebook automation demo...")
        
        posts = self.search_posts(
            self.config.FACEBOOK_SEARCH_QUERY,
            self.config.FACEBOOK_MAX_POSTS
        )
        
        if not posts:
            logger.warning("No posts found")
            return
        
        comments = [
            "Great insights on real estate investing! Thanks for sharing.",
            "Interesting perspective on the Milwaukee market.",
            "This is really helpful for investors.",
            "Love the detailed analysis!",
            "Thanks for sharing this valuable information.",
            "Real estate investing in the Midwest is a great opportunity.",
            "This aligns perfectly with what we're seeing in the market."
        ]
        
        for i, post in enumerate(posts):
            post_id = post.get('id')
            if not post_id:
                continue
            
            comment_text = random.choice(comments)
            logger.info(f" Processing post {i+1}/{len(posts)}")
            
            success = self.post_comment(post_id, comment_text)
            
            if success:
                logger.info(f" Successfully engaged with post {post_id}")
            else:
                logger.warning(f" Failed to engage with post {post_id}")
            
            # Delay between posts
            if i < len(posts) - 1:
                delay = random.randint(30, 90)
                logger.info(f" Waiting {delay}s before next post...")
                time.sleep(delay)
        
        logger.info(" Facebook automation demo complete!")


def run():
    """Entry point for Facebook automation"""
    automation = FacebookAutomation()
    automation.run_demo()


if __name__ == "__main__":
    run()