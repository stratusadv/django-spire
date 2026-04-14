"""
Tests for the Playwright tool library.

These tests verify that the library functions work correctly.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from ..lib.browser import start_browser, close_browser, login
from ..lib.actions import goto, click, fill, wait_for_load_state
from ..lib.utils import (
    debug_page_state,
    take_screenshot,
    inspect_page,
    get_page_html,
    capture_console_errors,
)
from ..config import BASE_URL, LOGIN_URL


class TestPlaywrightLibrary:
    """Test suite for Playwright library functions."""

    @pytest.fixture
    def browser_setup(self):
        """Set up and tear down browser for tests."""
        p, browser, page = start_browser(headless=True)
        yield p, browser, page
        close_browser(browser, p)

    def test_start_browser_returns_valid_objects(self, browser_setup):
        """Test that start_browser returns valid browser and page objects."""
        p, browser, page = browser_setup
        assert p is not None
        assert browser is not None
        assert page is not None
        assert browser.is_connected()

    def test_login_success(self, browser_setup):
        """Test that login function successfully logs in."""
        p, browser, page = browser_setup

        url = login(page)

        assert url is not None
        assert BASE_URL in url
        assert LOGIN_URL not in url or "login" not in page.url.lower()

    def test_goto_absolute_url(self, browser_setup):
        """Test navigation with absolute URL."""
        p, browser, page = browser_setup

        login(page)
        result_url = goto(page, f"{BASE_URL}{LOGIN_URL}")

        assert result_url == f"{BASE_URL}{LOGIN_URL}"
        assert page.url == result_url

    def test_goto_relative_url(self, browser_setup):
        """Test navigation with relative URL."""
        p, browser, page = browser_setup

        login(page)
        result_url = goto(page, LOGIN_URL)

        assert result_url == f"{BASE_URL}{LOGIN_URL}"
        assert page.url == result_url

    def test_debug_page_state_output(self, browser_setup, capsys):
        """Test that debug_page_state produces output."""
        p, browser, page = browser_setup

        login(page)
        debug_page_state(page, "test_debug")

        captured = capsys.readouterr()
        assert "URL:" in captured.out
        assert "Title:" in captured.out
        assert "Elements:" in captured.out

    def test_inspect_page_output(self, browser_setup, capsys):
        """Test that inspect_page lists elements."""
        p, browser, page = browser_setup

        login(page)
        result = inspect_page(page)

        captured = capsys.readouterr()
        assert "PAGE INSPECTION" in captured.out
        assert "BUTTONS" in captured.out
        assert "LINKS" in captured.out
        assert "INPUTS" in captured.out
        assert isinstance(result, dict)
        assert "buttons" in result
        assert "links" in result
        assert "inputs" in result

    def test_take_screenshot(self, browser_setup):
        """Test that screenshot is saved."""
        p, browser, page = browser_setup

        login(page)
        screenshot_path = take_screenshot(page, "test_screenshot.png")

        assert screenshot_path is not None
        assert Path(screenshot_path).exists()

    def test_get_page_html(self, browser_setup):
        """Test that get_page_html returns HTML content."""
        p, browser, page = browser_setup

        login(page)
        html = get_page_html(page)

        assert html is not None
        assert len(html) > 0
        assert "<html" in html.lower() or "<!doctype" in html.lower()

    def test_get_page_html_truncation(self, browser_setup):
        """Test that get_page_html truncates long content."""
        p, browser, page = browser_setup

        login(page)
        html = get_page_html(page, max_length=100)

        assert len(html) <= 100 + 50
        assert "truncated" in html or len(html) < 1000

    def test_capture_console_errors(self, browser_setup):
        """Test that console error capture works."""
        p, browser, page = browser_setup

        get_errors = capture_console_errors(page)
        login(page)

        errors = get_errors()
        assert isinstance(errors, list)

    def test_close_browser(self):
        """Test that close_browser properly closes the browser."""
        p, browser, page = start_browser(headless=True)

        assert browser.is_connected()

        close_browser(browser, p)

        assert not browser.is_connected()
