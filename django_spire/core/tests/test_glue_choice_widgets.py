from __future__ import annotations

from pathlib import Path

from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import SimpleTestCase


def _core_js(name: str) -> str:
    return Path(finders.find(f'django_spire/js/{name}')).read_text()


class GlueChoiceWidgetTemplateTestCase(SimpleTestCase):
    def test_adaptive_field_selects_from_cardinality_and_searchable_metadata(self) -> None:
        html = render_to_string(
            'django_spire/glue/form/field/choice/adaptive_field.html',
            {'glue_field': 'form.company'},
        )
        search_js = _core_js('search_and_select.js')
        multi_js = _core_js('multi_search_and_select.js')

        assert 'adaptiveChoiceField?.choices_searchable' in html
        assert "'ModelMultipleChoiceField'" in html
        assert "'CheckboxSelectMultiple'" in html
        assert 'x-data="searchAndSelect(field' in html
        assert 'x-data="multiSearchAndSelect(field)"' in html
        assert 'glueField.searchChoices(this.searchQuery.trim())' in search_js
        assert 'glueField.searchChoices(this.search.trim())' in multi_js
        assert 'glueField?.selectedChoices || []' in multi_js
        assert '<select' in html
        assert 'type="checkbox"' not in html

    def test_explicit_choice_fields_keep_their_original_widgets(self) -> None:
        single_html = render_to_string(
            'django_spire/glue/form/field/choice/field.html', {'glue_field': 'form.company'}
        )
        adaptive_multiple_html = render_to_string(
            'django_spire/glue/form/field/choice/adaptive_field.html',
            {'glue_field': 'form.companies'},
        )
        multi_js = _core_js('multi_search_and_select.js')

        assert '<select' in single_html
        assert 'field.searchChoices' not in single_html
        assert 'glueField?.selectedChoices || []' in multi_js
        assert 'type="checkbox"' not in adaptive_multiple_html

    def test_search_widget_supports_server_and_local_choice_sources(self) -> None:
        html = render_to_string(
            'django_spire/glue/form/widget/search_and_select_widget.html',
            {'glue_field': 'form.company'},
        )
        search_js = _core_js('search_and_select.js')

        assert 'x-data="searchAndSelect(field' in html
        assert 'field.choices_searchable' in html
        assert 'field.isSearchingChoices' in html
        assert 'glueField.searchChoices(this.searchQuery.trim())' in search_js
        assert 'glueField.clearSearch?.()' in search_js
        assert 'glueField?.choices_searchable' in search_js
        assert 'String(choice.label).toLowerCase().includes(query)' in search_js

    def test_multiple_search_widget_supports_server_and_local_choice_sources(self) -> None:
        html = render_to_string(
            'django_spire/glue/form/widget/multi_search_and_select_widget.html',
            {'glue_field': 'form.companies'},
        )
        multi_js = _core_js('multi_search_and_select.js')

        assert 'x-data="multiSearchAndSelect(field)"' in html
        assert 'field.choices_searchable' in html
        assert 'field.isSearchingChoices' in html
        assert 'glueField.searchChoices(this.search.trim())' in multi_js
        assert 'glueField.clearSearch?.()' in multi_js
        assert 'glueField?.selectedChoices || []' in multi_js
