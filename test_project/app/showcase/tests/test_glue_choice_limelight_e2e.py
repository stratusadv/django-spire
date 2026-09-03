from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from test_project.app.showcase.choices import PriorityChoices
from test_project.app.showcase.tests.factories import (
    create_test_showcase_category,
    create_test_showcase_tag,
)

from test_project.app.showcase.tests.test_e2e import (
    choose_multi_search,
    choose_multi_static,
    choose_single_search,
    field_widget,
    single_select_trigger,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Locator, Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]


def test_adaptive_choice_widgets_demo(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    """
    The adaptive choice template picks a widget from field metadata alone:
    static single, searchable single, or the multiselect (which gains a
    search box only when the field is backend-searchable). This walkthrough
    proves all of them on the Widget Showcase page, plus the two behaviors
    that make backend-searchable sources worth the round trip: a selection
    keeps its rich label when the search is cleared, and a query can match a
    secondary search field even when the result's label does not contain the
    query.
    """
    del transactional_db

    create_test_showcase_category(name='Infrastructure')
    create_test_showcase_tag(name='Alpha Tag')
    create_test_showcase_tag(name='Beta Tag')
    # `quill` is found by searching its first name only -- its label
    # (the username) does not contain the query.
    get_user_model().objects.create_user(
        username='quill', first_name='Zephyr', last_name='Kestrel', email='quill@example.com'
    )

    demo = demo_start()

    demo.goto('showcase:page:form')
    expect(page.get_by_role('heading', name='Widget Showcase')).to_be_visible()
    page.wait_for_function('window.Glue && window.Alpine')

    demo.title(
        'Adaptive Choice Widgets',
        kicker='django-spire',
        subtitle='One template, four widgets -- chosen from field metadata alone.',
    )

    demo.narrate('Static single choice renders a native select', step='1')
    single_static = field_widget(page, 'Select choice').locator('select')
    expect(single_static).to_be_visible()
    expect(single_static.locator('option')).to_have_text(['Low', 'Medium', 'High'])
    demo.select(single_static, 'High')
    expect(single_static).to_have_value(PriorityChoices.HIGH)

    demo.narrate('Static multiple choice renders a non-searchable multiselect', step='2')
    checkbox_tags_widget = choose_multi_static(page, 'Checkbox tags', 'Alpha Tag')
    choose_multi_static(page, 'Checkbox tags', 'Beta Tag')
    expect(checkbox_tags_widget.locator('button.form-control .badge')).to_have_text(
        ['Alpha Tag', 'Beta Tag']
    )

    demo.narrate('Searchable single choice runs a backend search', step='3')
    choose_single_search(page, 'Category', 'Infra', 'Infrastructure')
    expect(single_select_trigger(page, 'Category')).to_have_value('Infrastructure')

    demo.narrate('Searchable multiple choice keeps every selected label', step='4')
    search_tags_widget = choose_multi_search(page, 'Search tags', 'Alpha', 'Alpha Tag')
    choose_multi_search(page, 'Search tags', 'Beta', 'Beta Tag')
    selected_badges: Locator = search_tags_widget.locator('button.form-control .badge')
    expect(selected_badges).to_have_text(['Alpha Tag', 'Beta Tag'])

    demo.narrate('A secondary search field matches a row its label omits', step='5')
    assigned = field_widget(page, 'Assigned user')
    assigned.locator('input[type="text"]').first.click()
    assigned.locator('input.form-control-sm').fill('Zephyr')
    quill_result = assigned.locator('.list-group-item', has_text='quill')
    expect(quill_result).to_be_visible()
    expect(quill_result).to_have_text('quill')
    quill_result.click()

    demo.narrate('The selected rich label survives the cleared search', step='6')
    expect(single_select_trigger(page, 'Assigned user')).to_have_value('quill')
    demo.spotlight(field_widget(page, 'Assigned user'), label='Retained after search clears')
