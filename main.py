"""
Main entry point for the Amazing Properties Assessment.

Features
--------
1. Craigslist Real Estate Scraper
2. Facebook Feed Scraper + Comment Automation
3. Run Everything
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# ==========================================================
# Environment
# ==========================================================

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# ==========================================================
# Logging
# ==========================================================

logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
)

logger.add(
    LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    rotation="10 MB",
    retention="14 days",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True,
    level="INFO",
)

# ==========================================================
# Craigslist Scraper
# ==========================================================


def run_scraper() -> None:
    """
    Run the Craigslist scraper.
    """

    logger.info("=" * 70)
    logger.info("Starting Craigslist Scraper")
    logger.info("=" * 70)

    from scrapy.cmdline import execute

    scraper_dir = PROJECT_ROOT / "craigslist_scraper"

    if not scraper_dir.exists():

        raise FileNotFoundError(
            f"Craigslist scraper not found:\n{scraper_dir}"
        )

    original_directory = os.getcwd()

    try:

        os.chdir(scraper_dir)

        execute(
            [
                "scrapy",
                "crawl",
                "cl",
                "-a",
                "cities=milwaukee,columbus",
                "-a",
                "min_price=50000",
                "-a",
                "max_price=250000",
                "-o",
                str(DATA_DIR / "listings.json"),
            ]
        )

        logger.success(
            "Craigslist scraper completed successfully."
        )

    finally:

        os.chdir(original_directory)


# ==========================================================
# Facebook Automation
# ==========================================================


def run_facebook() -> None:
    """
    Run Facebook automation.
    """

    logger.info("=" * 70)
    logger.info("Starting Facebook Automation")
    logger.info("=" * 70)

    from fb_automation.playwright_runner import run

    run()

    logger.success(
        "Facebook automation completed successfully."
    )


# ==========================================================
# Menu
# ==========================================================


def menu() -> str:

    print()
    print("=" * 60)
    print(" AMAZING PROPERTIES - ASSESSMENT")
    print("=" * 60)
    print("1. Run Craigslist Scraper")
    print("2. Run Facebook Automation")
    print("3. Run Everything")
    print("4. Exit")
    print("=" * 60)

    return input(
        "Select option (1-4): "
    ).strip()


# ==========================================================
# Main
# ==========================================================


def main() -> None:

    while True:

        choice = menu()

        try:

            if choice == "1":

                run_scraper()

            elif choice == "2":

                run_facebook()

            elif choice == "3":

                run_scraper()

                run_facebook()

            elif choice == "4":

                print("\nGoodbye!\n")

                break

            else:

                print("\nInvalid option.\n")

        except KeyboardInterrupt:

            logger.warning(
                "Execution interrupted by user."
            )

            break

        except Exception as exc:

            logger.exception(exc)


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    main()