from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from playwright.sync_api import expect

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

ECHARTS = 'script[src*="echarts"]'


def test_a_page_with_charts_loads_echarts_once_and_draws_each_chart(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    demo_start().goto('home:page:chart_demo')

    charts = page.locator('[x-data="spireChart()"]')
    expect(charts).to_have_count(4)

    for index in range(4):
        expect(charts.nth(index).locator('canvas')).to_have_count(1)

    expect(page.locator(ECHARTS)).to_have_count(1)


def test_a_page_without_charts_does_not_load_echarts(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    demo_start().goto('home:page:home')
    page.wait_for_function('() => window.Alpine !== undefined')
    page.wait_for_load_state('networkidle')

    expect(page.locator(ECHARTS)).to_have_count(0)
    assert page.evaluate('() => window.echarts === undefined')
