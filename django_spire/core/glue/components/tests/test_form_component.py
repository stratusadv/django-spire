from __future__ import annotations

import pytest
from django_glue import Glue
from django_glue.exceptions import GlueComponentParameterError
from django_glue.glue.components import component_registry
from django_glue.glue.objects.django.form.object import FormGlue

from django_spire.core.glue.components import FormComponent
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.task.forms import TaskModelForm
from test_project.app.task.models import Task


class TaskFormComponent(FormComponent):
    template = 'task/form/task_form.html'
    attr = 'entry'
    form = TaskModelForm


class CustomAttrFormComponent(FormComponent):
    template = 'task/form/task_form.html'
    attr = 'task_form'
    form = TaskModelForm


class FormComponentTestCase(BaseTestCase):
    def test_form_child_is_named_by_attr(self) -> None:
        assert 'entry' in TaskFormComponent.__dict__
        assert 'task_form' in CustomAttrFormComponent.__dict__

    def test_reconstructs_by_importing_its_identifier(self) -> None:
        identifier = f'{TaskFormComponent.__module__}.{TaskFormComponent.__qualname__}'

        del component_registry.by_identifier[identifier]

        assert component_registry.from_identifier(identifier) is TaskFormComponent

    def test_child_is_a_form_glue_holding_the_form(self) -> None:
        component = TaskFormComponent()

        assert isinstance(component.entry, FormGlue)
        assert isinstance(component.entry.form, TaskModelForm)

    def test_get_form_can_receive_constructor_arguments(self) -> None:
        class InitialFormComponent(FormComponent):
            template = 'task/form/task_form.html'
            attr = 'seeded'
            form = TaskModelForm

            seed: str = Glue.ComponentParameter('Default')

            def get_form(self) -> TaskModelForm:
                return self.form(initial={'name': self.seed})

        component = InitialFormComponent(seed='Seeded')

        assert component.seeded.form.initial['name'] == 'Seeded'

    def test_requires_an_attr(self) -> None:
        with pytest.raises(ValueError, match='attr'):

            class AttrlessComponent(FormComponent):
                template = 'task/form/task_form.html'
                form = TaskModelForm

    def test_has_no_pk_parameter(self) -> None:
        with pytest.raises(GlueComponentParameterError):
            TaskFormComponent(pk=1)

    def test_glue_form_path_names_the_form_child(self) -> None:
        assert TaskFormComponent().glue_form_path() == 'component.entry'
        assert CustomAttrFormComponent().glue_form_path() == 'component.task_form'

    def test_requires_a_form_class(self) -> None:
        with pytest.raises(TypeError, match='form'):

            class FormlessComponent(FormComponent):
                template = 'task/form/task_form.html'

    def test_rejects_a_non_form_class(self) -> None:
        with pytest.raises(TypeError, match='form'):

            class WrongFormComponent(FormComponent):
                template = 'task/form/task_form.html'
                form = Task

    def test_rejects_an_attr_that_claims_a_class_attribute(self) -> None:
        with pytest.raises(ValueError, match='reserved'):

            class ClaimingFormComponent(FormComponent):
                template = 'task/form/task_form.html'
                attr = 'template'
                form = TaskModelForm
