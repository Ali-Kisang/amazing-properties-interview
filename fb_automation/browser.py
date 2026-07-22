"""
Browser Manager

Responsibilities
----------------
- Launch persistent Chrome
- Reuse existing profile
- Create browser context
- Create pages
- Close browser safely
"""

from __future__ import annotations

from playwright.async_api import (
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from .config import Config
from .utils import banner, logger


class BrowserManager:
    """
    Manages the Playwright browser lifecycle.
    """

    def __init__(self) -> None:
        self.playwright: Playwright | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    # ==========================================================
    # Startup
    # ==========================================================

    async def start(self) -> Page:
        """
        Launch Chrome using a persistent profile.
        """

        if self.page is not None:
            return self.page

        banner("Launching Chrome")

        self.playwright = await async_playwright().start()

        self.context = (
            await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(Config.PROFILE_DIR),
                headless=Config.HEADLESS,
                channel=Config.BROWSER_CHANNEL,
                viewport=Config.VIEWPORT,
                user_agent=Config.USER_AGENT,
                accept_downloads=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-infobars",
                    "--no-first-run",
                    "--start-maximized",
                ],
            )
        )

        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()

        # Set default timeout for all Playwright actions
        self.page.set_default_timeout(Config.PAGE_TIMEOUT)

        logger.success("Chrome launched successfully.")

        return self.page

    # ==========================================================
    # Get Page
    # ==========================================================

    async def get_page(self) -> Page:
        """
        Return the active browser page.
        """

        if self.page is None:
            return await self.start()

        return self.page

    # ==========================================================
    # Close
    # ==========================================================

    async def close(self) -> None:
        """
        Close browser resources safely.
        """

        banner("Closing Browser")

        try:
            if self.context:
                await self.context.close()
        except Exception as exc:
            logger.warning(f"Context close failed: {exc}")

        try:
            if self.playwright:
                await self.playwright.stop()
        except Exception as exc:
            logger.warning(f"Playwright stop failed: {exc}")

        self.page = None
        self.context = None
        self.playwright = None

        logger.success("Browser closed successfully.")