from __future__ import annotations

import pytest
from django import forms
from django_glue.exceptions import GlueComponentParameterError, GlueModelInstanceNotFoundError
from django_glue.glue.components import component_registry

from django_spire.core.components import ModelFormComponent
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.task.forms import TaskModalForm, TaskModelForm
from test_project.app.task.models import Task


class TaskModelFormComponent(ModelFormComponent):
    template = 'task/modal/task_form_modal.html'
    form_class = TaskModelForm
    fields = ('id', 'name', 'description')


class DefaultModelFormComponent(ModelFormComponent):
    template = 'task/modal/task_form_modal.html'
    form_class = TaskModelForm


class PlainForm(forms.Form):
    name = forms.CharField()


class ModelFormComponentTestCase(BaseTestCase):
    def test_reconstructs_by_importing_its_identifier(self) -> None:
        identifier = f'{TaskModelFormComponent.__module__}.{TaskModelFormComponent.__qualname__}'

        del component_registry.by_identifier[identifier]

        assert component_registry.from_identifier(identifier) is TaskModelFormComponent

    def test_pk_parameter_defaults_to_none_and_accepts_a_value(self) -> None:
        assert TaskModelFormComponent().pk is None
        assert TaskModelFormComponent(pk=3).pk == 3

    def test_unexpected_parameter_is_rejected(self) -> None:
        with pytest.raises(GlueComponentParameterError):
            TaskModelFormComponent(unknown=1)

    def test_the_model_is_the_forms_own(self) -> None:
        task = Task.objects.create(name='Fetched')

        assert TaskModelFormComponent(pk=task.pk).model.instance.pk == task.pk

        blank = DefaultModelFormComponent()

        assert isinstance(blank.model.instance, Task)
        assert blank.model.instance.pk is None

    def test_a_row_that_no_longer_exists_is_reported_as_not_found(self) -> None:
        task = Task.objects.create(name='Deleted Since')
        pk = task.pk
        task.delete()

        with pytest.raises(GlueModelInstanceNotFoundError) as error:
            TaskModelFormComponent(pk=pk).get_model()

        assert error.value.status == 404
        assert error.value.pk == pk

    def test_get_model_can_be_overridden(self) -> None:
        class MarkedModelFormComponent(ModelFormComponent):
            template = 'task/modal/task_form_modal.html'
            form_class = TaskModelForm

            def get_model(self) -> Task:
                return Task(name='Resolved By Subclass')

        assert MarkedModelFormComponent().model.instance.name == 'Resolved By Subclass'

    def test_fields_default_to_the_forms_own(self) -> None:
        assert DefaultModelFormComponent().model.fields == (
            'name',
            'description',
            'status',
            'parent',
        )

    def test_fields_set_on_the_class_replace_the_forms(self) -> None:
        assert TaskModelFormComponent().model.fields == ('id', 'name', 'description')

    def test_get_fields_can_be_overridden(self) -> None:
        class NarrowingModelFormComponent(ModelFormComponent):
            template = 'task/modal/task_form_modal.html'
            form_class = TaskModelForm
            fields = ('id', 'name', 'description')

            def get_fields(self) -> tuple[str, ...]:
                return ('id', 'name')

        assert NarrowingModelFormComponent().model.fields == ('id', 'name')

    def test_has_no_choices_by_default(self) -> None:
        assert DefaultModelFormComponent().model.choices == {}

    def test_get_choices_receives_the_resolved_instance(self) -> None:
        seen: list[Task] = []

        class ChoosingModelFormComponent(ModelFormComponent):
            template = 'task/modal/task_form_modal.html'
            form_class = TaskModelForm
            fields = ('id', 'name', 'parent')

            def get_choices(self, instance: Task) -> dict:
                seen.append(instance)
                return {'parent': Task.objects.all()}

        model = ChoosingModelFormComponent().model

        assert seen[0] is model.instance
        assert model.choices.keys() == {'parent'}

    def test_glue_form_path_names_the_models_form(self) -> None:
        assert TaskModelFormComponent().glue_form_path() == 'component.model.form'

    def test_built_directly_from_a_form_class_and_a_template(self) -> None:
        component = ModelFormComponent(
            form_class=TaskModalForm,
            template='task/modal/task_form_modal.html',
        )

        assert component.template == 'task/modal/task_form_modal.html'
        assert isinstance(component.model.instance, Task)
        assert component.model.fields == ('name', 'description', 'status')

    def test_a_directly_built_component_is_rebuilt_from_its_signed_identity(self) -> None:
        task = Task.objects.create(name='Fetched')
        component = ModelFormComponent(
            form_class=TaskModalForm,
            template='task/modal/task_form_modal.html',
            pk=task.pk,
        )
        identity = component.identity

        rebuilt = component_registry.from_identifier(identity['component_id'])(
            **identity['parameters'],
        )

        assert identity['component_id'].endswith('.ModelFormComponent')
        assert identity['parameters'] == {
            'form_path': 'test_project.app.task.forms:TaskModalForm',
            'template_name': 'task/modal/task_form_modal.html',
            'pk': task.pk,
        }
        assert rebuilt.form_class is TaskModalForm
        assert rebuilt.model.instance == task

    def test_rejects_a_non_model_form(self) -> None:
        with pytest.raises(TypeError, match='ModelForm'):

            class PlainFormModelFormComponent(ModelFormComponent):
                template = 'task/modal/task_form_modal.html'
                form_class = PlainForm

    def test_the_removed_attr_setting_is_refused_by_name(self) -> None:
        with pytest.raises(TypeError, match='attr was removed'):

            class NamedChildModelFormComponent(ModelFormComponent):
                template = 'task/modal/task_form_modal.html'
                attr = 'task'
                form_class = TaskModelForm

    def test_the_removed_form_setting_is_refused_by_name(self) -> None:
        with pytest.raises(TypeError, match='form was removed'):

            class OldStyleModelFormComponent(ModelFormComponent):
                template = 'task/modal/task_form_modal.html'
                form = TaskModelForm
