"""
Utility functions for Facebook Playwright Automation.

Responsibilities
----------------
- Logging
- Human-like delays
- Human typing
- Mouse movement
- Scrolling
- Safe clicking
- Retry helpers
"""

from __future__ import annotations

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable, TypeVar

from loguru import logger
from playwright.async_api import Locator, Page

from .config import Config

T = TypeVar("T")

# ============================================================
# Logging
# ============================================================
#
# NOTE: Logger configuration is intentionally NOT done here.
#
# loguru's `logger` is a global singleton shared across the
# whole process. `main.py` already configures it once, at
# startup, with:
#
#     logger.add("logs/app_{time:YYYY-MM-DD}.log", ...)
#
# Previously this module also called `logger.remove()` +
# `logger.add(...)` at import time. Since `fb_automation`
# (and this module) is only imported lazily inside
# `run_facebook()`, that call silently wiped out main.py's
# handler and replaced it with a different log file/format —
# meaning `logs/app_{date}.log` stopped receiving log lines
# the moment Facebook automation ran, with no error or
# warning to indicate it happened.
#
# If Facebook automation needs its own dedicated log file
# *in addition to* main's, add it via `logger.add(...)` only
# (no `logger.remove()`), so both handlers stay active:
#
#     logger.add(
#         Config.LOG_FILE,
#         rotation="10 MB",
#         retention="14 days",
#         compression="zip",
#         enqueue=True,
#         level="INFO",
#         backtrace=True,
#         diagnose=True,
#         format=(
#             "{time:YYYY-MM-DD HH:mm:ss} | "
#             "{level:<8} | "
#             "{message}"
#         ),
#     )
#
# and rely on main.py (or the console) for the colorized
# stdout handler, rather than adding a second one here.

# ============================================================
# Time
# ============================================================

def timestamp() -> str:
    """Return current timestamp."""

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# Human Delays
# ============================================================

async def human_delay(
    minimum: float | None = None,
    maximum: float | None = None,
) -> None:
    """
    Random delay between actions.
    """

    minimum = Config.MIN_DELAY if minimum is None else minimum
    maximum = Config.MAX_DELAY if maximum is None else maximum

    await asyncio.sleep(
        random.uniform(minimum, maximum)
    )


def typing_delay() -> int:
    """
    Random typing delay in milliseconds.
    """

    return random.randint(40, 120)


# ============================================================
# Human Typing
# ============================================================

async def type_like_human(
    page: Page,
    selector_or_locator: str | Locator,
    text: str,
) -> None:
    """
    Type naturally into either an input, textarea or contenteditable element.
    Now supports both selector strings and Locator objects.
    """

    # Handle both selector strings and Locator objects
    if isinstance(selector_or_locator, str):
        locator = page.locator(selector_or_locator).last
    else:
        locator = selector_or_locator

    await locator.wait_for(
        state="visible",
        timeout=15000,
    )

    await locator.scroll_into_view_if_needed()

    await locator.click()

    # Clear existing content
    try:
        await locator.fill("")
    except Exception:
        pass

    for char in text:
        await page.keyboard.type(
            char,
            delay=random.randint(40, 120),
        )

        if random.random() < 0.08:
            await asyncio.sleep(
                random.uniform(0.15, 0.45)
            )

# ============================================================
# Mouse
# ============================================================

async def move_mouse_randomly(
    page: Page,
) -> None:
    """
    Human-like mouse movement.
    """

    await page.mouse.move(
        random.randint(50, 250),
        random.randint(50, 250),
        steps=random.randint(10, 25),
    )

    await page.mouse.move(
        random.randint(300, 1200),
        random.randint(150, 700),
        steps=random.randint(40, 80),
    )


# ============================================================
# Scroll
# ============================================================

async def human_scroll(page: Page) -> None:
    """
    Scroll naturally.
    """

    distance = random.randint(500, 900)

    await page.mouse.wheel(0, distance)

    await human_delay(
        Config.SCROLL_DELAY_MIN,
        Config.SCROLL_DELAY_MAX,
    )


async def random_scroll(page: Page) -> None:
    """
    Random scrolling behaviour.
    """

    for _ in range(random.randint(1, 3)):

        await page.mouse.wheel(
            0,
            random.randint(250, 700),
        )

        await human_delay(0.4, 1.2)


# ============================================================
# Safe Click
# ============================================================

async def safe_click(
    page: Page,
    selector: str,
) -> None:
    """
    Click an element safely.
    """

    locator = page.locator(selector).first

    await locator.wait_for(state="visible")

    await locator.scroll_into_view_if_needed()

    await move_mouse_randomly(page)

    await human_delay(0.3, 0.8)

    await locator.click()


async def safe_locator_click(
    locator: Locator,
) -> None:
    """
    Click a locator using several fallbacks.
    """

    await locator.wait_for(
        state="visible",
        timeout=15000,
    )

    await locator.scroll_into_view_if_needed()

    await human_delay(0.3, 0.8)

    try:
        await locator.click(timeout=5000)
        return
    except Exception:
        pass

    try:
        await locator.click(force=True)
        return
    except Exception:
        pass

    try:
        await locator.evaluate(
            "(el) => el.click()"
        )
        return
    except Exception:
        pass

    box = await locator.bounding_box()

    if box:

        await locator.page.mouse.click(
            box["x"] + box["width"] / 2,
            box["y"] + box["height"] / 2,
        )


# ============================================================
# Retry Helper
# ============================================================

async def retry_async(
    func: Callable[[], Awaitable[T]],
    retries: int = 3,
) -> T:
    """
    Retry async function.
    """

    last_error = None

    for attempt in range(retries):

        try:

            return await func()

        except Exception as exc:

            last_error = exc

            logger.warning(
                f"Retry {attempt + 1}/{retries}: {exc}"
            )

            await human_delay(1, 2)

    raise last_error


# ============================================================
# Screenshots
# ============================================================

async def save_screenshot(
    page: Page,
    name: str,
) -> Path:
    """
    Save a timestamped screenshot.

    Returns
    -------
    Path
        Path to the saved screenshot.
    """

    filename = (
        Config.SCREENSHOT_DIR /
        f"{name}_{datetime.now():%Y%m%d_%H%M%S}.png"
    )

    await page.screenshot(
        path=str(filename),
        full_page=True,
    )

    logger.info(f"Screenshot saved -> {filename}")

    return filename


# ============================================================
# JSON Helpers
# ============================================================

def save_json(
    data: Any,
    path: Path | None = None,
) -> None:
    """
    Save JSON using UTF-8 formatting.
    """

    path = path or Config.POSTS_JSON

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )

    logger.info(f"JSON saved -> {path}")


def load_json(
    path: Path | None = None,
) -> list[Any]:
    """
    Load JSON safely.

    Returns empty list if file
    does not exist or is invalid.
    """

    path = path or Config.POSTS_JSON

    if not path.exists():

        return []

    try:

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except json.JSONDecodeError:

        logger.warning(
            f"Invalid JSON file: {path}"
        )

        return []


# ============================================================
# Comments
# ============================================================

def random_comment() -> str:
    """
    Return a random predefined comment.
    """

    return random.choice(
        Config.COMMENT_TEMPLATES
    )


# ============================================================
# Formatting
# ============================================================

def separator(
    character: str = "=",
    length: int = 70,
) -> str:
    """
    Return a separator line.
    """

    return character * length


def banner(
    title: str,
) -> None:
    """
    Print a formatted banner.
    """

    line = separator()

    logger.info(line)
    logger.info(title)
    logger.info(line)


# ============================================================
# Misc Helpers
# ============================================================

def chunk_list(
    items: list[Any],
    size: int,
) -> list[list[Any]]:
    """
    Split a list into chunks.

    Example
    -------
    [1,2,3,4,5]
        ->
    [[1,2],[3,4],[5]]
    """

    return [

        items[i:i + size]

        for i in range(
            0,
            len(items),
            size,
        )

    ]


def unique(
    values: list[Any],
) -> list[Any]:
    """
    Remove duplicates while
    preserving order.
    """

    return list(
        dict.fromkeys(values)
    )


# ============================================================
# Exports
# ============================================================

__all__ = [

    "logger",

    "timestamp",

    "banner",

    "separator",

    "human_delay",

    "typing_delay",

    "type_like_human",

    "move_mouse_randomly",

    "human_scroll",

    "random_scroll",

    "safe_click",

    "safe_locator_click",

    "retry_async",

    "save_screenshot",

    "save_json",

    "load_json",

    "random_comment",

    "chunk_list",

    "unique",

]