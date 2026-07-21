import scrapy
from urllib.parse import urlencode
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Keywords we care about, checked against title/description after scraping
# rather than baked into the CL query string (which was over-narrowing results)
KEYWORDS = ['single family', 'duplex', 'multi-family', 'multifamily', 'investment', 'rental']


class CLSpider(scrapy.Spider):
    name = "cl"

    async def start(self):
        logger.info("=" * 60)
        logger.info("🚀 START CALLED!")
        logger.info("=" * 60)

        cities = ['milwaukee', 'columbus']
        min_price = 50000
        max_price = 250000

        for city in cities:
            params = {
                'min_price': min_price,
                'max_price': max_price,
            }
            url = f"https://{city}.craigslist.org/search/rea?{urlencode(params)}"
            logger.info(f"🔍 Fetching: {url}")

            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'city': city},
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
            )

    def parse(self, response):
        city = response.meta.get('city', 'unknown')
        logger.info(f"📍 {city} - Status: {response.status}")
        logger.info(f"📍 {city} - Final URL after redirects: {response.url}")

        if response.status != 200:
            logger.error(f"❌ HTTP {response.status}")
            return

        if 'captcha' in response.text.lower() or len(response.text) < 500:
            logger.warning(f"⚠️ {city} - Response looks suspicious (possible block page). Length: {len(response.text)}")

        page_title = response.css('title::text').get()
        logger.info(f"📍 {city} - Page title: {page_title}")

        listings = response.css('ol.cl-static-search-results li.cl-static-search-result')
        logger.info(f"📍 {city} - Found {len(listings)} listings")

        for listing in listings:
            detail_url = listing.css('a::attr(href)').get()
            title = listing.css('div.title::text').get()
            price = listing.css('div.price::text').get()
            location = listing.css('div.location::text').get()

            title_clean = title.strip() if title else ''
            matched_keywords = [kw for kw in KEYWORDS if kw in title_clean.lower()]

            logger.info(f"📄 Found: {title_clean[:50] or 'No title'} - {price}")

            yield {
                'title': title_clean or None,
                'price': price.strip() if price else None,
                'location': location.strip() if location else None,
                'listing_url': detail_url,
                'city': city,
                'matched_keywords': matched_keywords,
                'scraped_at': datetime.now().isoformat(),
            }

        # Pagination for the new search/area format uses an offset-based
        # "s" param (e.g. &s=120 for the second page of 120). Follow it
        # if present so we don't silently stop at page 1.
        next_link = response.css('a.button.next::attr(href)').get()
        if next_link:
            next_url = response.urljoin(next_link)
            logger.info(f"➡️ {city} - Following pagination: {next_url}")
            yield scrapy.Request(
                url=next_url,
                callback=self.parse,
                meta={'city': city}
            )
        else:
            logger.info(f"📍 {city} - No further pagination link found")