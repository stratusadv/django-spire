from __future__ import annotations

import pytest
from django import forms
from django.template import Context, Template, TemplateSyntaxError
from django.test import SimpleTestCase

from django_spire.core.components import FormComponent
from django_spire.core.templatetags.django_spire_glue import GlueFormPath


class _SampleForm(forms.Form):
    name = forms.CharField()


class _NamedTaskFormComponent(FormComponent):
    template = 'django_spire/glue/form/modal_form.html'
    form_class = _SampleForm
    glue_form_object_name = 'task_form'


class GlueFormPathTestCase(SimpleTestCase):
    def test_renders_dotted_field_paths_without_quotes(self) -> None:
        template = Template(
            "{% load django_spire_glue django_glue %}"
            "{% glue_form_path 'time_entry_form' %}"
            "{{ time_entry_form }}|"
            "{{ time_entry_form.description }}|"
            "{{ time_entry_form.description|glue_field_metadata_path }}|"
            "{{ time_entry_form.description|glue_field_value_path }}"
        )

        rendered = template.render(Context())

        assert rendered == (
            'time_entry_form|'
            'time_entry_form.description|'
            'time_entry_form.$fields.description|'
            'time_entry_form.description'
        )

    def test_field_names_matching_str_methods_do_not_collide(self) -> None:
        template = Template(
            "{% load django_spire_glue %}"
            "{% glue_form_path 'task_form' %}"
            "{{ task_form.title }}|"
            "{{ task_form.format }}|"
            "{{ task_form.count }}|"
            "{{ task_form.index }}|"
            "{{ task_form.split }}"
        )

        rendered = template.render(Context())

        assert rendered == (
            'task_form.title|'
            'task_form.format|'
            'task_form.count|'
            'task_form.index|'
            'task_form.split'
        )

    def test_inherits_dynamic_variable_name(self) -> None:
        template = Template(
            "{% load django_spire_glue %}"
            "{% glue_form_path form_name %}"
            "{{ account_form.email }}"
        )

        rendered = template.render(Context({'form_name': 'account_form'}))

        assert rendered == 'account_form.email'

    def test_supports_as_alias(self) -> None:
        template = Template(
            "{% load django_spire_glue %}"
            "{% glue_form_path form_name as form %}"
            "{{ form.email }}"
        )

        rendered = template.render(Context({'form_name': 'account_form'}))

        assert rendered == 'account_form.email'

    def test_preserves_python_str_indexing_and_slicing(self) -> None:
        path = GlueFormPath('time_entry_form')

        assert path['description'] == 'time_entry_form.description'
        assert path[0] == 't'
        assert path[:4] == 'time'

    def test_rejects_invalid_tag_syntax(self) -> None:
        with pytest.raises(TemplateSyntaxError):
            Template("{% load django_spire_glue %}{% glue_form_path %}")

        with pytest.raises(TemplateSyntaxError):
            Template("{% load django_spire_glue %}{% glue_form_path 'a' into b %}")

    def test_form_template_exposes_form_path_under_object_name(self) -> None:
        template = Template(
            "{% extends 'django_spire/glue/form/modal_form.html' %}"
            "{% block glue_form_content %}"
            "{% include 'django_spire/glue/form/widget/input_widget.html' with glue_field=time_entry_form.description %}"
            "{% endblock %}"
        )

        rendered = template.render(
            Context({
                'glue_form': 'component.model.form',
                'glue_form_object_name': 'time_entry_form',
            })
        )

        assert 'time_entry_form: component.model.form,' in rendered
        assert 'time_entry_form.$fields.description' in rendered
        assert '() => time_entry_form.description' in rendered

    def test_default_glue_form_name_does_not_collide_with_modal_form_binding(self) -> None:
        template = Template(
            "{% extends 'django_spire/glue/form/modal_form.html' %}"
            "{% block glue_form_content %}"
            "{% include 'django_spire/glue/form/widget/input_widget.html' with glue_field=glue_form.title %}"
            "{% endblock %}"
        )

        rendered = template.render(Context({'glue_form': 'Glue.form.task_form'}))

        assert 'glue_form: Glue.form.task_form,' in rendered
        assert 'glue_form.$fields.title' in rendered
        assert '() => glue_form.title' in rendered

    def test_form_component_inherits_glue_form_object_name_in_template_context(self) -> None:
        template = Template(
            "{% extends 'django_spire/glue/form/modal_form.html' %}"
            "{% block glue_form_content %}"
            "{% include 'django_spire/glue/form/widget/input_widget.html' with glue_field=task_form.name %}"
            "{% endblock %}"
        )

        rendered = template.render(Context({'component': _NamedTaskFormComponent()}))

        assert 'task_form: component.form,' in rendered
        assert 'task_form.$fields.name' in rendered
        assert '() => task_form.name' in rendered
