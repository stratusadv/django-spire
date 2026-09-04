from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from playwright.sync_api import expect

from test_project.app.showcase.models import WidgetShowcase
from test_project.app.showcase.tests.factories import create_test_showcase_category
from test_project.app.showcase.tests.test_e2e import field_widget, open_showcase_form

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]


class TestSelectWidgetDefaultChoiceValue:
    """
    Regression coverage for select_widget.html's applyDefaultChoice() fix.

    Without an empty placeholder option, a plain <select> (a single relation
    field with choices_searchable false -- see adaptive_field.html) still
    visually shows its first <option> once choices load, purely as native
    browser fallback: nothing is marked `selected`, so no `change` event ever
    fires and Alpine's own `value` (the actual bound field) stayed null. The
    dropdown looked filled in but submitting reported the field as required --
    exactly what StatisticGroupForm.domain hit in stratusadv-portal, which is
    what 'Primary category' here stands in for.
    """

    def test_only_choice_is_committed_as_a_real_value_not_just_shown(
        self, page: Page, demo_start: Callable[..., Demo], transactional_db: None
    ) -> None:
        """The field's own bound value -- not just the <select>'s DOM display
        -- must already hold the one available choice before any user
        interaction, so a plain `field.choices[0]` read proves the fix rather
        than the browser's fallback rendering.
        """
        del transactional_db

        category = create_test_showcase_category(name='Only Category')

        demo = demo_start()
        demo.title(
            'A Visually-Filled Select Is A Really-Filled Select',
            kicker='django-spire',
            subtitle='select_widget.html commits the shown default into the real field value.',
        )

        open_showcase_form(demo, page)

        demo.narrate('The only choice appears in the dropdown, unopened and untouched', step='1')
        select = field_widget(page, 'Primary category').locator('select')
        expect(select).to_have_value(str(category.pk))

        demo.narrate('That is a real Alpine-bound value, not a DOM-only default', step='2')
        bound_value = select.evaluate(
            """
            el => {
                const scope = Alpine.$data(el)
                return scope.value
            }
            """
        )
        assert str(bound_value) == str(category.pk)

    def test_submitting_without_touching_the_field_still_saves_it(
        self, page: Page, demo_start: Callable[..., Demo], transactional_db: None
    ) -> None:
        """The end-to-end proof: a required select_widget.html field with one
        available choice, never clicked, must not block submission -- it did
        before the fix (`clean_data` came back with no domain/category at
        all, "This field is required").
        """
        del transactional_db

        category = create_test_showcase_category(name='Uncontested Category')

        demo = demo_start()
        open_showcase_form(demo, page)

        demo.narrate('Filling only the other required fields', step='1')
        demo.fill(field_widget(page, 'Char field').locator('input'), 'Default Choice Save')

        demo.narrate('Submitting without ever touching Primary category', step='2')
        with page.expect_navigation():
            demo.click(page.locator('button.btn-primary'))
        page.wait_for_function('window.Glue && window.Alpine')

        demo.narrate('It saved -- no "this field is required" error, no redirect back', step='3')
        showcase = WidgetShowcase.objects.get(char_field='Default Choice Save')
        assert showcase.primary_category_id == category.pk
        demo.spotlight(field_widget(page, 'Primary category'), label='Saved without a click')

    def test_editing_an_existing_choice_is_left_alone(
        self, page: Page, demo_start: Callable[..., Demo], transactional_db: None
    ) -> None:
        """The fix only fills in a *missing* value -- it must never override
        an already-bound one, e.g. an existing record being edited, even
        when other choices exist and would otherwise be `choices[0]`.
        """
        del transactional_db

        # Alphabetically first, but must lose to the real bound value below.
        create_test_showcase_category(name='Alpha Category')
        chosen = create_test_showcase_category(name='Zulu Category')

        showcase = WidgetShowcase.objects.create(
            char_field='Existing', primary_category=chosen
        )

        demo = demo_start()
        open_showcase_form(demo, page, pk=showcase.pk)

        demo.narrate('The existing selection is shown, not the alphabetically-first one', step='1')
        select = field_widget(page, 'Primary category').locator('select')
        expect(select).to_have_value(str(chosen.pk))
