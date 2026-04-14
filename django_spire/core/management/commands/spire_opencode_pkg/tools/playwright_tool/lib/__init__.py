"""
Playwright Tool Library

Core library functions for browser automation.
"""

from .browser import start_browser, close_browser, login
from .actions import (
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
)
from .utils import (
    take_screenshot,
    inspect_page,
    debug_page_state,
    get_page_html,
    capture_console_errors,
)

__all__ = [
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
