from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from django.utils import timezone
from playwright.sync_api import expect

from test_project.app.showcase.choices import PriorityChoices
from test_project.app.showcase.tests.factories import (
    create_test_showcase_category,
    create_test_showcase_tag,
    create_test_widget_showcase,
)

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


pytestmark = pytest.mark.e2e

# One label per field, matching the auto-generated verbose name for each
# model field showcase/form/form.html renders. Covers all 29 templates under
# django_spire/core/templates/django_spire/glue/form/field/.
FIELD_LABELS = [
    'Boolean field',
    'Char field',
    'Color field',
    'Email field',
    'Password field',
    'Postal code field',
    'Search field',
    'Slug field',
    'Telephone field',
    'Url field',
    'Uuid field',
    'Select choice',
    'Radio choice',
    'Checkbox tags',
    'Search tags',
    'Category',
    'Assigned user',
    'Watchers',
    'Date field',
    'Datetime field',
    'Time field',
    'Currency field',
    'Decimal field',
    'Float field',
    'Big integer field',
    'Integer field',
    'Positive integer field',
    'Small integer field',
    'Text field',
]


def field_widget(scope: Locator | Page, label: str) -> Locator:
    """
    Scope down to a field's own widget.html div by its label text, rather
    than a bare input/select -- several widgets (search-and-select, radio,
    checkbox group) render no id on their actual input elements, only on
    individual choice items, so `get_by_label()` can't find them.
    """
    return scope.locator(
        f'xpath=.//label[.//span[normalize-space(text())="{label}"]]/parent::div'
    )


def open_showcase_form(demo, page: Page, pk: int = 0) -> None:
    if pk:
        demo.goto('showcase:page:form', pk=pk)
    else:
        demo.goto('showcase:page:form')

    page.wait_for_function('window.Glue && window.Alpine')


class TestWidgetShowcaseRenders:
    def test_every_widget_renders_with_its_label(
        self,
        page: Page,
        demo_start,
        transactional_db: None,
    ) -> None:
        """Smoke test: all 29 field templates render and are visible."""
        del transactional_db

        demo = demo_start()

        demo.title_card(
            'Every Glue Form Widget, One Page',
            kicker='django-spire',
            subtitle='One model field per template under glue/form/field/.',
        )

        open_showcase_form(demo, page)

        demo.narrate('Every field widget is present', step='1')
        for label in FIELD_LABELS:
            expect(field_widget(page, label)).to_be_visible()

        demo.spotlight(field_widget(page, 'Search tags'), label='Multi search-and-select')


def open_single_select(scope: Locator, label: str) -> Locator:
    """search_and_select_widget.html: a readonly text input opens the
    dropdown; the widget itself carries no id, so scope by label first.
    The dropdown's own search box is also input[type="text"], so .first
    is what targets the readonly trigger rather than that search box."""
    widget = field_widget(scope, label)
    widget.locator('input[type="text"]').first.click()
    return widget


def single_select_trigger(scope: Locator, label: str) -> Locator:
    return field_widget(scope, label).locator('input[type="text"]').first


def open_multi_select(scope: Locator, label: str) -> Locator:
    """multi_search_and_select_widget.html: a <button> trigger, not an
    input -- distinct from the single-select widget above."""
    widget = field_widget(scope, label)
    widget.locator('button').first.click()
    return widget


class TestWidgetShowcaseRoundTrip:
    def test_filling_every_field_type_and_saving_persists_them_all(
        self,
        page: Page,
        demo_start,
        transactional_db: None,
        django_user_model,
    ) -> None:
        """
        The showcase proof: fill one distinct value into every widget type,
        save through save_model_obj(), and confirm every field -- including
        both M2M widgets and both FK widgets -- persisted correctly.
        """
        del transactional_db

        category = create_test_showcase_category(name='Infrastructure')
        tag_alpha = create_test_showcase_tag(name='Alpha Tag')
        tag_beta = create_test_showcase_tag(name='Beta Tag')
        assignee = django_user_model.objects.create_user(username='assignee-user')
        watcher_one = django_user_model.objects.create_user(username='watcher-one')
        watcher_two = django_user_model.objects.create_user(username='watcher-two')

        demo = demo_start()

        demo.title_card(
            'Filling And Saving Every Widget',
            kicker='django-spire',
            subtitle='One save_model_obj() call round-trips all 29 field types.',
        )

        open_showcase_form(demo, page)

        demo.narrate('Filling the char-family and boolean widgets', step='1')
        demo.click(field_widget(page, 'Boolean field').locator('input[type="checkbox"]'))
        demo.fill(field_widget(page, 'Char field').locator('input'), 'Sample text')
        field_widget(page, 'Color field').locator('input').fill('#ff0000')
        demo.fill(field_widget(page, 'Email field').locator('input'), 'showcase@example.com')
        demo.fill(field_widget(page, 'Password field').locator('input'), 'sup3rSecret!')
        demo.fill(field_widget(page, 'Postal code field').locator('input'), '90210')
        demo.fill(field_widget(page, 'Search field').locator('input'), 'search term')
        demo.fill(field_widget(page, 'Slug field').locator('input'), 'my-slug-value')
        demo.fill(field_widget(page, 'Telephone field').locator('input'), '555-123-4567')
        demo.fill(field_widget(page, 'Url field').locator('input'), 'https://example.com')
        demo.fill(
            field_widget(page, 'Uuid field').locator('input'),
            '12345678-1234-5678-1234-567812345678',
        )

        demo.narrate('Filling the choice-family widgets, including both FK and M2M', step='2')
        field_widget(page, 'Select choice').locator('select').select_option(PriorityChoices.HIGH)
        demo.click(field_widget(page, 'Radio choice').get_by_label('Low'))
        demo.click(field_widget(page, 'Checkbox tags').get_by_label('Alpha Tag'))

        search_tags_widget = open_multi_select(page, 'Search tags')
        demo.click(search_tags_widget.get_by_text('Alpha Tag', exact=True))
        demo.click(search_tags_widget.get_by_text('Beta Tag', exact=True))
        # multi_search_and_select_widget.html deliberately leaves its
        # dropdown open after each pick (so several items can be added in a
        # row) -- close it before moving on, same as a real user would.
        page.keyboard.press('Escape')

        category_widget = open_single_select(page, 'Category')
        demo.click(category_widget.get_by_text('Infrastructure', exact=True))

        assigned_user_widget = open_single_select(page, 'Assigned user')
        demo.click(assigned_user_widget.get_by_text('assignee-user', exact=True))

        watchers_widget = open_multi_select(page, 'Watchers')
        demo.click(watchers_widget.get_by_text('watcher-one', exact=True))
        demo.click(watchers_widget.get_by_text('watcher-two', exact=True))
        page.keyboard.press('Escape')

        demo.narrate('Filling datetime, decimal, float, and integer widgets', step='3')
        field_widget(page, 'Date field').locator('input').fill('2027-03-15')
        field_widget(page, 'Datetime field').locator('input').fill('2027-03-15T10:30')
        field_widget(page, 'Time field').locator('input').fill('14:45')
        demo.fill(field_widget(page, 'Currency field').locator('input'), '1234.56')
        demo.fill(field_widget(page, 'Decimal field').locator('input'), '99.99')
        demo.fill(field_widget(page, 'Float field').locator('input'), '3.14')
        demo.fill(field_widget(page, 'Big integer field').locator('input'), '9999999999')
        demo.fill(field_widget(page, 'Integer field').locator('input'), '42')
        demo.fill(field_widget(page, 'Positive integer field').locator('input'), '7')
        demo.fill(field_widget(page, 'Small integer field').locator('input'), '3')
        demo.fill(field_widget(page, 'Text field').locator('textarea'), 'A longer showcase description.')

        demo.narrate('Saving redirects to the new record -- same as Deal/Task on create', step='4')
        with page.expect_navigation():
            demo.click(page.locator('button.btn-primary'))
        page.wait_for_function('window.Glue && window.Alpine')
        assert page.url.rstrip('/').split('/')[-1].isdigit(), page.url

        demo.narrate('The live panel reflects every field on the fresh page', step='5')
        live_panel = page.locator('.card', has_text='Live Model Values')

        def live_value(row_label: str) -> Locator:
            # :text-is() for an exact match on the <th> -- has_text would
            # substring-match "Integer field" inside "Big integer field".
            return live_panel.locator(f'tr:has(th:text-is("{row_label}"))').locator('td')

        expect(live_value('Char field')).to_have_text('Sample text')
        expect(live_value('Select choice')).to_have_text(PriorityChoices.HIGH)
        expect(live_value('Category')).to_have_text('Infrastructure')
        expect(live_value('Checkbox tags')).to_have_text('Alpha Tag')
        expect(live_value('Integer field')).to_have_text('42')
        demo.spotlight(live_panel, label='Live panel, post-save')

        demo.narrate('Every field persisted -- text, choice, FK, and M2M alike', step='6')
        from test_project.app.showcase.models import WidgetShowcase

        showcase = WidgetShowcase.objects.get()
        demo.spotlight(page.locator('button.btn-primary'), label='Saved')

        assert showcase.boolean_field is True
        assert showcase.char_field == 'Sample text'
        assert showcase.color_field == '#ff0000'
        assert showcase.email_field == 'showcase@example.com'
        assert showcase.password_field == 'sup3rSecret!'
        assert showcase.postal_code_field == '90210'
        assert showcase.search_field == 'search term'
        assert showcase.slug_field == 'my-slug-value'
        assert showcase.telephone_field == '555-123-4567'
        assert showcase.url_field == 'https://example.com'
        assert str(showcase.uuid_field) == '12345678-1234-5678-1234-567812345678'

        assert showcase.select_choice == PriorityChoices.HIGH
        assert showcase.radio_choice == PriorityChoices.LOW
        assert list(showcase.checkbox_tags.values_list('pk', flat=True)) == [tag_alpha.pk]
        assert set(showcase.search_tags.values_list('pk', flat=True)) == {tag_alpha.pk, tag_beta.pk}
        assert showcase.category_id == category.pk
        assert showcase.assigned_user_id == assignee.pk
        assert set(showcase.watchers.values_list('pk', flat=True)) == {watcher_one.pk, watcher_two.pk}

        assert str(showcase.date_field) == '2027-03-15'
        # datetime-local input has no timezone; the browser sends it as
        # local time, stored server-side as UTC -- compare in local time.
        assert timezone.localtime(showcase.datetime_field).strftime('%Y-%m-%dT%H:%M') == '2027-03-15T10:30'
        assert showcase.time_field.strftime('%H:%M') == '14:45'
        assert str(showcase.currency_field) == '1234.56'
        assert str(showcase.decimal_field) == '99.99'
        assert showcase.float_field == pytest.approx(3.14)
        assert showcase.big_integer_field == 9999999999
        assert showcase.integer_field == 42
        assert showcase.positive_integer_field == 7
        assert showcase.small_integer_field == 3
        assert showcase.text_field == 'A longer showcase description.'

    def test_editing_an_existing_showcase_hydrates_every_field(
        self,
        page: Page,
        demo_start,
        transactional_db: None,
        django_user_model,
    ) -> None:
        """An update form arrives with every widget already bound to server
        state, including both search-and-select widgets and the radio/
        checkbox-group widgets -- not just plain text inputs."""
        del transactional_db

        category = create_test_showcase_category(name='Operations')
        tag = create_test_showcase_tag(name='Existing Tag')
        assignee = django_user_model.objects.create_user(username='existing-assignee')

        showcase = create_test_widget_showcase(
            char_field='Already Saved',
            select_choice=PriorityChoices.LOW,
            radio_choice=PriorityChoices.HIGH,
            category=category,
            assigned_user=assignee,
            integer_field=123,
        )
        showcase.checkbox_tags.add(tag)

        demo = demo_start()

        demo.title_card(
            'Hydrating An Existing Record',
            kicker='django-spire',
            subtitle='Every widget arrives with server state already bound, not just text inputs.',
        )

        open_showcase_form(demo, page, pk=showcase.pk)

        demo.narrate('Plain, choice, and relation widgets all hydrate', step='1')
        expect(field_widget(page, 'Char field').locator('input')).to_have_value('Already Saved')
        expect(field_widget(page, 'Select choice').locator('select')).to_have_value(PriorityChoices.LOW)
        expect(field_widget(page, 'Radio choice').get_by_label('High')).to_be_checked()
        expect(field_widget(page, 'Checkbox tags').get_by_label('Existing Tag')).to_be_checked()
        expect(single_select_trigger(page, 'Category')).to_have_value('Operations')
        expect(single_select_trigger(page, 'Assigned user')).to_have_value('existing-assignee')
        demo.spotlight(field_widget(page, 'Category'), label='FK hydrated')

    def test_editing_an_existing_showcase_updates_the_live_panel_without_reloading(
        self,
        page: Page,
        demo_start,
        transactional_db: None,
    ) -> None:
        """
        The actual live-update proof: editing and saving an *existing*
        record refreshes the read-only panel in place, no page reload --
        unlike creating a brand new one, which redirects (see the fill-and-
        save test above). The panel lives in its own Alpine/Vue reactive
        scope from the editing form, so this only works because saving
        dispatches a 'widget-showcase-saved' event the panel listens for
        and reloads its own state from, rather than relying on the two
        components sharing one reactive object.
        """
        del transactional_db

        showcase = create_test_widget_showcase(char_field='Before Edit', integer_field=1)

        demo = demo_start()

        demo.title_card(
            'Live Updates, No Reload',
            kicker='django-spire',
            subtitle='Saving an existing record refreshes the read-only panel in place.',
        )

        open_showcase_form(demo, page, pk=showcase.pk)
        url_before_save = page.url

        live_panel = page.locator('.card', has_text='Live Model Values')

        def live_value(row_label: str) -> Locator:
            return live_panel.locator(f'tr:has(th:text-is("{row_label}"))').locator('td')

        demo.narrate('The panel starts showing the original values', step='1')
        expect(live_value('Char field')).to_have_text('Before Edit')
        expect(live_value('Integer field')).to_have_text('1')

        demo.narrate('Editing and saving, without navigating anywhere', step='2')
        demo.fill(field_widget(page, 'Char field').locator('input'), 'After Edit')
        demo.fill(field_widget(page, 'Integer field').locator('input'), '99')
        with page.expect_response(lambda r: '/load_state/' in r.url):
            demo.click(page.locator('button.btn-primary'))

        demo.narrate('The panel updates in place -- same URL, no reload', step='3')
        assert page.url == url_before_save
        expect(live_value('Char field')).to_have_text('After Edit')
        expect(live_value('Integer field')).to_have_text('99')
        demo.spotlight(live_panel, label='Updated without a reload')
