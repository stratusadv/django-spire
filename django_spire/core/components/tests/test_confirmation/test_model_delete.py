from __future__ import annotations

from django.template.loader import render_to_string
from django.test import RequestFactory
from django_glue import Glue

from django_spire.core.components.confirmation import ModelDeleteConfirmationComponent
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.comment.tests.factories import create_test_comment_example


class ModelDeleteConfirmationComponentTestCase(BaseTestCase):
    def test_confirming_soft_deletes_the_row_and_fires_its_key(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = ModelDeleteConfirmationComponent(model_obj=comment)

        component.confirm()

        comment.refresh_from_db()

        assert comment.is_deleted is True
        assert component.__dict__['_pending_events'] == [
            {'name': 'confirmed', 'detail': {'pk': comment.pk}},
        ]

    def test_confirm_requires_delete_access(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        request = RequestFactory().get('/')
        request.user = self.super_user
        request.session = self.client.session
        component = Glue.object(request, ModelDeleteConfirmationComponent(model_obj=comment))

        assert component._resolve_required_access(
            component._bound_attributes['confirm'].definition.required_access
        ) == Glue.Access.DELETE

    def test_the_prompt_names_the_row_unless_it_is_worded_when_built(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        named = ModelDeleteConfirmationComponent(model_obj=comment)
        worded = ModelDeleteConfirmationComponent(
            model_obj=comment,
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

    def test_the_row_it_was_built_with_is_read_without_a_query(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = ModelDeleteConfirmationComponent(model_obj=comment)

        with self.assertNumQueries(0):
            assert component.model_obj == comment
            assert component.model_name == 'Comment'
