from __future__ import annotations

import base64
import re

import pytest

from typing import TYPE_CHECKING

from playwright.sync_api import expect

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

PIXEL = {
    'name': 'pixel.png',
    'mimeType': 'image/png',
    'buffer': base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    ),
}
IMAGE_DATA_URL = re.compile(r'^data:image/png;base64,')


def open_file_form(page: Page, demo_start: Callable[..., Demo]) -> list[str]:
    errors = []
    page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
    page.on('pageerror', lambda error: errors.append(str(error)))

    demo_start().goto('file:form:create')
    page.wait_for_function('() => window.Alpine !== undefined')

    return errors


def test_the_single_file_field_previews_and_clears_an_image(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    errors = open_file_form(page, demo_start)
    field = page.locator('[x-data="glueSingleFileField()"]')

    field.locator('input[type="file"]').set_input_files(PIXEL)

    preview = field.locator('img')
    expect(preview).to_be_visible()
    expect(preview).to_have_attribute('src', IMAGE_DATA_URL)

    field.locator('button').click()

    expect(preview).to_be_hidden()
    assert errors == []


def test_the_multi_file_field_previews_and_removes_an_image(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    errors = open_file_form(page, demo_start)
    field = page.locator('[x-data^="glueMultiFileField("]')

    field.locator('input[type="file"]').set_input_files(PIXEL)
    field.locator('button.form-control').click()

    expect(field.locator('.badge')).to_have_text('pixel.png')
    expect(field.locator('.list-group img')).to_have_attribute('src', IMAGE_DATA_URL)

    # The development toolbar's overlay sits over the icon at this viewport.
    field.locator('.bi-trash').dispatch_event('click')

    expect(field.locator('.badge')).to_have_count(0)
    assert errors == []


def test_focus_moving_inside_a_field_is_neither_a_focus_nor_a_blur(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    open_file_form(page, demo_start)
    field = page.locator('[x-data="glueSingleFileField()"]')
    file_input = field.locator('input[type="file"]')

    file_input.set_input_files(PIXEL)
    clear = field.locator('button')
    expect(clear).to_be_visible()

    file_input.focus()
    page.evaluate("""() => {
        window.field_events = [];
        for (const name of ['field-focus', 'field-blur']) {
            document.addEventListener(name, () => window.field_events.push(name));
        }
    }""")
    clear.focus()

    assert page.evaluate('() => window.field_events') == []
