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
        assert 'x-data="searchAndSelect(field)"' in html
        assert 'x-data="multiSearchAndSelect(field)"' in html
        assert 'source.searchChoices(this.searchQuery.trim())' in search_js
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

        assert 'x-data="searchAndSelect(field)"' in html
        assert 'x-show="isSearchable && isSearching"' in html
        assert 'source.searchChoices(this.searchQuery.trim())' in search_js
        assert 'source.clearSearch?.()' in search_js
        assert 'source?.choices_searchable' in search_js
        assert 'source?.isSearchingChoices' in search_js
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

    def test_the_search_widget_is_the_generic_widget_over_the_glue_field(self) -> None:
        glue_html = render_to_string(
            'django_spire/glue/form/widget/search_and_select_widget.html',
            {'glue_field': 'form.company'},
        )
        generic_html = render_to_string(
            'django_spire/widget/search_and_select_widget.html',
            {'source': 'accountSource', 'placeholder': 'All accounts'},
        )
        search_js = _core_js('search_and_select.js')

        assert 'x-data="glueField(' in glue_html
        assert 'x-data="searchAndSelect(field)"' in glue_html
        assert 'x-data="searchAndSelect(accountSource)"' in generic_html
        assert 'glueField(' not in generic_html
        assert 'field.' not in generic_html
        assert 'All accounts' in generic_html
        assert 'source.value = choice.value' in search_js
        assert 'escapeHtml(choice?.label' in search_js

    def test_a_glue_search_field_is_its_own_source(self) -> None:
        html = render_to_string(
            'django_spire/glue/form/field/choice/search_field.html',
            {'glue_field': 'form.company'},
        )

        assert 'x-data="searchAndSelect(field)"' in html

    def test_a_search_field_lists_an_empty_choice_that_clears_it(self) -> None:
        html = render_to_string(
            'django_spire/glue/form/field/choice/search_field.html',
            {'glue_field': 'component.filters.account', 'include_empty': True, 'empty_label': 'All accounts'},
        )

        assert '@click="selectItem({value: null})"' in html
        assert 'All accounts' in html

    def test_a_search_field_lists_no_empty_choice_unless_asked(self) -> None:
        html = render_to_string(
            'django_spire/glue/form/field/choice/search_field.html',
            {'glue_field': 'form.company'},
        )

        assert 'selectItem({value: null})' not in html

    def test_a_choice_source_can_be_built_over_any_values(self) -> None:
        source_js = _core_js('choice_source.js')
        multi_js = _core_js('multi_search_and_select.js')

        assert 'Spire.widget.choiceSource = ({choices, getSelected, setSelected})' in source_js
        assert 'get selectedChoices()' in source_js
        assert 'addChoice(value)' in source_js
        assert 'removeChoice(value)' in source_js
        assert 'escapeHtml(choice.label)' in multi_js

    def test_dropdown_choice_widgets_wire_keyboard_navigation(self) -> None:
        single_html = render_to_string(
            'django_spire/widget/search_and_select_widget.html',
            {'source': 'field', 'include_empty': True},
        )
        multi_html = render_to_string(
            'django_spire/widget/multi_search_and_select_widget.html',
            {'source': 'field'},
        )
        nav_js = _core_js('dropdown_navigation.js')
        search_js = _core_js('search_and_select.js')
        multi_js = _core_js('multi_search_and_select.js')

        assert 'Spire.widget.dropdownNavigation' in nav_js
        assert "Alpine.bind('dropdownTrigger'" in nav_js
        assert "Alpine.bind('dropdownSearchInput'" in nav_js
        assert "Alpine.bind('dropdownOption'" in nav_js
        assert '...Spire.widget.dropdownNavigation' in search_js
        assert '...Spire.widget.dropdownNavigation' in multi_js

        assert 'data-include-empty="true"' in single_html
        assert 'x-bind="dropdownTrigger"' in single_html
        assert 'x-bind="dropdownSearchInput"' in single_html
        assert 'x-bind="dropdownOption(' in single_html

        assert 'x-bind="dropdownTrigger"' in multi_html
        assert 'x-bind="dropdownSearchInput"' in multi_html
        assert 'x-bind="dropdownOption(' in multi_html
        assert '@keydown.space="handleSpaceKey($event)"' in multi_html
