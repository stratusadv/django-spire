from __future__ import annotations

import pytest
from django.template.loader import render_to_string
from django.test import RequestFactory
from django_glue import Glue
from django_glue.exceptions import GlueModelInstanceNotFoundError

from django_spire.core.components.confirmation import (
    ModelDeleteConfirmationComponent,
    ModelSetDeletedConfirmationComponent,
)
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.comment.models import CommentExample
from test_project.app.comment.tests.factories import create_test_comment_example


class ModelDeleteConfirmationComponentTestCase(BaseTestCase):
    def test_confirming_deletes_the_row_from_the_database_and_fires_its_key(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        pk = comment.pk
        component = ModelDeleteConfirmationComponent(instance=comment)

        component.confirm()

        assert CommentExample.objects.filter(pk=pk).exists() is False
        assert component.__dict__['_pending_events'] == [
            {'name': 'confirmed', 'detail': {'pk': pk}},
        ]


class ModelSetDeletedConfirmationComponentTestCase(BaseTestCase):
    def test_confirming_soft_deletes_the_row_and_fires_its_key(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = ModelSetDeletedConfirmationComponent(instance=comment)

        component.confirm()

        comment.refresh_from_db()

        assert comment.is_deleted is True
        assert component.__dict__['_pending_events'] == [
            {'name': 'confirmed', 'detail': {'pk': comment.pk}},
        ]


class KeptCommentDeleteConfirmationComponent(ModelSetDeletedConfirmationComponent):
    @Glue.ComponentParameter
    def instance(self, pk: int) -> CommentExample:
        return CommentExample.objects.filter(name__startswith='Kept').get(pk=pk)


class ScopedInstanceTestCase(BaseTestCase):
    def test_a_subclass_can_scope_the_row_it_looks_up_again(self) -> None:
        kept = create_test_comment_example(name='Kept Notes')
        dropped = create_test_comment_example(name='Dropped Notes')
        component_class = KeptCommentDeleteConfirmationComponent
        kept_parameters = component_class(instance=kept).identity['parameters']
        dropped_parameters = component_class(instance=dropped).identity['parameters']

        assert component_class(**kept_parameters).instance == kept

        with pytest.raises(GlueModelInstanceNotFoundError):
            component_class(**dropped_parameters).instance  # noqa: B018


class BaseModelDeleteConfirmationComponentTestCase(BaseTestCase):
    def test_confirm_requires_delete_access(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        request = RequestFactory().get('/')
        request.user = self.super_user
        request.session = self.client.session

        for component_class in (
            ModelDeleteConfirmationComponent,
            ModelSetDeletedConfirmationComponent,
        ):
            component = Glue.object(request, component_class(instance=comment))

            assert component._resolve_required_access(
                component._bound_attributes['confirm'].definition.required_access
            ) == Glue.Access.DELETE

    def test_the_prompt_names_the_row_unless_it_is_worded_when_built(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        named = ModelSetDeletedConfirmationComponent(instance=comment)
        worded = ModelSetDeletedConfirmationComponent(
            instance=comment,
            title='Archive Comment',
            message='It can be restored later.',
            confirm_label='Archive',
        )

        named_html = ' '.join(render_to_string(named.template, {'component': named}).split())
        worded_html = ' '.join(render_to_string(worded.template, {'component': worded}).split())

        assert 'Delete Comment' in named_html
        assert '"<strong>Budget Review</strong>"' in named_html
        assert '</i>Delete </button>' in named_html
        assert 'Archive Comment' in worded_html
        assert 'It can be restored later.' in worded_html
        assert '</i>Archive </button>' in worded_html
        assert 'Delete' not in worded_html
