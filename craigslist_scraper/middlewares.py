
"""
Downloader middlewares for anti-bot protection
"""
import random
import time
import hashlib
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import logging
from config.settings import Config

logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware:
    """Rotate user agents to avoid detection"""
    
    def __init__(self, user_agents):
        self.user_agents = user_agents
    
    @classmethod
    def from_crawler(cls, crawler):
        # Get list of user agents from settings
        user_agents = crawler.settings.get('USER_AGENT_LIST', [])
        if not user_agents:
            # Fallback user agents
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            ]
        return cls(user_agents)
    
    def process_request(self, request, spider):
        # Pick a random user agent
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent
        
        # Also rotate Accept headers
        request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        request.headers['Accept-Language'] = 'en-US,en;q=0.9'
        request.headers['Accept-Encoding'] = 'gzip, deflate, br'
        request.headers['Connection'] = 'keep-alive'


class ProxyMiddleware:
    """Handle proxy rotation"""
    
    def __init__(self, proxy_list):
        self.proxies = proxy_list
    
    @classmethod
    def from_crawler(cls, crawler):
        proxy_list = crawler.settings.get('PROXY_LIST', [])
        return cls(proxy_list)
    
    def process_request(self, request, spider):
        if self.proxies:
            proxy = random.choice(self.proxies)
            request.meta['proxy'] = proxy
            logger.debug(f"Using proxy: {proxy}")
    
    def process_response(self, request, response, spider):
        # If we get a 403 or 429, try rotating proxy
        if response.status in [403, 429, 503]:
            logger.warning(f"Got {response.status} from {request.url}")
            # Force proxy rotation by making this request fail
            request.dont_filter = True
            return request
        return response


class BrowserFingerprintMiddleware:
    """Mimic real browser fingerprint by sending realistic headers"""
    
    def process_request(self, request, spider):
        # Add realistic browser headers
        request.headers.update({
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Add random delay to mimic human behavior
        request.meta['download_slot'] = random.randint(1000, 5000)


class RequestThrottlingMiddleware:
    """Intelligent request throttling with exponential backoff"""
    
    def __init__(self, crawler):
        self.crawler = crawler
        self.request_count = 0
        self.start_time = time.time()
    
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware
    
    def process_request(self, request, spider):
        # Track request rate
        self.request_count += 1
        
        # Calculate requests per second
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            rate = self.request_count / elapsed
            if rate > 5:  # More than 5 requests/second
                # Add random delay
                delay = random.uniform(1, 3)
                time.sleep(delay)
    
    def spider_closed(self, spider):
        # Log statistics
        elapsed = time.time() - self.start_time
        rate = self.request_count / elapsed if elapsed > 0 else 0
        spider.logger.info(f"Total requests: {self.request_count}")
        spider.logger.info(f"Average rate: {rate:.2f} requests/second")


class SessionManagementMiddleware:
    """Maintain sessions and handle authentication flows"""
    
    def __init__(self):
        self.sessions = {}
        self.cookies = {}
    
    def process_request(self, request, spider):
        # Use consistent session for same domain
        domain = request.url.split('/')[2] if '://' in request.url else ''
        
        if domain not in self.sessions:
            self.sessions[domain] = {
                'session_id': hashlib.md5(f"{domain}_{time.time()}".encode()).hexdigest()[:16],
                'cookies': {},
                'headers': {}
            }
        
        # Add session cookie
        if 'cookies' in self.sessions[domain]:
            request.cookies.update(self.sessions[domain]['cookies'])
    
    def process_response(self, request, response, spider):
        # Save session cookies
        if 'Set-Cookie' in response.headers:
            domain = request.url.split('/')[2] if '://' in request.url else ''
            if domain in self.sessions:
                cookies = response.headers.getlist('Set-Cookie')
                for cookie in cookies:
                    # Parse cookie
                    parts = cookie.decode('utf-8').split(';')[0].split('=')
                    if len(parts) == 2:
                        self.sessions[domain]['cookies'][parts[0]] = parts[1]
        
        return response