---
name: playwright_tool
description: Browser automation library with reusable functions and test scripts
---

# Playwright Tool

## Overview

The Playwright Tool provides a browser automation library for testing web applications. It consists of reusable library functions and a structured folder for disposable test scripts.

### Key Principles
- **Library + Scripts Pattern**: Library provides building blocks, scripts are disposable test code
- **No Persistent State**: Each script starts fresh, browser closes when script ends
- **Absolute Imports**: Scripts import from library using absolute paths
- **Script Discovery**: Scripts live in `scripts/` folder with descriptive names

## Core Architecture

### File Structure

```
.opencode/tools/playwright_tool/
├── lib/                      # Core library (importable)
│   ├── __init__.py          # Exports all functions
│   ├── browser.py           # Browser management
│   ├── actions.py           # Action functions
│   ├── utils.py             # Utility functions
│   └── config.py            # Configuration
├── scripts/                  # Test scripts (scratchpad)
│   ├── login.py
│   └── check_company_user_form.py
├── tests/                    # Test suite
├── screenshots/              # Screenshot output
└── README.md                # Usage documentation
```

### Library Functions

**Browser Management** (`lib/browser.py`):
- `start_browser(headless=False)` - Start browser, returns (p, browser, page)
- `close_browser(browser, p)` - Close browser and stop Playwright
- `login(page, username, password)` - Login to Django application

**Actions** (`lib/actions.py`):
- `goto(page, url)` - Navigate to URL (relative or absolute)
- `click(page, selector)` - Click element
- `fill(page, selector, value)` - Fill input field
- `check(page, selector)` - Check checkbox/radio
- `uncheck(page, selector)` - Uncheck checkbox
- `select(page, selector, value)` - Select dropdown option
- `hover(page, selector)` - Hover over element
- `press(page, selector, key)` - Press key on element
- `wait_for_load_state(page, state)` - Wait for load state
- `wait_for_selector(page, selector, timeout)` - Wait for element

**Utilities** (`lib/utils.py`):
- `take_screenshot(page, filename)` - Take screenshot
- `inspect_page(page)` - List all clickable elements
- `debug_page_state(page, step_name)` - Debug page state
- `get_page_html(page, max_length)` - Get page HTML
- `capture_console_errors(page)` - Set up console error capture

## Implementation Guide

### Writing Scripts

Scripts are disposable test code. Write them in `scripts/`, run them, modify as needed.

**DON'T**: Create reusable modules or import scripts into other code

```python
# ❌ DON'T: Importing scripts as modules
from scripts.login import main
main()  # Scripts are not meant to be imported
```

**DO**: Write self-contained scripts that use library functions

```python
# ✅ DO: Self-contained script using library
from __future__ import annotations
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from lib.browser import start_browser, close_browser, login
from lib.actions import goto, click
from lib.utils import inspect_page, take_screenshot

def main():
    p, browser, page = start_browser(headless=False)
    
    try:
        login(page)
        goto(page, "/companies/")
        inspect_page(page)
        take_screenshot(page, "companies.png")
    finally:
        close_browser(browser, p)

if __name__ == "__main__":
    main()
```

### Running Scripts

Execute scripts directly with Python:

```bash
python .opencode/tools/playwright_tool/scripts/login.py
```

### Configuration

Edit `lib/config.py` to customize settings:

```python
BASE_URL = "http://localhost:8000"
LOGIN_URL = "/django_spire/auth/login/"
DEFAULT_TIMEOUT = 10000
SCREENSHOT_DIR = ".opencode/tools/playwright_tool/screenshots"
USERNAME = "stratus"
PASSWORD = "stratus"
```

### Example: Complete Workflow

```python
# scripts/check_user_form.py
from __future__ import annotations
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from lib.browser import start_browser, close_browser, login
from lib.actions import goto
from lib.utils import (
    inspect_page,
    debug_page_state,
    take_screenshot,
    capture_console_errors,
)

def main():
    p, browser, page = start_browser(headless=False)
    get_errors = capture_console_errors(page)
    
    try:
        # Login
        login(page)
        
        # Navigate to company page
        goto(page, "/django_spire/companies/")
        
        # Inspect page
        inspect_page(page)
        
        # Debug state
        debug_page_state(page, "company_list")
        
        # Take screenshot
        take_screenshot(page, "company_page.png")
        
        # Check console errors
        errors = get_errors()
        print(f"Console errors: {len(errors)}")
        for err in errors:
            print(f"  - {err['text']}")
            
    finally:
        close_browser(browser, p)

if __name__ == "__main__":
    main()
```

## Code Review Checklist

When reviewing Playwright scripts, verify the following:

1. **Absolute Imports**: Verify scripts use absolute imports from `lib/`, not relative imports
2. **Self-Contained**: Confirm scripts are standalone and not imported by other code
3. **Proper Cleanup**: Check that `close_browser()` is called in `finally` block
4. **Error Capture**: Verify `capture_console_errors()` is used for debugging
5. **Screenshots**: Confirm screenshots are taken at key workflow steps
6. **Descriptive Names**: Scripts should have descriptive names (not `test.py`, `temp.py`)
7. **No Hardcoded URLs**: Use `BASE_URL` from config, not hardcoded URLs
8. **Headless Mode**: Scripts should default to `headless=False` for debugging
9. **Wait States**: Verify `wait_for_load_state()` is called after navigation
10. **Selectors**: Prefer specific selectors (`text=`, `#id`, `[name='field']`) over generic ones

## Known Limitations

- **No Persistent State**: Browser closes when script ends. Cannot maintain state across scripts.
- **No Interactive Mode**: REPL/interactive mode not supported. Use scripts instead.
- **Sequential Execution**: Scripts run sequentially, not in parallel.

## Related Skills

- [python-style](../python-style/SKILL.md) - Python coding standards
- [testing](../testing/SKILL.md) - Django testing best practices
