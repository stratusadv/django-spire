from __future__ import annotations

from django.template.loader import render_to_string
from django.test import SimpleTestCase


class GlueChoiceWidgetTemplateTestCase(SimpleTestCase):
    def test_adaptive_field_selects_from_cardinality_and_searchable_metadata(self) -> None:
        html = render_to_string(
            'django_spire/glue/form/field/choice/adaptive_field.html',
            {'glue_field': 'form.company'},
        )

        assert 'adaptiveChoiceField?.choices_searchable' in html
        assert "'ModelMultipleChoiceField'" in html
        assert "'CheckboxSelectMultiple'" in html
        assert 'field.searchChoices(this.searchQuery.trim())' in html
        assert 'field.searchChoices(this.search.trim())' in html
        assert 'field?.selectedChoices || []' in html
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

        assert '<select' in single_html
        assert 'field.searchChoices' not in single_html
        assert 'field?.selectedChoices || []' in adaptive_multiple_html
        assert 'type="checkbox"' not in adaptive_multiple_html

    def test_search_widget_supports_server_and_local_choice_sources(self) -> None:
        html = render_to_string(
            'django_spire/glue/form/widget/search_and_select_widget.html',
            {'glue_field': 'form.company'},
        )

        assert 'field?.choices_searchable' in html
        assert 'field.searchChoices(this.searchQuery.trim())' in html
        assert 'field.clearSearch?.()' in html
        assert 'field.isSearchingChoices' in html
        assert 'String(choice.label).toLowerCase().includes(query)' in html

    def test_multiple_search_widget_supports_server_and_local_choice_sources(self) -> None:
        html = render_to_string(
            'django_spire/glue/form/widget/multi_search_and_select_widget.html',
            {'glue_field': 'form.companies'},
        )

        assert 'field?.choices_searchable' in html
        assert 'field.searchChoices(this.search.trim())' in html
        assert 'field.clearSearch?.()' in html
        assert 'field.isSearchingChoices' in html
        assert 'field?.selectedChoices || []' in html
