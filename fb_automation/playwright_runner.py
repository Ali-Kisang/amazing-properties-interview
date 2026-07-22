"""
Facebook Automation Runner

Responsibilities
----------------
- Initialize configuration
- Authenticate Facebook
- Scrape feed
- Comment on posts
- Save results
- Shutdown browser safely
"""

from __future__ import annotations

import asyncio

from .commenter import FacebookCommenter
from .config import Config
from .login import FacebookLogin
from .models import FacebookPost
from .scraper import FacebookScraper
from .utils import (
    banner,
    logger,
    save_json,
)


class FacebookAutomation:
    """
    Coordinates the complete Facebook automation workflow.
    """

    def __init__(self):

        Config.initialize()

        self.login = FacebookLogin()

        self.page = None

        self.scraper: FacebookScraper | None = None

        self.commenter: FacebookCommenter | None = None

        self.posts: list[FacebookPost] = []

    # ==========================================================
    # Initialize
    # ==========================================================

    async def initialize(self) -> None:
        """
        Launch browser and authenticate Facebook.
        """

        banner("Initializing Facebook Automation")

        self.page = await self.login.get_authenticated_page()

        self.scraper = FacebookScraper(self.page)

        self.commenter = FacebookCommenter(self.page)

        logger.success(
            "Facebook automation initialized."
        )

    # ==========================================================
    # Scrape Posts
    # ==========================================================

    async def scrape_posts(
        self,
    ) -> list[FacebookPost]:
        """
        Scrape Facebook posts.
        """

        banner("Scraping Facebook Feed")

        if self.scraper is None:
            raise RuntimeError("Scraper not initialized.")

        self.posts = await self.scraper.scrape()

        logger.success(
            f"Scraped {len(self.posts)} posts."
        )

        return self.posts

    # ==========================================================
    # Comment Posts
    # ==========================================================

    async def comment_posts(
        self,
    ) -> list[FacebookPost]:
        """
        Comment on scraped posts.
        """

        banner("Commenting on Facebook Posts")

        if not self.posts:

            logger.warning(
                "No posts available for commenting."
            )

            return self.posts

        if self.commenter is None:
            raise RuntimeError("Commenter not initialized.")

        self.posts = await self.commenter.run(
            self.posts
        )

        commented = sum(
            post.commented
            for post in self.posts
        )

        logger.success(
            f"Commented on {commented}/{len(self.posts)} posts."
        )

        return self.posts

    # ==========================================================
    # Save Results
    # ==========================================================

    async def save_results(self) -> None:
        """
        Save posts to JSON.
        """

        banner("Saving Results")

        save_json(
            [
                post.to_dict()
                for post in self.posts
            ]
        )

        logger.success(
            "Results saved successfully."
        )

    # ==========================================================
    # Summary
    # ==========================================================

    def print_summary(self) -> None:

        banner("Automation Summary")

        total = len(self.posts)

        commented = sum(
            post.commented
            for post in self.posts
        )

        logger.info(
            f"Posts Scraped   : {total}"
        )

        logger.info(
            f"Posts Commented : {commented}"
        )

        logger.success(
            "Automation completed successfully."
        )

    # ==========================================================
    # Shutdown
    # ==========================================================

    async def shutdown(self) -> None:

        banner("Shutting Down")

        try:

            await self.login.close()

        except Exception as exc:

            logger.warning(
                f"Shutdown warning: {exc}"
            )

        logger.success(
            "Shutdown complete."
        )

    # ==========================================================
    # Run Workflow
    # ==========================================================

    async def run(self) -> list[FacebookPost]:

        try:

            await self.initialize()

            await self.scrape_posts()

            await self.save_results()

            await self.comment_posts()

            await self.save_results()

            self.print_summary()

            return self.posts

        except Exception as exc:

            logger.exception(
                f"Automation failed: {exc}"
            )
            raise

        finally:

            await self.shutdown()


# ==========================================================
# Public Entry Point
# ==========================================================

def run() -> list[FacebookPost]:

    async def _main():

        automation = FacebookAutomation()

        return await automation.run()

    return asyncio.run(_main())