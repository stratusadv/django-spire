from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured
from django_glue import Glue
from django_glue.exceptions import GlueComponentParameterError
from django_glue.glue.components import component_registry
from django_glue.glue.objects.django.form.object import FormGlue

from django_spire.core.glue.components import FormComponent
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.task.forms import TaskModalForm, TaskModelForm
from test_project.app.task.models import Task


class TaskFormComponent(FormComponent):
    template = 'task/form/task_form.html'
    form_class = TaskModelForm


class FormComponentTestCase(BaseTestCase):
    def test_reconstructs_by_importing_its_identifier(self) -> None:
        identifier = f'{TaskFormComponent.__module__}.{TaskFormComponent.__qualname__}'

        del component_registry.by_identifier[identifier]

        assert component_registry.from_identifier(identifier) is TaskFormComponent

    def test_child_is_a_form_glue_holding_the_form(self) -> None:
        component = TaskFormComponent()

        assert isinstance(component.form, FormGlue)
        assert isinstance(component.form.form, TaskModelForm)

    def test_get_form_can_receive_constructor_arguments(self) -> None:
        class InitialFormComponent(FormComponent):
            template = 'task/form/task_form.html'
            form_class = TaskModelForm

            seed: str = Glue.ComponentParameter('Default')

            def get_form(self) -> TaskModelForm:
                return self.form_class(initial={'name': self.seed})

        component = InitialFormComponent(seed='Seeded')

        assert component.form.form.initial['name'] == 'Seeded'

    def test_has_no_pk_parameter(self) -> None:
        with pytest.raises(GlueComponentParameterError):
            TaskFormComponent(pk=1)

    def test_glue_form_path_names_the_form_child(self) -> None:
        assert TaskFormComponent().glue_form_path() == 'component.form'

    def test_built_directly_from_a_form_class_and_a_template(self) -> None:
        component = FormComponent(form_class=TaskModalForm, template='task/form/task_form.html')

        assert component.template == 'task/form/task_form.html'
        assert component.form_class is TaskModalForm
        assert isinstance(component.form.form, TaskModalForm)

    def test_a_directly_built_component_is_rebuilt_from_its_signed_identity(self) -> None:
        component = FormComponent(form_class=TaskModalForm, template='task/form/task_form.html')
        identity = component.identity

        rebuilt = component_registry.from_identifier(identity['component_id'])(
            **identity['parameters'],
        )

        assert identity['component_id'].endswith('.FormComponent')
        assert identity['parameters'] == {
            'form_path': 'test_project.app.task.forms:TaskModalForm',
            'template_name': 'task/form/task_form.html',
        }
        assert rebuilt.template == 'task/form/task_form.html'
        assert rebuilt.form_class is TaskModalForm

    def test_a_form_class_passed_directly_replaces_the_one_on_the_class(self) -> None:
        component = TaskFormComponent(form_class=TaskModalForm)

        assert component.form_class is TaskModalForm
        assert TaskFormComponent.form_class is TaskModelForm

    def test_a_form_that_is_not_at_module_level_is_refused(self) -> None:
        class LocalForm(TaskModelForm):
            pass

        with pytest.raises(ImproperlyConfigured, match='module level'):
            FormComponent(form_class=LocalForm, template='task/form/task_form.html')

    def test_requires_a_form_class(self) -> None:
        with pytest.raises(TypeError, match='form_class'):
            FormComponent(template='task/form/task_form.html')

    def test_requires_a_template(self) -> None:
        with pytest.raises(ValueError, match='template'):
            FormComponent(form_class=TaskModalForm)

    def test_rejects_a_non_form_class(self) -> None:
        with pytest.raises(TypeError, match='form_class'):

            class WrongFormComponent(FormComponent):
                template = 'task/form/task_form.html'
                form_class = Task

    def test_the_removed_attr_setting_is_refused_by_name(self) -> None:
        with pytest.raises(TypeError, match='attr was removed'):

            class NamedChildFormComponent(FormComponent):
                template = 'task/form/task_form.html'
                attr = 'entry'
                form_class = TaskModelForm

    def test_the_removed_form_setting_is_refused_by_name(self) -> None:
        with pytest.raises(TypeError, match='form was removed'):

            class OldStyleFormComponent(FormComponent):
                template = 'task/form/task_form.html'
                form = TaskModelForm
