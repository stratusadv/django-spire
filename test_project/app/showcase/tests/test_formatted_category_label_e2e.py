from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from playwright.sync_api import expect

from test_project.app.showcase.tests.factories import create_test_showcase_category
from test_project.app.showcase.tests.test_e2e import field_widget, single_select_trigger

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]


def test_formatted_category_label_html_demo(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    """
    A choices source configured with a label_formatter (see
    WidgetShowcaseForm.formatted_category) serves pre-rendered HTML labels.
    This walkthrough proves both halves of the client contract: the
    dropdown renders the label as real markup, and the selected trigger
    shows its plain text form.
    """
    del transactional_db

    create_test_showcase_category(name='Infrastructure')

    demo = demo_start()
    demo.goto('showcase:page:form')
    expect(page.get_by_role('heading', name='Widget Showcase')).to_be_visible()
    page.wait_for_function('window.Glue && window.Alpine')

    demo.narrate('The formatted source renders its choice label as HTML', step='1')
    widget = field_widget(page, 'Formatted category')
    widget.locator('input[type="text"]').first.click()
    item = widget.locator('.list-group-item', has_text='Infrastructure')
    expect(item).to_be_visible()
    expect(item.locator('b')).to_have_text('Infrastructure')

    demo.narrate('The selected trigger keeps the plain text form', step='2')
    item.click()
    expect(single_select_trigger(page, 'Formatted category')).to_have_value(
        'Infrastructure (formatted label)'
    )
    demo.spotlight(widget, label='HTML label, plain trigger')
