"""
Facebook Feed Scraper

Responsibilities
----------------
- Open Facebook home feed
- Scroll naturally
- Discover posts
- Extract structured data
- Return FacebookPost objects
"""

from __future__ import annotations

from playwright.async_api import (
    Locator,
    Page,
)

from .config import Config
from .models import FacebookPost
from .utils import (
    banner,
    human_scroll,
    logger,
    retry_async,
    unique,
)


class FacebookScraper:
    """
    Scrapes posts from the authenticated
    Facebook Home Feed.
    """

    # Multiple fallback selectors for Facebook posts
    ARTICLE_SELECTORS = [
        'div[role="article"]:not([aria-label="Loading..."])',
        'div[data-pagelet^="FeedUnit_"]',
        'div[data-pagelet*="FeedUnit"]',
        'div[data-testid="fbfeed_story"]',
        'div[data-testid="feed_story"]',
        'div[data-testid="story"]',
        'div[data-ad-comet-preview="message"]',
        'div[data-ad-rendering-role="story_message"]',
    ]

    def __init__(
        self,
        page: Page,
    ):

        self.page = page

        self.posts: list[FacebookPost] = []

        self.seen: set[str] = set()

    # ==========================================================
    # Navigation
    # ==========================================================

    async def open_feed(self) -> None:

        banner("Opening Facebook Feed")

        logger.info(
            "Navigating to Facebook Home..."
        )

        await self.page.goto(

            "https://web.facebook.com/",

            wait_until="domcontentloaded",

            timeout=60000,

        )

        await self.page.wait_for_timeout(8000)  # Increased wait time
        
        # Log the page title and URL for debugging
        title = await self.page.title()
        url = self.page.url
        logger.info(f"Page Title: {title}")
        logger.info(f"Current URL: {url}")
        
        # Try to find any content on the page
        body_text = await self.page.locator("body").inner_text()
        logger.info(f"Body text length: {len(body_text)}")
        
        # Check for login or other issues
        if "login" in url.lower() or "login" in body_text.lower()[:500]:
            logger.error("Login page detected! Session may have expired.")
            
        # Wait for feed to load by checking for any content
        try:
            await self.page.wait_for_function(
                """
                () => {
                    // Check if there's any substantial text content
                    const body = document.body.innerText;
                    return body.length > 100;
                }
                """,
                timeout=30000
            )
            logger.success("Page loaded with content.")
        except Exception:
            logger.warning("Page may not have loaded properly.")

    # ==========================================================
    # Feed Loading
    # ==========================================================

    async def load_feed(self) -> None:

        banner("Loading Feed")

        previous = 0
        unchanged = 0
        
        for scroll in range(Config.MAX_SCROLLS):
            
            # Scroll to bottom to trigger loading
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Wait for content to load
            await self.page.wait_for_timeout(3000)
            
            # Count posts using multiple selectors
            total = 0
            for selector in self.ARTICLE_SELECTORS:
                try:
                    count = await self.page.locator(selector).count()
                    total += count
                except:
                    pass
            
            logger.info(
                f"Scroll {scroll+1}: "
                f"{total} potential posts"
            )

            if total == previous:
                unchanged += 1
            else:
                unchanged = 0

            previous = total

            if unchanged >= 3:
                logger.info(
                    "End of feed detected."
                )
                break

    # ==========================================================
    # Safe Helpers
    # ==========================================================

    async def _text(
        self,
        locator: Locator,
    ) -> str:

        try:

            return (
                await locator.inner_text()
            ).strip()

        except Exception:

            return ""

    async def _all_text(
        self,
        locator: Locator,
    ) -> list[str]:

        values = []

        try:

            locators = await locator.all()

            for item in locators:

                text = await self._text(item)

                if text:

                    values.append(text)

        except Exception:

            pass

        return unique(values)
    
    # ==========================================================
    # Author Extraction
    # ==========================================================

    async def _extract_author(
        self,
        article: Locator,
    ) -> str:
        """
        Extract the author's name using several
        fallback strategies.
        """

        selectors = [

            'a[href*="/profile.php"]',

            'a[href*="/user/"]',

            "strong",

            "h2",

            "h3",

            'span[dir="auto"]',

        ]

        for selector in selectors:

            try:

                elements = await article.locator(
                    selector
                ).all()

                for element in elements:

                    text = await self._text(element)

                    if (
                        text
                        and len(text) > 2
                        and len(text) < 80
                    ):

                        return text

            except Exception:

                continue

        return "Unknown Author"

    # ==========================================================
    # Text Extraction
    # ==========================================================

    async def _extract_text(
        self,
        article: Locator,
    ) -> str:
        """
        Extract visible post text.
        """
        try:
            # Try multiple approaches to get text
            text = ""
            
            # First try: specific selectors for post text
            text_selectors = [
                'div[data-ad-preview="message"]',
                'div[data-ad-comet-preview="message"]',
                'div[data-testid="post_message"]',
                'div[data-testid="feed_story_text"]',
                'div[dir="auto"]',
                'span[dir="auto"]',
            ]
            
            for selector in text_selectors:
                try:
                    elements = await article.locator(selector).all()
                    for element in elements:
                        element_text = await self._text(element)
                        if element_text and len(element_text) > 10:
                            text += " " + element_text
                except:
                    continue
            
            # If no text found, get all text from the article
            if not text or len(text.strip()) < 10:
                text = await article.inner_text()
            
            # Clean up the text
            text = " ".join(text.split())
            
            # Debug: Log first 200 chars
            if text:
                logger.info(f"RAW POST TEXT: {text[:200]}...")
            else:
                logger.warning("No text found in article")
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""

    # ==========================================================
    # Timestamp
    # ==========================================================

    async def _extract_timestamp(
        self,
        article: Locator,
    ) -> str:

        selectors = [

            "time",

            "abbr",

            'a[href*="/posts/"]',

            'a[href*="/permalink/"]',

        ]

        for selector in selectors:

            try:

                locator = article.locator(
                    selector
                ).first

                if await locator.count():

                    value = await self._text(locator)

                    if value:

                        return value

            except Exception:

                pass

        return ""

    # ==========================================================
    # Links
    # ==========================================================

    async def _extract_links(
        self,
        article: Locator,
    ) -> list[str]:

        try:

            links = await article.locator(
                "a"
            ).evaluate_all(
                """
                elements =>
                    elements
                        .map(a => a.href)
                        .filter(Boolean)
                """
            )

            return unique(links)

        except Exception:

            return []

    # ==========================================================
    # Images
    # ==========================================================

    async def _extract_images(
        self,
        article: Locator,
    ) -> list[str]:

        try:

            images = await article.locator(
                "img"
            ).evaluate_all(
                """
                elements =>
                    elements
                        .map(img => img.src)
                        .filter(Boolean)
                """
            )

            return unique(images)

        except Exception:

            return []

    # ==========================================================
    # Build FacebookPost
    # ==========================================================

    async def _extract_post(
        self,
        article: Locator,
    ) -> FacebookPost | None:
        
        # First check: Is this a loading skeleton?
        try:
            aria_label = await article.get_attribute("aria-label")
            if aria_label and "Loading" in aria_label:
                logger.debug("Skipping loading skeleton")
                return None
            
            visual_completion = await article.get_attribute("data-visualcompletion")
            if visual_completion and "loading" in visual_completion:
                logger.debug("Skipping loading skeleton")
                return None
        except:
            pass
        
        # Extract author and text
        author = await self._extract_author(article)
        text = await self._extract_text(article)
        
        # Debug: Print what we're actually getting
        logger.info("=" * 80)
        logger.info(f"AUTHOR: {author}")
        logger.info(f"TEXT LENGTH: {len(text)}")
        if text:
            logger.info(f"TEXT:\n{text[:500]}...")  # First 500 chars
        else:
            logger.info("TEXT: (empty)")
        logger.info("=" * 80)
        
        # Check if we have valid content
        if not text or len(text.strip()) < 10:
            logger.debug("Text too short or empty, skipping")
            return None
        
        timestamp = await self._extract_timestamp(article)
        links = await self._extract_links(article)
        images = await self._extract_images(article)
        
        post_url = ""
        for link in links:
            if "/posts/" in link or "/permalink/" in link:
                post_url = link
                break
        
        post = FacebookPost(
            author=author,
            text=text,
            timestamp=timestamp,
            post_url=post_url,
            images=images,
            links=links,
        )
        
        fingerprint = post.fingerprint()
        if fingerprint in self.seen:
            return None
        
        self.seen.add(fingerprint)
        return post
    
    # ==========================================================
    # Collect Posts
    # ==========================================================

    async def collect_posts(
        self,
    ) -> list[FacebookPost]:
        """
        Collect posts currently visible
        in the Facebook feed.
        """

        banner("Collecting Posts")

        # Try all selectors and collect unique articles
        all_articles = []
        for selector in self.ARTICLE_SELECTORS:
            try:
                articles = await self.page.locator(selector).all()
                all_articles.extend(articles)
                logger.info(f"Selector '{selector}' found {len(articles)} items")
            except Exception as e:
                logger.debug(f"Selector '{selector}' failed: {e}")

        # Remove duplicates based on inner text or HTML
        unique_articles = []
        seen_content = set()
        for article in all_articles:
            try:
                html = await article.evaluate("el => el.outerHTML")
                if html not in seen_content:
                    seen_content.add(html)
                    unique_articles.append(article)
            except:
                pass

        logger.info(
            f"Detected {len(unique_articles)} unique feed items."
        )

        for index, article in enumerate(
            unique_articles,
            start=1,
        ):

            if len(self.posts) >= Config.MAX_POSTS:
                logger.info(
                    "Maximum configured posts reached."
                )
                break

            logger.info(
                f"Processing post "
                f"{index}/{len(unique_articles)}"
            )

            try:

                async def extract():
                    return await self._extract_post(article)

                post = await retry_async(extract)

                if post is None:
                    continue

                self.posts.append(post)

                logger.success(
                    f"Collected post #{len(self.posts)}"
                )

            except Exception as exc:

                logger.warning(
                    f"Unable to process post "
                    f"{index}: {exc}"
                )

        logger.success(
            f"Collected {len(self.posts)} unique posts."
        )

        return self.posts

    # ==========================================================
    # Summary
    # ==========================================================

    def summary(self) -> None:
        """
        Display scraper statistics.
        """

        banner("Scraper Summary")

        logger.info(
            f"Posts Collected : {len(self.posts)}"
        )

        logger.info(
            f"Duplicates      : "
            f"{len(self.seen) - len(self.posts)}"
        )

    # ==========================================================
    # Public
    # ==========================================================

    async def scrape(
        self,
    ) -> list[FacebookPost]:
        """
        Complete scraping workflow.

        Returns
        -------
        list[FacebookPost]
        """

        banner(
            "Starting Facebook Feed Scraper"
        )

        self.posts.clear()

        self.seen.clear()

        await self.open_feed()

        await self.load_feed()

        await self.collect_posts()

        self.summary()

        return self.posts