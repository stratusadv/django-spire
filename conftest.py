from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

import pytest

if TYPE_CHECKING:
    from playwright.sync_api import Route


pytest_plugins = ['django_spire.testing.playwright.fixtures', 'limelight.pytest_plugin']

VENDOR_ASSETS = {
    '/npm/bootstrap-icons@1.13.x/font/bootstrap-icons.min.css': (
        'bootstrap-icons/bootstrap-icons.min.css'
    ),
    '/npm/bootstrap-icons@1.13.x/font/fonts/bootstrap-icons.woff': (
        'bootstrap-icons/fonts/bootstrap-icons.woff'
    ),
    '/npm/bootstrap-icons@1.13.x/font/fonts/bootstrap-icons.woff2': (
        'bootstrap-icons/fonts/bootstrap-icons.woff2'
    ),
    '/npm/echarts@6.1.0/dist/echarts.min.js': 'echarts/echarts.min.js',
    '/ajax/libs/pulltorefreshjs/0.1.22/index.umd.min.js': 'pulltorefreshjs/index.umd.min.js',
    '/npm/@alpinejs/intersect@3.15.x/dist/cdn.min.js': 'alpinejs/intersect.min.js',
    '/npm/@alpinejs/mask@3.15.x/dist/cdn.min.js': 'alpinejs/mask.min.js',
    '/npm/@alpinejs/collapse@3.15.x/dist/cdn.min.js': 'alpinejs/collapse.min.js',
    '/npm/@alpinejs/persist@3.15.x/dist/cdn.min.js': 'alpinejs/persist.min.js',
    '/npm/@alpinejs/focus@3.15.x/dist/cdn.min.js': 'alpinejs/focus.min.js',
    '/npm/@alpinejs/sort@3.15.x/dist/cdn.min.js': 'alpinejs/sort.min.js',
    '/npm/bootstrap@5.3.x/dist/js/bootstrap.bundle.min.js': 'bootstrap/bootstrap.bundle.min.js',
}


@pytest.fixture(autouse=True)
def use_vendored_assets_for_e2e(request: pytest.FixtureRequest) -> None:
    if request.node.get_closest_marker('e2e') is None:
        return

    page = request.getfixturevalue('page')
    vendor_root = Path(__file__).parent / 'test_project/vendor'

    def serve_asset(route: Route) -> None:
        relative_path = VENDOR_ASSETS.get(urlsplit(route.request.url).path)
        if relative_path is None:
            route.abort()
            return

        route.fulfill(path=vendor_root / relative_path)

    page.route('https://**', serve_asset)
