from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, override_settings


def _templates_with(overrides: dict[str, str]) -> list[dict]:
    """The project's template settings, with ``overrides`` found ahead of every other template."""
    backend = {**settings.TEMPLATES[0]}
    options = {**backend.get('OPTIONS', {})}
    loaders = options.pop('loaders', None) or [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]
    options['loaders'] = [('django.template.loaders.locmem.Loader', overrides), *loaders]

    return [{**backend, 'APP_DIRS': False, 'OPTIONS': options}]


class TopNavigationButtonsTemplateTestCase(SimpleTestCase):
    def render_buttons(self) -> str:
        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        return render_to_string('django_spire/navigation/top/menu/buttons.html', {'request': request})

    def test_the_project_hook_adds_nothing_by_default(self) -> None:
        html = self.render_buttons()

        assert 'project overrides this template' not in html
        assert html.strip() == ''

    def test_a_project_adds_its_controls_ahead_of_spires(self) -> None:
        overrides = {
            'django_spire/navigation/top/menu/project_buttons.html': '<span data-company-switcher>Northwind</span>',
        }

        with override_settings(TEMPLATES=_templates_with(overrides)):
            html = self.render_buttons()

        assert html.strip().startswith('<span data-company-switcher>Northwind</span>')

    def test_the_account_menu_opens_from_a_named_button(self) -> None:
        class SignedInUser:
            is_authenticated = True
            is_superuser = False

            def get_full_name(self) -> str:
                return 'Lee Okafor'

        request = RequestFactory().get('/')
        request.user = SignedInUser()

        html = render_to_string(
            'django_spire/navigation/top/menu/buttons.html',
            {'request': request, 'user': request.user, 'hide_notification_dropdown': True},
        )

        # A button the keyboard reaches and a screen reader names, with no fixed id: the
        # template is drawn more than once on a page.
        assert 'aria-label="Account menu"' in html
        assert 'data-bs-toggle="dropdown"' in html.split('aria-label="Account menu"')[0].rsplit('<button', 1)[1]
        assert ' id="' not in html


class AsyncIconButtonTemplateTestCase(SimpleTestCase):
    def test_the_icon_is_a_button_that_awaits_its_call(self) -> None:
        html = render_to_string(
            'django_spire/button/async_icon_button.html',
            {'button_icon': 'bi bi-search', 'button_class': 'mx-1', 'x_button_click': 'Spire.searchPalette.open()'},
        )

        assert '<button' in html
        assert 'type="button"' in html
        assert 'x-bind="asyncButton(() => Spire.searchPalette.open())"' in html
        assert 'class="bi bi-search fs-2 text-primary text-primary-hover"' in html
        assert ' mx-1"' in html
