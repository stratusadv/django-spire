from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from playwright.sync_api import expect

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

RECORD_FIELD_EVENTS = """() => {
    window.field_events = [];
    for (const name of ['field-input', 'field-change', 'field-focus', 'field-blur']) {
        document.addEventListener(name, (event) => window.field_events.push({
            name,
            field: event.detail.field.name,
            value: event.detail.value,
            previous: event.detail.previousValue,
        }));
    }
}"""


def open_showcase(page: Page, demo_start: Callable[..., Demo]) -> None:
    demo_start().goto('showcase:page:form')
    page.wait_for_function('() => window.Alpine !== undefined')


def test_an_input_takes_its_name_and_state_from_its_field(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    open_showcase(page, demo_start)

    char = page.locator('input[name="char_field"]')
    expect(char).to_have_count(1)
    expect(char).to_be_enabled()
    expect(char).not_to_have_class('is-invalid')
    expect(char).to_have_class('form-control ')


def test_a_field_reports_its_focus_input_change_and_blur(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    open_showcase(page, demo_start)
    char = page.locator('input[name="char_field"]')
    initial = char.input_value()
    page.evaluate(RECORD_FIELD_EVENTS)

    char.click()
    page.keyboard.press('End')
    page.keyboard.type('Ab')
    page.locator('input[name="email_field"]').click()

    events = page.evaluate('() => window.field_events')
    char_events = [event for event in events if event['field'] == 'char_field']

    assert [event['name'] for event in char_events] == [
        'field-focus', 'field-input', 'field-input', 'field-change', 'field-blur',
    ]
    assert char_events[3]['value'] == initial + 'Ab'
    assert char_events[3]['previous'] == initial
    assert (events[-1]['name'], events[-1]['field']) == ('field-focus', 'email_field')
