from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
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

        # The adaptive field template picks one of three widget markup shapes
        # per field: a plain select (static single), a search-and-select, and
        # the multiselect (both static and searchable multiples). Both search
        # widgets carry a backend path (field.searchChoices) and a static
        # local-filter path (label.includes(query)).
        assert 'adaptiveChoiceField?.choices_searchable' in html
        assert '<select' in html
        assert 'field?.selectedChoices || []' in html
        assert 'field.searchChoices(this.search.trim())' in html
        assert 'String(choice.label).toLowerCase().includes(query)' in html
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
