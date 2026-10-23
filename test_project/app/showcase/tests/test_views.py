from __future__ import annotations

from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.staticfiles import finders
from django.test import RequestFactory, TestCase
from django.urls import reverse

from django_glue.glue.options.django.choices import GlueRelatedModelChoices

from test_project.app.showcase.forms import WidgetShowcaseForm
from test_project.app.showcase.models import ShowcaseCategory


class ShowcasePageTestCase(TestCase):
    def test_page_renders_all_choice_widgets(self) -> None:
        user = get_user_model().objects.create_superuser(username='showcase')
        self.client.force_login(user)

        response = self.client.get(reverse('showcase:page:form'))
        assert response.status_code == 200
        html = response.content.decode()
        search_js = Path(finders.find('django_spire/js/search_and_select.js')).read_text()
        multi_js = Path(finders.find('django_spire/js/multi_search_and_select.js')).read_text()

        # The adaptive field template picks one of three widget markup shapes
        # per field: a plain select (static single), a search-and-select, and
        # the multiselect (both static and searchable multiples). The widget
        # logic (backend search + static local filter) lives in the Alpine
        # component files that the templates reference via x-data.
        assert 'adaptiveChoiceField?.choices_searchable' in html
        assert '<select' in html
        assert 'x-data="searchAndSelect(field' in html
        assert 'x-data="multiSearchAndSelect(field)"' in html
        assert 'glueField?.selectedChoices || []' in multi_js
        assert 'glueField.searchChoices(this.search.trim())' in multi_js
        assert 'String(choice.label).toLowerCase().includes(query)' in search_js
        assert 'type="radio"' in html


class FormattedCategoryChoicesTestCase(TestCase):
    def test_formatted_category_choices_carry_formatted_html_label(self) -> None:
        ShowcaseCategory.objects.create(name='Grappling')
        field = WidgetShowcaseForm().fields['formatted_category']

        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        result = GlueRelatedModelChoices(field.queryset).load(
            search='', request=request
        )

        assert result['results'][0]['label'] == (
            '<b>Grappling</b> <span class="text-body-secondary small">'
            '(formatted label)</span>'
        )
        assert result['results'][0]['has_html_label'] is True
