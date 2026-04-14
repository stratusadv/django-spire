from __future__ import annotations

import os
import time
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright

try:
    from .config import (
        BASE_URL,
        LOGIN_URL,
        DEFAULT_TIMEOUT,
        SCREENSHOT_DIR,
        USERNAME,
        PASSWORD,
    )
except ImportError:
    from config import (
        BASE_URL,
        LOGIN_URL,
        DEFAULT_TIMEOUT,
        SCREENSHOT_DIR,
        USERNAME,
        PASSWORD,
    )

try:
    from app.company.models import Company
    from app.company.utils import company_reverse
except ImportError:
    Company = None
    company_reverse = None


def start_browser(headless=False):
    """Start a new Playwright browser instance."""
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=headless)
    page = browser.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT)
    return p, browser, page


def close_browser(browser, p):
    """Close the browser and stop Playwright."""
    browser.close()
    p.stop()


def login(page, username=None, password=None):
    """Login to the Django application."""
    if username is None:
        username = USERNAME
    if password is None:
        password = PASSWORD

    print(f"\n{'=' * 60}")
    print("LOGIN STARTED")
    print(f"{'=' * 60}")

    page.goto(f"{BASE_URL}{LOGIN_URL}")
    page.wait_for_load_state("domcontentloaded")

    print(f"Navigated to: {page.url}")
    print(f"Page title: {page.title()}")

    try:
        page.locator("#djHideToolBarButton").click()
        print("Debug toolbar hidden")
    except Exception:
        pass

    print(f"Filling credentials for user: {username}")
    page.fill("input[name=username]", username)
    page.fill("input[name=password]", password)

    print("Submitting login form...")
    page.click("button[type=submit]")
    time.sleep(2)

    print(f"Logged in! Current URL: {page.url}")
    print(f"{'=' * 60}\n")

    return page.url


def debug_page_state(page, step_name=""):
    """Debug helper to capture page state."""
    print(f"\n{'=' * 60}")
    print(f"DEBUG: {step_name}")
    print(f"{'=' * 60}")
    print(f"URL: {page.url}")
    print(f"Title: {page.title()}")

    inputs = page.locator("input").all()
    buttons = page.locator("button").all()
    links = page.locator("a").all()

    print(f"Elements: {len(inputs)} inputs, {len(buttons)} buttons, {len(links)} links")

    if inputs:
        print("\nInputs:")
        for i, inp in enumerate(inputs[:10]):
            try:
                name = inp.get_attribute("name")
                inp_type = inp.get_attribute("type")
                inp_id = inp.get_attribute("id")
                if name or inp_id:
                    print(f"  - name={name}, type={inp_type}, id={inp_id}")
            except Exception:
                pass

    if buttons:
        print("\nButtons:")
        for i, btn in enumerate(buttons[:10]):
            try:
                text = btn.inner_text()[:30]
                btn_id = btn.get_attribute("id")
                btn_class = btn.get_attribute("class")
                if text or btn_id:
                    print(f"  - '{text}' (id={btn_id}, class={btn_class})")
            except Exception:
                pass

    if links:
        print("\nLinks:")
        for i, link in enumerate(links[:10]):
            try:
                text = link.inner_text()[:30]
                href = link.get_attribute("href")
                if text or href:
                    print(f"  - '{text}' (href={href})")
            except Exception:
                pass

    print(f"{'=' * 60}\n")


def take_screenshot(page, filename=None):
    """Take a screenshot of the current page."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"

    screenshot_path = Path(SCREENSHOT_DIR) / filename
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    page.screenshot(path=str(screenshot_path))
    print(f"Screenshot saved: {screenshot_path}")
    return str(screenshot_path)


def inspect_page(page):
    """List all clickable elements on the page for easy selection."""
    print(f"\n{'=' * 60}")
    print("PAGE INSPECTION")
    print(f"{'=' * 60}")
    print(f"URL: {page.url}")
    print(f"Title: {page.title()}")

    buttons = page.locator("button").all()
    links = page.locator("a").all()
    inputs = page.locator("input").all()

    print(f"\n=== BUTTONS ({len(buttons)}) ===")
    for i, btn in enumerate(buttons):
        try:
            text = btn.inner_text().strip()[:50]
            btn_id = btn.get_attribute("id")
            btn_class = btn.get_attribute("class")
            selector = (
                f"#{btn_id}"
                if btn_id
                else f".{btn_class.split()[0]}"
                if btn_class
                else f"button:nth({i})"
            )
            if text:
                print(f"  [{i}] '{text}' -> click('{selector}')")
            else:
                print(f"  [{i}] (empty) -> click('{selector}')")
        except Exception as e:
            print(f"  [{i}] Error: {e}")

    print(f"\n=== LINKS ({len(links)}) ===")
    for i, link in enumerate(links):
        try:
            text = link.inner_text().strip()[:50]
            href = link.get_attribute("href")
            link_id = link.get_attribute("id")
            selector = (
                f"#{link_id}"
                if link_id
                else f"a[href='{href}']"
                if href
                else f"a:nth({i})"
            )
            if text:
                print(f"  [{i}] '{text}' -> goto/link('{selector}')")
            elif href:
                print(f"  [{i}] href='{href}' -> goto/link('{selector}')")
        except Exception as e:
            print(f"  [{i}] Error: {e}")

    print(f"\n=== INPUTS ({len(inputs)}) ===")
    for i, inp in enumerate(inputs):
        try:
            name = inp.get_attribute("name")
            inp_id = inp.get_attribute("id")
            inp_type = inp.get_attribute("type")
            placeholder = inp.get_attribute("placeholder")
            label = None
            try:
                label = inp.locator("preceding::label").first.inner_text()
            except Exception:
                pass

            selector = (
                f"#{inp_id}"
                if inp_id
                else f"[name='{name}']"
                if name
                else f"input:nth({i})"
            )
            info = f"type={inp_type}"
            if placeholder:
                info += f", placeholder='{placeholder}'"
            if label:
                info += f", label='{label}'"

            print(f"  [{i}] {info} -> fill('{selector}', '...')")
        except Exception as e:
            print(f"  [{i}] Error: {e}")

    print(f"\n{'=' * 60}\n")

    return {"buttons": len(buttons), "links": len(links), "inputs": len(inputs)}


def get_page_html(page, max_length=None):
    """Get page HTML content."""
    from .config import HTML_OUTPUT_MAX_LENGTH

    if max_length is None:
        max_length = HTML_OUTPUT_MAX_LENGTH

    html = page.content()
    if len(html) > max_length:
        return html[:max_length] + f"\n... (truncated, total {len(html)} chars)"
    return html
