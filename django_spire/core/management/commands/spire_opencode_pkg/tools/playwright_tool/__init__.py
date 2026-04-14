"""
Playwright Tool

A browser automation library for testing web applications with Playwright.

Usage:
    # Import library functions
    from opencode.tools.playwright_tool.lib import (
        start_browser, close_browser, login,
        goto, click, fill,
        inspect_page, take_screenshot, debug_page_state
    )

    # Write scripts in scripts/ folder
    # Run scripts directly: python scripts/login.py
"""

from .config import (
    BASE_URL,
    LOGIN_URL,
    DEFAULT_TIMEOUT,
    SCREENSHOT_DIR,
    USERNAME,
    PASSWORD,
)
from .lib import (
    start_browser,
    close_browser,
    login,
    goto,
    click,
    fill,
    check,
    uncheck,
    select,
    hover,
    press,
    wait_for_load_state,
    wait_for_selector,
    take_screenshot,
    inspect_page,
    debug_page_state,
    get_page_html,
    capture_console_errors,
)

__all__ = [
    # Config
    "BASE_URL",
    "LOGIN_URL",
    "DEFAULT_TIMEOUT",
    "SCREENSHOT_DIR",
    "USERNAME",
    "PASSWORD",
    # Browser management
    "start_browser",
    "close_browser",
    "login",
    # Actions
    "goto",
    "click",
    "fill",
    "check",
    "uncheck",
    "select",
    "hover",
    "press",
    "wait_for_load_state",
    "wait_for_selector",
    # Utilities
    "take_screenshot",
    "inspect_page",
    "debug_page_state",
    "get_page_html",
    "capture_console_errors",
]
