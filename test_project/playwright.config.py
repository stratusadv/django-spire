from __future__ import annotations

import os


BASE_URL = os.getenv('PLAYWRIGHT_BASE_URL', 'http://localhost:8000')


def pytest_configure(config) -> None:
    config.addinivalue_line(
        'markers',
        'playwright: mark test as a playwright test'
    )
