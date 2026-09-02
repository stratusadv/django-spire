from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class ShowcasePageTestCase(TestCase):
    def test_page_renders_all_choice_widgets(self) -> None:
        user = get_user_model().objects.create_superuser(username='showcase')
        self.client.force_login(user)

        response = self.client.get(reverse('showcase:page:form'))
        assert response.status_code == 200
        html = response.content.decode()

        # The adaptive field template picks one of three widget markup
        # shapes per field: a plain select (static single), a search-and-
        # select, and the multiselect used for both static and searchable
        # multiples -- its search box only renders when backend-searchable.
        assert 'adaptiveChoiceField?.choices_searchable' in html
        assert '<select' in html
        assert 'field?.selectedChoices || []' in html
        assert 'field.searchChoices(this.search.trim())' in html
        assert 'x-show="field?.choices_searchable"' in html
        assert 'type="radio"' in html
