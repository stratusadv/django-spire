from __future__ import annotations

import re

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase


class SideNavigationTemplateTestCase(BaseTestCase):
    def test_a_full_page_renders_its_navigation_links_once(self) -> None:
        html = self.client.get(reverse('home:page:home')).content.decode()

        hrefs = re.findall(r'<a\s+class="[^"]*text-link-side-navigation[^"]*"\s+href="([^"]*)"', html)

        assert hrefs
        assert len(hrefs) == len(set(hrefs))

    def test_a_navigation_link_takes_its_behaviour_from_the_side_navigation(self) -> None:
        html = self.client.get(reverse('home:page:home')).content.decode()

        assert 'x-bind="sideNavigationLink"' in html
        assert 'navLink(' not in html
        assert '@nav-redirect.window' not in html

    def test_the_mobile_menu_opens_the_side_navigation(self) -> None:
        html = self.client.get(reverse('home:page:home')).content.decode()

        assert html.count('x-data="sideNavigation()"') == 1
        assert '@click.stop="toggle_mobile_nav()"' in html
