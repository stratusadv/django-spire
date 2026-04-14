from __future__ import annotations
from playwright.sync_api import Page

try:
    from .config import BASE_URL
except ImportError:
    from config import BASE_URL


def goto(page: Page, url: str) -> str:
    """Navigate to a URL.

    Args:
        page: Playwright page instance
        url: URL to navigate to (can be relative or absolute)

    Returns:
        Current URL after navigation
    """
    if not url.startswith("http"):
        url = BASE_URL + url
    page.goto(url)
    return page.url


def click(page: Page, selector: str):
    """Click an element.

    Args:
        page: Playwright page instance
        selector: CSS selector or text selector
    """
    page.click(selector)


def fill(page: Page, selector: str, value: str):
    """Fill an input field.

    Args:
        page: Playwright page instance
        selector: CSS selector for the input
        value: Value to fill
    """
    page.fill(selector, value)


def check(page: Page, selector: str):
    """Check a checkbox or radio button.

    Args:
        page: Playwright page instance
        selector: CSS selector for the input
    """
    page.check(selector)


def uncheck(page: Page, selector: str):
    """Uncheck a checkbox.

    Args:
        page: Playwright page instance
        selector: CSS selector for the input
    """
    page.uncheck(selector)


def select(page: Page, selector: str, value: str):
    """Select an option in a dropdown.

    Args:
        page: Playwright page instance
        selector: CSS selector for the select element
        value: Option value to select
    """
    page.select_option(selector, value)


def hover(page: Page, selector: str):
    """Hover over an element.

    Args:
        page: Playwright page instance
        selector: CSS selector for the element
    """
    page.hover(selector)


def press(page: Page, selector: str, key: str):
    """Press a key on an element.

    Args:
        page: Playwright page instance
        selector: CSS selector for the element
        key: Key to press (e.g., 'Enter', 'Tab')
    """
    page.press(selector, key)


def wait_for_load_state(page: Page, state: str = "domcontentloaded"):
    """Wait for page load state.

    Args:
        page: Playwright page instance
        state: Load state to wait for
    """
    page.wait_for_load_state(state)


def wait_for_selector(page: Page, selector: str, timeout: int = None):
    """Wait for an element to appear.

    Args:
        page: Playwright page instance
        selector: CSS selector to wait for
        timeout: Timeout in milliseconds (optional)
    """
    if timeout:
        page.wait_for_selector(selector, timeout=timeout)
    else:
        page.wait_for_selector(selector)
