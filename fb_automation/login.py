"""
Facebook Login Manager

Responsibilities
----------------
- Reuse persistent browser session
- Detect login state
- Support manual login
- Return authenticated page
"""

from __future__ import annotations

from playwright.async_api import Page

from .browser import BrowserManager
from .utils import (
    banner,
    logger,
    save_screenshot,
)


class FacebookLogin:
    """
    Handles Facebook authentication using an
    existing Playwright browser profile.
    """

    def __init__(self):

        self.browser = BrowserManager()

        self.page: Page | None = None

    # ==========================================================
    # Startup
    # ==========================================================

    async def start(self) -> Page:

        self.page = await self.browser.get_page()

        return self.page

    # ==========================================================
    # Session Detection
    # ==========================================================

    async def is_logged_in(self) -> bool:

        logger.info(
            "Checking Facebook session..."
        )

        url = self.page.url.lower()

        logger.info(f"Current URL: {url}")

        blocked = [

            "login",

            "checkpoint",

            "recover",

            "authentication",

            "two_step_verification",

        ]

        if any(item in url for item in blocked):

            return False

        try:

            await self.page.wait_for_load_state(
                "networkidle",
                timeout=10000,
            )

        except Exception:

            pass

        selectors = [

            '[role="feed"]',

            '[role="navigation"]',

            '[aria-label="Home"]',

            '[aria-label="Account"]',

            '[aria-label="Your profile"]',

        ]

        for selector in selectors:

            try:

                if await self.page.locator(selector).count():

                    logger.success(
                        "Facebook session detected."
                    )

                    return True

            except Exception:

                continue

        return False

    # ==========================================================
    # Manual Login
    # ==========================================================

    async def manual_login(self):

        banner("Manual Facebook Login")

        await self.page.goto(

            "https://web.facebook.com/",

            wait_until="domcontentloaded",

        )

        print()
        print("=" * 70)
        print("Login to Facebook in Chrome.")
        print("Complete any Two-Factor Authentication.")
        print("Wait until the Home Feed is visible.")
        print("Return here and press ENTER.")
        print("=" * 70)
        print()

        input("Press ENTER after login...")

        try:

            await self.page.wait_for_load_state(
                "networkidle",
                timeout=15000,
            )

        except Exception:

            pass

        if not await self.is_logged_in():

            raise RuntimeError(
                "Facebook session could not be verified."
            )

        await save_screenshot(

            self.page,

            "facebook_login_success",

        )

        logger.success(
            "Facebook session saved."
        )

    # ==========================================================
    # Authentication
    # ==========================================================

    async def get_authenticated_page(self) -> Page:

        if self.page is None:

            await self.start()

        if self.page.url in ("", "about:blank"):

            await self.page.goto(

                "https://web.facebook.com/",

                wait_until="domcontentloaded",

            )

        if not await self.is_logged_in():

            await self.manual_login()

        else:

            logger.success(
                "Using existing Facebook session."
            )

        return self.page

    # ==========================================================
    # Shutdown
    # ==========================================================

    async def close(self):

        await self.browser.close()