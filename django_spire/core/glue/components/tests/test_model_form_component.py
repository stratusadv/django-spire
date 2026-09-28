from __future__ import annotations

import pytest
from django_glue import Glue
from django_glue.exceptions import GlueComponentParameterError
from django_glue.glue.component_registry import component_registry

from django_spire.core.glue.components import ModelFormComponent
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.task.forms import TaskModelForm
from test_project.app.task.models import Task


class TaskModelFormComponent(ModelFormComponent):
    template = 'task/modal/task_form_modal.html'
    attr = 'task'
    model_class = Task
    form = TaskModelForm
    fields = ('id', 'name', 'description')

    entry_id: int | None = Glue.ComponentParameter(None)


class DefaultModelFormComponent(ModelFormComponent):
    template = 'task/modal/task_form_modal.html'
    model_class = Task
    form = TaskModelForm
    fields = ('id', 'name')


class ModelFormComponentTestCase(BaseTestCase):
    def test_model_child_is_named_by_attr(self) -> None:
        assert 'task' in TaskModelFormComponent.__dict__
        assert 'model' in DefaultModelFormComponent.__dict__

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

    def test_default_get_model_returns_blank_or_fetched_instance(self) -> None:
        task = Task.objects.create(name='Fetched')

        assert TaskModelFormComponent(pk=task.pk).task.instance.pk == task.pk

        blank = DefaultModelFormComponent()

        assert isinstance(blank.model.instance, Task)
        assert blank.model.instance.pk is None

    def test_get_model_can_be_overridden(self) -> None:
        class MarkedModelFormComponent(ModelFormComponent):
            template = 'task/modal/task_form_modal.html'
            model_class = Task
            form = TaskModelForm
            fields = ('id', 'name')

            def get_model(self) -> Task:
                return Task(name='Resolved By Subclass')

        assert MarkedModelFormComponent().model.instance.name == 'Resolved By Subclass'

    def test_get_fields_defaults_to_fields(self) -> None:
        assert DefaultModelFormComponent().model.fields == ('id', 'name')

    def test_get_fields_can_be_overridden(self) -> None:
        class NarrowingModelFormComponent(ModelFormComponent):
            template = 'task/modal/task_form_modal.html'
            model_class = Task
            form = TaskModelForm
            fields = ('id', 'name', 'description')

            def get_fields(self) -> tuple[str, ...]:
                return ('id', 'name')

        assert NarrowingModelFormComponent().model.fields == ('id', 'name')

    def test_dynamic_fields_only_need_get_fields(self) -> None:
        class DynamicModelFormComponent(ModelFormComponent):
            template = 'task/modal/task_form_modal.html'
            model_class = Task
            form = TaskModelForm

            def get_fields(self) -> tuple[str, ...]:
                return ('id', 'name')

        assert DynamicModelFormComponent().model.fields == ('id', 'name')

    def test_has_no_choices_by_default(self) -> None:
        assert DefaultModelFormComponent().model.choices == {}

    def test_get_choices_receives_the_resolved_instance(self) -> None:
        seen: list[Task] = []

        class ChoosingModelFormComponent(ModelFormComponent):
            template = 'task/modal/task_form_modal.html'
            model_class = Task
            form = TaskModelForm
            fields = ('id', 'name', 'parent')

            def get_choices(self, instance: Task) -> dict:
                seen.append(instance)
                return {'parent': Task.objects.all()}

        model = ChoosingModelFormComponent().model

        assert seen[0] is model.instance
        assert model.choices.keys() == {'parent'}

    def test_context_data_names_the_component_and_glue_form(self) -> None:
        component = TaskModelFormComponent()

        context = component.get_context_data()

        assert context['component'] is component
        assert context['glue_form'] == 'component.task.form'
        assert set(context) == {'component', 'glue_form'}

    def test_requires_a_model_class(self) -> None:
        with pytest.raises(TypeError, match='model_class'):

            class IncompleteModelFormComponent(ModelFormComponent):
                template = 'task/modal/task_form_modal.html'
                form = TaskModelForm
                fields = ('id',)

    def test_rejects_a_non_model_form(self) -> None:
        with pytest.raises(TypeError, match='form'):

            class WrongFormModelFormComponent(ModelFormComponent):
                template = 'task/modal/task_form_modal.html'
                model_class = Task
                form = Task
                fields = ('id',)

    def test_requires_fields_or_get_fields(self) -> None:
        with pytest.raises(ValueError, match='fields'):

            class FieldlessModelFormComponent(ModelFormComponent):
                template = 'task/modal/task_form_modal.html'
                model_class = Task
                form = TaskModelForm

    def test_rejects_an_attr_that_claims_a_class_attribute(self) -> None:
        with pytest.raises(ValueError, match='reserved'):

            class ClaimingModelFormComponent(ModelFormComponent):
                template = 'task/modal/task_form_modal.html'
                attr = 'template'
                model_class = Task
                form = TaskModelForm
                fields = ('id',)
