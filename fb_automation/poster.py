"""
Facebook Timeline Poster

Responsibilities
----------------
- Open Facebook Home Feed
- Open the timeline composer
- Wait for the post dialog
- Prepare for typing
"""

from __future__ import annotations

from playwright.async_api import Locator, Page

from .utils import (
    banner,
    human_delay,
    logger,
    move_mouse_randomly,
    retry_async,
    safe_locator_click,
    type_like_human,
)


class FacebookPoster:
    """Handles creating timeline posts."""

    DIALOG_SELECTOR = (
        'div[role="dialog"],'
        'div[aria-modal="true"]'
    )

    def __init__(self, page: Page):

        self.page = page

    # ==========================================================
    # Navigation
    # ==========================================================

    async def open_home(self) -> None:
        """
        Open the authenticated Facebook Home Feed.
        """

        logger.info("Opening Facebook Home...")

        await self.page.goto(
            "https://web.facebook.com/",
            wait_until="domcontentloaded",
            timeout=60000,
        )

        await self.page.wait_for_timeout(5000)

        logger.success("Facebook Home loaded.")

    # ==========================================================
    # Composer Trigger
    # ==========================================================

    async def _find_composer_trigger(
        self,
    ) -> Locator | None:
        """
        Locate the 'What's on your mind?' composer.
        """

        selectors = [

            'div[role="button"][aria-label*="What"]',

            'div[role="button"]:has-text("What\'s on your mind")',

            'span:has-text("What\'s on your mind")',

            'div[data-pagelet="FeedUnit_0"] div[role="button"]',

            'div[aria-label*="Create a post"]',

            'div[role="button"][tabindex="0"]',

        ]

        for selector in selectors:

            try:

                locator = self.page.locator(
                    selector
                ).first

                if await locator.count():

                    if await locator.is_visible():

                        logger.info(
                            f"Composer found using: {selector}"
                        )

                        return locator

            except Exception:

                continue

        logger.warning(
            "Unable to locate the composer trigger."
        )

        return None

    # ==========================================================
    # Open Composer
    # ==========================================================

    async def open_composer(
        self,
    ) -> bool:
        """
        Open Facebook's Create Post dialog.
        """

        banner("Opening Timeline Composer")

        await self.open_home()

        trigger = await self._find_composer_trigger()

        if trigger is None:

            return False

        async def click():

            await move_mouse_randomly(
                self.page
            )

            await safe_locator_click(
                trigger
            )

        await retry_async(click)

        try:

            await self.page.wait_for_selector(
                self.DIALOG_SELECTOR,
                timeout=20000,
            )

            # Give React time to mount the editor.
            await self.page.wait_for_timeout(
                3000
            )

            logger.success(
                "Timeline composer opened."
            )

            return True

        except Exception:

            logger.warning(
                "Composer dialog failed to open."
            )

            try:

                await self.page.screenshot(
                    path="data/composer_failed.png",
                    full_page=True,
                )

                with open(
                    "data/composer_failed.html",
                    "w",
                    encoding="utf-8",
                ) as f:

                    f.write(
                        await self.page.content()
                    )

                logger.info(
                    "Saved composer_failed.html"
                )

            except Exception as exc:

                logger.warning(exc)

            return False
            # ==========================================================
    # Editor
    # ==========================================================

    async def _find_editor(self) -> Locator | None:
        """
        Locate Facebook's post editor inside the dialog.
        """

        selectors = [

            'div[role="dialog"] div[role="textbox"]',

            'div[aria-modal="true"] div[role="textbox"]',

            'div[contenteditable="true"]',

            '[contenteditable="true"][spellcheck="true"]',

            'div[data-lexical-editor="true"]',

            'div[aria-label*="on your mind"]',

        ]

        for selector in selectors:

            try:

                locator = self.page.locator(selector).last

                if await locator.count():

                    await locator.wait_for(
                        state="visible",
                        timeout=5000,
                    )

                    logger.info(
                        f"Editor found using: {selector}"
                    )

                    return locator

            except Exception:

                continue

        # Debug snapshot

        try:

            await self.page.screenshot(
                path="data/editor_not_found.png",
                full_page=True,
            )

            with open(
                "data/editor_not_found.html",
                "w",
                encoding="utf-8",
            ) as f:

                f.write(await self.page.content())

        except Exception:

            pass

        logger.warning("Post editor not found.")

        return None

    # ==========================================================
    # Type Post
    # ==========================================================

    async def type_post(
        self,
        text: str,
    ) -> bool:

        editor = await self._find_editor()

        if editor is None:

            return False

        try:

            await editor.click()

            await human_delay(0.5, 1)

            await type_like_human(
                self.page,
                editor,
                text,
            )

            logger.success(
                "Post typed successfully."
            )

            return True

        except Exception as exc:

            logger.warning(exc)

            return False

    # ==========================================================
    # Submit Button
    # ==========================================================

    async def _find_submit_button(
        self,
    ) -> Locator | None:

        selectors = [

            'div[aria-label="Post"]',

            'div[role="button"][aria-label="Post"]',

            'div[role="dialog"] div[role="button"]:has-text("Post")',

            'button:has-text("Post")',

        ]

        for selector in selectors:

            try:

                locator = self.page.locator(
                    selector
                ).last

                if await locator.count():

                    return locator

            except Exception:

                continue

        logger.warning(
            "Submit button not found."
        )

        return None

    async def submit_post(self) -> bool:

        button = await self._find_submit_button()

        if button is None:

            return False

        async def click():

            await safe_locator_click(
                button
            )

        await retry_async(click)

        try:

            await self.page.wait_for_selector(
                self.DIALOG_SELECTOR,
                state="detached",
                timeout=30000,
            )

            logger.success(
                "Post submitted."
            )

        except Exception:

            logger.warning(
                "Dialog still open after submission."
            )

        await human_delay(2, 4)

        return True

    # ==========================================================
    # Verify
    # ==========================================================

    async def verify_post(
        self,
        text: str,
    ) -> bool:

        try:

            await self.page.wait_for_timeout(
                5000
            )

            locator = self.page.get_by_text(
                text,
                exact=False,
            ).first

            await locator.wait_for(
                state="visible",
                timeout=10000,
            )

            logger.success(
                "Post verified."
            )

            return True

        except Exception:

            logger.warning(
                "Unable to verify post."
            )

            return False

    # ==========================================================
    # Public
    # ==========================================================

    async def create_post(
        self,
        text: str,
    ) -> dict:

        banner("Creating Timeline Post")

        result = {

            "text": text,

            "success": False,

            "verified": False,

            "error": None,

        }

        try:

            if not await self.open_composer():

                result["error"] = "Composer not found"

                return result

            if not await self.type_post(text):

                result["error"] = "Editor not found"

                return result

            if not await self.submit_post():

                result["error"] = "Submit button not found"

                return result

            result["verified"] = await self.verify_post(
                text
            )

            result["success"] = True

            logger.success(
                "Timeline post created successfully."
            )

            return result

        except Exception as exc:

            logger.exception(exc)

            result["error"] = str(exc)

            return result