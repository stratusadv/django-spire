from __future__ import annotations

from django.template.loader import render_to_string
from django.test import SimpleTestCase


class DeleteFormTemplateTestCase(SimpleTestCase):
    def test_delete_form_confirms_the_delete(self) -> None:
        html = render_to_string(
            'django_spire/form/delete_form.html',
            {'form_description': 'Are you sure you would like to delete group "Crew"?'},
        )

        assert 'method="post"' in html
        assert 'Are you sure you would like to delete group &quot;Crew&quot;?' in html
        assert '<input type="hidden" name="should_delete" value="true">' in html


class GlueFieldWidgetTemplateTestCase(SimpleTestCase):
    def test_a_field_takes_its_events_and_input_state_from_binds(self) -> None:
        html = render_to_string(
            'django_spire/glue/form/widget/input_widget.html',
            {'glue_field': 'task_form.name'},
        )

        assert 'x-bind="glueFieldEvents"' in html
        assert 'x-bind="glueFieldInput"' in html
        assert '@focusin' not in html
        assert ':required' not in html

    def test_the_file_fields_are_components(self) -> None:
        single = render_to_string(
            'django_spire/file/form/field/single_file_field.html',
            {'glue_field': 'file_form.picture'},
        )
        multi = render_to_string(
            'django_spire/file/form/field/multi_file_field.html',
            {'glue_field': 'file_form.attachments', 'accept': "image/*,.o'k"},
        )

        assert 'x-data="glueSingleFileField()"' in single
        assert 'NEED TO PUT' not in single
        file_input = single[single.index('type="file"'):]
        assert file_input[:file_input.index('>')].count('class=') == 1
        assert "accept: 'image/*,.o\\u0027k'" in multi
        assert 'handle_files_change(event) {' not in multi
