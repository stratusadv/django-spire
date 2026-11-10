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
        assert 'source.searchChoices(this.search.trim())' in multi_js
        assert 'source?.selectedChoices || []' in multi_js
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
        assert 'source?.selectedChoices || []' in multi_js
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
        assert 'x-show="isSearchable && isSearching"' in html
        assert 'source?.choices_searchable' in multi_js
        assert 'source?.isSearchingChoices' in multi_js
        assert 'source.searchChoices(this.search.trim())' in multi_js
        assert 'source.clearSearch?.()' in multi_js
        assert 'source?.selectedChoices || []' in multi_js

    def test_the_multiple_search_widget_is_the_generic_widget_over_the_glue_field(self) -> None:
        glue_html = render_to_string(
            'django_spire/glue/form/widget/multi_search_and_select_widget.html',
            {'glue_field': 'form.companies'},
        )
        generic_html = render_to_string(
            'django_spire/widget/multi_search_and_select_widget.html',
            {'source': 'typeSource', 'empty_label': 'All types'},
        )

        assert 'x-data="glueField(' in glue_html
        assert 'x-data="multiSearchAndSelect(field)"' in glue_html
        assert 'x-data="multiSearchAndSelect(typeSource)"' in generic_html
        assert 'glueField(' not in generic_html
        assert 'field.' not in generic_html
        assert 'All types' in generic_html

    def test_a_choice_source_can_be_built_over_any_values(self) -> None:
        source_js = _core_js('choice_source.js')
        multi_js = _core_js('multi_search_and_select.js')

        assert 'Spire.widget.choiceSource = ({choices, getSelected, setSelected})' in source_js
        assert 'get selectedChoices()' in source_js
        assert 'addChoice(value)' in source_js
        assert 'removeChoice(value)' in source_js
        assert 'escapeHtml(choice.label)' in multi_js
