# Playwright Tool

## Overview

A browser automation library for testing web applications with Playwright. It provides reusable library functions and a structured folder for test scripts.

### Architecture

**Library (`lib/`)**: Core functions for browser control, actions, and utilities. Import these to write your own scripts.

**Scripts (`scripts/`)**: Disposable test scripts. Write, run, modify, and keep as needed. These are scratchpad code, not reusable modules.

## File Structure

```
.opencode/tools/playwright_tool/
├── lib/                      # Core library (importable)
│   ├── __init__.py          # Exports all functions
│   ├── browser.py           # Browser management (start, close, login)
│   ├── actions.py           # Actions (goto, click, fill, etc.)
│   ├── utils.py             # Utilities (screenshot, inspect, debug)
│   └── config.py            # Configuration (URLs, credentials)
├── scripts/                  # Test scripts (scratchpad)
│   ├── login.py             # Example: Test login
│   └── check_company_user_form.py  # Example: Check company page
├── tests/                    # Test suite
│   └── test_library.py      # Library function tests
├── screenshots/              # Screenshot output
├── __init__.py              # Package exports
└── README.md                # This file
```

## Configuration

Edit `lib/config.py` to customize:

```python
BASE_URL = "http://localhost:8000"
LOGIN_URL = "/django_spire/auth/login/"
DEFAULT_TIMEOUT = 10000
SCREENSHOT_DIR = ".opencode/tools/playwright_tool/screenshots"
USERNAME = "stratus"
PASSWORD = "stratus"
```

## Library Functions

### Browser Management

```python
from lib.browser import start_browser, close_browser, login

# Start browser
p, browser, page = start_browser(headless=False)

# Login
login(page)

# Close browser
close_browser(browser, p)
```

### Actions

```python
from lib.actions import goto, click, fill, wait_for_load_state

# Navigate
goto(page, "/companies/")  # Relative URL
goto(page, "http://example.com")  # Absolute URL

# Click
click(page, "button[type=submit]")
click(page, "text=Add User")

# Fill form
fill(page, "input[name='email']", "test@example.com")
fill(page, "input[name='password']", "password123")

# Wait
wait_for_load_state(page, "networkidle")
```

### Utilities

```python
from lib.utils import (
    inspect_page,
    debug_page_state,
    take_screenshot,
    get_page_html,
    capture_console_errors,
)

# Inspect all clickable elements
inspect_page(page)

# Debug page state
debug_page_state(page, "after_login")

# Take screenshot
screenshot_path = take_screenshot(page, "my_screenshot.png")

# Get page HTML
html = get_page_html(page)

# Capture console errors
get_errors = capture_console_errors(page)
# ... do stuff ...
errors = get_errors()
```

## Writing Scripts

Scripts are disposable test code. Write them in `scripts/`, run them, modify as needed.

### Example Script

```python
# scripts/check_login.py
from __future__ import annotations
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from lib.browser import start_browser, close_browser, login
from lib.actions import goto
from lib.utils import inspect_page, take_screenshot

def main():
    p, browser, page = start_browser(headless=False)
    
    try:
        login(page)
        goto(page, "/companies/")
        inspect_page(page)
        take_screenshot(page, "companies_page.png")
    finally:
        close_browser(browser, p)

if __name__ == "__main__":
    main()
```

### Running Scripts

```bash
python .opencode/tools/playwright_tool/scripts/check_login.py
```

## Running Tests

```bash
pytest .opencode/tools/playwright_tool/tests/
```

## Known Limitations

- **No persistent state**: Each script starts fresh. Browser closes when script ends.
- **No REPL**: Interactive mode not supported. Use scripts instead.

## Related Files

- `lib/config.py` - Configuration
- `lib/browser.py` - Browser management
- `lib/actions.py` - Action functions
- `lib/utils.py` - Utility functions
