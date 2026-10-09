from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.forms import ModelForm
from django_glue import Glue

from django_spire.core.components import (
    ComponentFormOptions,
    ModelFormComponent,
    PageFormOptions,
)
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.comment.models import CommentExample
from test_project.app.comment.tests.factories import create_test_comment_example

FORM_TEMPLATE = 'task/component/task_form_modal.html'


class CommentForm(ModelForm):
    class Meta:
        model = CommentExample
        fields = ('name',)


class CommentFormComponent(ModelFormComponent):
    template = FORM_TEMPLATE
    form_class = CommentForm


class ComponentFormOptionsTestCase(BaseTestCase):
    def test_a_form_class_and_template_build_the_generic_form_component(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        options = ComponentFormOptions(form_class=CommentForm, template=FORM_TEMPLATE)

        form = options.build_component(pk=comment.pk, access=Glue.Access.CHANGE)

        assert type(form) is ModelFormComponent
        assert form.form_class is CommentForm
        assert form.template == FORM_TEMPLATE
        assert form.model.instance == comment
        assert form.access == Glue.Access.CHANGE

    def test_a_component_is_built_with_its_own_form_and_template(self) -> None:
        options = ComponentFormOptions(component=CommentFormComponent)

        form = options.build_component(pk=None, access=Glue.Access.CHANGE)

        assert type(form) is CommentFormComponent
        assert form.form_class is CommentForm
        assert form.template == FORM_TEMPLATE
        assert form.model.instance.pk is None

    def test_a_component_beside_a_form_class_or_template_is_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='not both'):
            ComponentFormOptions(component=CommentFormComponent, form_class=CommentForm)

        with pytest.raises(ImproperlyConfigured, match='not both'):
            ComponentFormOptions(component=CommentFormComponent, template=FORM_TEMPLATE)

    def test_half_of_the_form_class_and_template_pair_is_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='together with'):
            ComponentFormOptions(form_class=CommentForm)

        with pytest.raises(ImproperlyConfigured, match='together with'):
            ComponentFormOptions(template=FORM_TEMPLATE)

        with pytest.raises(ImproperlyConfigured, match='together with'):
            ComponentFormOptions()


class PageFormOptionsTestCase(BaseTestCase):
    def test_one_route_serves_both_unless_a_create_route_is_given(self) -> None:
        shared = PageFormOptions('task:form:form')
        split = PageFormOptions('order:update', create_url_name='order:create')

        assert (shared.url_name, shared.create_url_name) == ('task:form:form', None)
        assert (split.url_name, split.create_url_name) == ('order:update', 'order:create')

    def test_the_return_route_is_optional(self) -> None:
        returning = PageFormOptions('order:update', return_url_name='order:list')

        assert PageFormOptions('order:update').return_url_name is None
        assert returning.return_url_name == 'order:list'
