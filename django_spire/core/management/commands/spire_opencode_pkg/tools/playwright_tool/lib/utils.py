from __future__ import annotations
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Page

try:
    from .config import SCREENSHOT_DIR, HTML_OUTPUT_MAX_LENGTH
except ImportError:
    from config import SCREENSHOT_DIR, HTML_OUTPUT_MAX_LENGTH


def take_screenshot(page: Page, filename: str = None) -> str:
    """Take a screenshot of the current page.

    Args:
        page: Playwright page instance
        filename: Optional filename (defaults to timestamp)

    Returns:
        Path to the saved screenshot
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"

    screenshot_path = Path(SCREENSHOT_DIR) / filename
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    page.screenshot(path=str(screenshot_path))
    return str(screenshot_path)


def inspect_page(page: Page) -> dict:
    """List all clickable elements on the page.

    Args:
        page: Playwright page instance

    Returns:
        Dict with counts of buttons, links, and inputs
    """
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
            print(f"  [{i}] {info} -> fill('{selector}', '...')")
        except Exception as e:
            print(f"  [{i}] Error: {e}")

    print(f"\n{'=' * 60}\n")

    return {"buttons": len(buttons), "links": len(links), "inputs": len(inputs)}


def debug_page_state(page: Page, step_name: str = ""):
    """Debug helper to capture page state.

    Args:
        page: Playwright page instance
        step_name: Optional label for this debug point
    """
    print(f"\n{'=' * 60}")
    print(f"DEBUG: {step_name}")
    print(f"{'=' * 60}")
    print(f"URL: {page.url}")
    print(f"Title: {page.title()}")

    inputs = page.locator("input").all()
    buttons = page.locator("button").all()
    links = page.locator("a").all()

    print(f"Elements: {len(inputs)} inputs, {len(buttons)} buttons, {len(links)} links")
    print(f"{'=' * 60}\n")


def get_page_html(page: Page, max_length: int = None) -> str:
    """Get page HTML content.

    Args:
        page: Playwright page instance
        max_length: Maximum length (defaults to config)

    Returns:
        HTML content (truncated if too long)
    """
    if max_length is None:
        max_length = HTML_OUTPUT_MAX_LENGTH

    html = page.content()
    if len(html) > max_length:
        return html[:max_length] + f"\n... (truncated, total {len(html)} chars)"
    return html


def capture_console_errors(page: Page) -> list:
    """Set up console error capture for a page.

    Args:
        page: Playwright page instance

    Returns:
        Function to retrieve captured errors
    """
    console_errors = []

    def handle_console(msg):
        if msg.type == "error":
            console_errors.append(
                {"type": msg.type, "text": msg.text, "location": msg.location}
            )

    page.on("console", handle_console)

    def get_errors():
        return console_errors

    return get_errors
