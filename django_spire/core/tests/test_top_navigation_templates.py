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


class ResponsiveIconTemplateTestCase(SimpleTestCase):
    def test_an_icon_with_a_click_shows_it_is_loading_while_the_click_runs(self) -> None:
        html = render_to_string(
            'django_spire/icon/responsive_icon.html',
            {'icon': 'bi bi-search', 'x_icon_click': 'Spire.searchPalette.open()'},
        )

        assert 'x-data="{ isLoading: false }"' in html
        assert '@click="isLoading = true; await Spire.searchPalette.open(); isLoading = false"' in html
        assert 'class="bi bi-search fs-2 text-primary text-primary-hover  cursor-pointer"' in html
        assert 'isActive' not in html
        assert '@mousedown' not in html
