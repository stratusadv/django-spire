from __future__ import annotations

from django.template.loader import render_to_string
from django.test import RequestFactory
from django_glue import Glue

from django_spire.core.components.confirmation import BaseModelActionConfirmationComponent
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.comment.tests.factories import create_test_comment_example


class RenameCommentConfirmationComponent(BaseModelActionConfirmationComponent):
    def perform_action(self) -> None:
        self.instance.name = 'Renamed'
        self.instance.save()


class BaseModelActionConfirmationComponentTestCase(BaseTestCase):
    def test_confirming_performs_the_action_and_fires_the_rows_key(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = RenameCommentConfirmationComponent(instance=comment)

        component.confirm()

        comment.refresh_from_db()

        assert comment.name == 'Renamed'
        assert component.__dict__['_pending_events'] == [
            {'name': 'confirmed', 'detail': {'pk': comment.pk}},
        ]

    def test_it_has_the_plain_prompt_and_needs_no_more_than_view_access(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        request = RequestFactory().get('/')
        request.user = self.super_user
        request.session = self.client.session
        component = RenameCommentConfirmationComponent(instance=comment)
        introduced = Glue.object(request, RenameCommentConfirmationComponent(instance=comment))

        html = render_to_string(component.template, {'component': component})

        assert 'Are you sure?' in html
        assert 'bi-trash' not in html
        assert introduced._resolve_required_access(
            introduced._bound_attributes['confirm'].definition.required_access
        ) == Glue.Access.VIEW

    def test_the_row_it_was_built_with_is_read_without_a_query(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = RenameCommentConfirmationComponent(instance=comment)

        with self.assertNumQueries(0):
            assert component.instance == comment
            assert component.model_name == 'Comment'
