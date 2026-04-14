"""
Script: Login Test
Purpose: Test basic login functionality
"""

from __future__ import annotations
import sys
from pathlib import Path

# Add parent directory to path for imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from lib.browser import start_browser, close_browser, login
from lib.utils import inspect_page, debug_page_state, take_screenshot


def main():
    """Run login test."""
    p, browser, page = start_browser(headless=False)

    try:
        print("\n=== LOGIN TEST ===")

        # Perform login
        print("\nLogging in...")
        login(page)

        print(f"\nLogged in successfully!")
        print(f"Current URL: {page.url}")

        # Inspect the page
        inspect_page(page)

        # Debug state
        debug_page_state(page, "after_login")

        # Take screenshot
        screenshot_path = take_screenshot(page, "login_success.png")
        print(f"\nScreenshot saved: {screenshot_path}")

    finally:
        print("\nClosing browser...")
        close_browser(browser, p)


if __name__ == "__main__":
    main()
