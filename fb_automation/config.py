"""
Configuration Module

Centralized configuration for the Facebook Playwright Automation.

Responsibilities
----------------
- Load environment variables
- Validate configuration
- Create project directories
- Browser configuration
- Timing configuration
- Scraper settings
- Comment settings
- Output file paths
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Application configuration."""

    # ==========================================================
    # Project Paths
    # ==========================================================

    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    DATA_DIR = PROJECT_ROOT / "data"
    LOG_DIR = PROJECT_ROOT / "logs"
    SCREENSHOT_DIR = PROJECT_ROOT / "screenshots"
    PROFILE_DIR = PROJECT_ROOT / "playwright_profile"

    POSTS_JSON = DATA_DIR / "posts.json"
    RESULTS_JSON = DATA_DIR / "post_results.json"
    REPORT_JSON = DATA_DIR / "report.json"

    LOG_FILE = LOG_DIR / "facebook.log"

    # ==========================================================
    # Facebook
    # ==========================================================

    FACEBOOK_HOME = "https://www.facebook.com/"

    FACEBOOK_EMAIL = os.getenv("FACEBOOK_EMAIL", "").strip()
    FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD", "").strip()

    # ==========================================================
    # Browser
    # ==========================================================

    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"

    USER_DATA_DIR = str(
        PROFILE_DIR
    )

    BROWSER_CHANNEL = "chrome"

    VIEWPORT = {
        "width": 1600,
        "height": 900,
    }

    USER_AGENT = (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    )

    PAGE_TIMEOUT = 60000

    NAVIGATION_TIMEOUT = 60000

    # ==========================================================
    # Human Behaviour
    # ==========================================================

    MIN_DELAY = 1.5
    MAX_DELAY = 4.5

    TYPE_DELAY_MIN = 0.05
    TYPE_DELAY_MAX = 0.18

    SCROLL_DELAY_MIN = 1.0
    SCROLL_DELAY_MAX = 3.0

    MOUSE_MOVE_MIN = 20
    MOUSE_MOVE_MAX = 80

    # ==========================================================
    # Scraper
    # ==========================================================

    MAX_SCROLLS = 20

    MAX_POSTS = 30

    MAX_RETRIES = 3

    RETRY_DELAY = 2

    # ==========================================================
    # Commenter
    # ==========================================================

    MAX_COMMENTS = 5

    COMMENT_DELAY_MIN = 5

    COMMENT_DELAY_MAX = 12

    COMMENT_TEMPLATES = [

        "Great insights! Thanks for sharing.",

        "Very informative post. Appreciate the update.",

        "Excellent perspective. Thanks for posting.",

        "Helpful information. Looking forward to more.",

        "Interesting thoughts. Thanks for sharing.",

        "Great content as always!",

        "Really useful information.",

        "Appreciate you taking the time to post this.",

        "Well explained!",

        "Thanks for sharing your experience."
    ]

    # ==========================================================
    # Timeline Poster
    # ==========================================================

    ENABLE_POSTING = True

    DEFAULT_TIMELINE_MESSAGE = (
        "Hello from my Playwright automation test 🚀"
    )

    # ==========================================================
    # Logging
    # ==========================================================

    LOG_LEVEL = "INFO"

    SAVE_SCREENSHOTS = True

    SAVE_HTML_ON_ERROR = False

    # ==========================================================
    # Validation
    # ==========================================================

    @classmethod
    def validate(cls) -> None:
        """
        Validate configuration.
        """

        errors = []

        if cls.MAX_POSTS <= 0:
            errors.append("MAX_POSTS must be greater than zero.")

        if cls.MAX_SCROLLS <= 0:
            errors.append("MAX_SCROLLS must be greater than zero.")

        if cls.MAX_COMMENTS <= 0:
            errors.append("MAX_COMMENTS must be greater than zero.")

        if errors:
            raise ValueError("\n".join(errors))

    # ==========================================================
    # Directories
    # ==========================================================

    @classmethod
    def create_directories(cls) -> None:
        """
        Create required directories.
        """

        cls.DATA_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        cls.LOG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        cls.SCREENSHOT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        cls.PROFILE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==========================================================
    # Startup
    # ==========================================================

    @classmethod
    def initialize(cls) -> None:
        """
        Initialize the application.
        """

        cls.create_directories()

        cls.validate()