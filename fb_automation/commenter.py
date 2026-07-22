"""
Facebook Comment Automation

Responsibilities
----------------
- Locate comment fields
- Type naturally
- Publish comments
- Retry failures
- Update FacebookPost status
"""

from __future__ import annotations

import random

from playwright.async_api import (
    Locator,
    Page,
)

from .models import FacebookPost
from .utils import (
    banner,
    human_delay,
    logger,
    random_comment,
    retry_async,
    safe_locator_click,
    type_like_human,
)


class FacebookCommenter:
    """
    Handles commenting on Facebook posts.
    """

    def __init__(
        self,
        page: Page,
    ):

        self.page = page

    # ==========================================================
    # Comment Box
    # ==========================================================

    async def _find_comment_button(
        self,
        article: Locator,
    ) -> Locator | None:
        """
        Locate the Comment button.
        """

        selectors = [

            '[aria-label="Leave a comment"]',

            '[aria-label="Comment"]',

            '[role="button"][aria-label*="Comment"]',

            'div[role="button"]:has-text("Comment")',

            'span:has-text("Comment")',

        ]

        for selector in selectors:

            try:

                locator = article.locator(
                    selector
                ).first

                if await locator.count():

                    return locator

            except Exception:

                continue

        return None

    # ==========================================================
    # Comment Input
    # ==========================================================

    async def _find_comment_input(
        self,
    ) -> Locator | None:
        """
        Locate the comment editor.
        """

        selectors = [

            '[contenteditable="true"]',

            '[role="textbox"]',

            'div[contenteditable="true"]',

            'div[aria-label*="comment"]',

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

        return None
        # ==========================================================
    # Open Comment Box
    # ==========================================================

    async def _open_comment_box(
        self,
        article: Locator,
    ) -> Locator | None:
        """
        Open the comment editor for a post.
        """

        button = await self._find_comment_button(
            article
        )

        if button is None:

            logger.warning(
                "Comment button not found."
            )

            return None

        logger.info(
            "Opening comment box..."
        )

        await safe_locator_click(button)

        await human_delay(
            0.8,
            1.8,
        )

        editor = await self._find_comment_input()

        if editor is None:

            logger.warning(
                "Comment editor not found."
            )

        return editor

    # ==========================================================
    # Submit Comment
    # ==========================================================

    async def _submit_comment(
        self,
    ) -> bool:
        """
        Submit the current comment.
        """

        try:

            await human_delay(
                0.5,
                1.2,
            )

            await self.page.keyboard.press(
                "Enter"
            )

            await human_delay(
                2,
                4,
            )

            return True

        except Exception as exc:

            logger.warning(
                f"Unable to submit comment: {exc}"
            )

            return False

    # ==========================================================
    # Comment Single Post
    # ==========================================================

    async def comment_post(
        self,
        article: Locator,
        post: FacebookPost,
    ) -> bool:
        """
        Comment on a single Facebook post.
        """

        logger.info(
            f"Commenting on post by "
            f"{post.author}"
        )

        comment = random_comment()

        async def perform():

            editor = await self._open_comment_box(
                article
            )

            if editor is None:

                raise RuntimeError(
                    "No comment editor."
                )

            await type_like_human(

                self.page,

                editor,

                comment,

            )

            success = await self._submit_comment()

            if not success:

                raise RuntimeError(
                    "Submit failed."
                )

            return True

        try:

            await retry_async(
                perform,
                retries=3,
            )

            post.mark_commented(
                comment
            )

            logger.success(
                "Comment published."
            )

            return True

        except Exception as exc:

            logger.error(
                f"Comment failed: {exc}"
            )

            return False
            # ==========================================================
    # Comment Multiple Posts
    # ==========================================================

    async def comment_posts(
        self,
        posts: list[FacebookPost],
    ) -> list[FacebookPost]:
        """
        Randomly comment on a subset of scraped posts.
        """

        banner("Starting Comment Automation")

        if not posts:

            logger.warning(
                "No posts available for commenting."
            )

            return posts

        articles = await self.page.locator(
            'div[role="article"],'
            'div[data-pagelet^="FeedUnit"],'
            'div[data-pagelet^="TimelineFeedUnit"],'
            'div[data-pagelet*="FeedUnit"]'
        ).all()

        if not articles:

            logger.warning(
                "No Facebook articles found."
            )

            return posts

        count = min(
            random.randint(2, 4),
            len(posts),
            len(articles),
        )

        selected = sorted(
            random.sample(
                range(count),
                count,
            )
        )

        logger.info(
            f"Selected {count} post(s) for commenting."
        )

        for index in selected:

            logger.info(
                f"Commenting on post {index + 1}"
            )

            await human_delay(
                3,
                7,
            )

            await self.comment_post(

                articles[index],

                posts[index],

            )

            await human_delay(
                5,
                10,
            )

        banner("Comment Summary")

        total = len(posts)

        commented = sum(

            post.commented

            for post in posts

        )

        logger.success(

            f"Successfully commented "

            f"{commented}/{total} posts."

        )

        return posts

    # ==========================================================
    # Public
    # ==========================================================

    async def run(
        self,
        posts: list[FacebookPost],
    ) -> list[FacebookPost]:
        """
        Execute the complete commenting workflow.
        """

        return await self.comment_posts(
            posts
        )