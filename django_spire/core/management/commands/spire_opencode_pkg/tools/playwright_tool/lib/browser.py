from __future__ import annotations
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

try:
    from .config import BASE_URL, LOGIN_URL, DEFAULT_TIMEOUT, USERNAME, PASSWORD
except ImportError:
    from config import BASE_URL, LOGIN_URL, DEFAULT_TIMEOUT, USERNAME, PASSWORD


def start_browser(headless: bool = False):
    """Start a new Playwright browser instance.

    Returns:
        Tuple of (playwright, browser, page)
    """
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=headless)
    page = browser.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT)
    return p, browser, page


def close_browser(browser, p):
    """Close the browser and stop Playwright."""
    browser.close()
    p.stop()


def login(page, username: str = None, password: str = None) -> str:
    """Login to the Django application.

    Args:
        page: Playwright page instance
        username: Username (defaults to config)
        password: Password (defaults to config)

    Returns:
        Current URL after login
    """
    if username is None:
        username = USERNAME
    if password is None:
        password = PASSWORD

    page.goto(f"{BASE_URL}{LOGIN_URL}")
    page.wait_for_load_state("domcontentloaded")

    try:
        page.locator("#djHideToolBarButton").click()
    except Exception:
        pass

    page.fill("input[name=username]", username)
    page.fill("input[name=password]", password)
    page.click("button[type=submit]")

    return page.url
