from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.forms import ModelForm
from django.test import RequestFactory
from django_glue import Glue

from django_spire.core.glue.components import ModelFormComponent
from django_spire.core.glue.components.confirmation import ModelDeleteConfirmationComponent
from django_spire.core.glue.components.scroll import (
    ComponentItemFormOptions,
    ModelCrudScrollComponent,
    PageItemFormOptions,
)
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.comment.models import CommentExample
from test_project.app.comment.tests.factories import create_test_comment_example

if TYPE_CHECKING:
    from django.db.models import QuerySet

FORM_TEMPLATE = 'task/component/task_form_modal.html'


class CommentForm(ModelForm):
    class Meta:
        model = CommentExample
        fields = ('name',)


class FormlessCommentCrudScrollComponent(ModelCrudScrollComponent):
    fields = ('name',)

    def get_queryset(self) -> QuerySet[CommentExample]:
        return CommentExample.objects.order_by('name')


class CommentCrudScrollComponent(FormlessCommentCrudScrollComponent):
    item_form_options = ComponentItemFormOptions(form_class=CommentForm, template=FORM_TEMPLATE)


class PagedCommentCrudScrollComponent(FormlessCommentCrudScrollComponent):
    item_form_options = PageItemFormOptions('order:update', create_url_name='order:create')


class ArchiveCommentConfirmationComponent(ModelDeleteConfirmationComponent):
    pass


class ArchivingCommentCrudScrollComponent(CommentCrudScrollComponent):
    delete_component = ArchiveCommentConfirmationComponent


class UndeletableCommentCrudScrollComponent(CommentCrudScrollComponent):
    delete_component = None


class KeptCommentCrudScrollComponent(CommentCrudScrollComponent):
    def get_queryset(self) -> QuerySet[CommentExample]:
        return CommentExample.objects.filter(name__startswith='Kept').order_by('name')


class ModelCrudScrollComponentTestCase(BaseTestCase):
    def test_the_delete_confirmation_holds_the_row_by_default(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        confirmation = CommentCrudScrollComponent().delete_confirmation(pk=comment.pk)

        assert type(confirmation) is ModelDeleteConfirmationComponent
        assert confirmation.model_obj == comment

    def test_confirming_the_delete_confirmation_soft_deletes_the_row(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        CommentCrudScrollComponent().delete_confirmation(pk=comment.pk).confirm()

        comment.refresh_from_db()

        assert comment.is_deleted is True

    def test_a_declared_delete_component_is_used_in_its_place(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        confirmation = ArchivingCommentCrudScrollComponent().delete_confirmation(pk=comment.pk)

        assert type(confirmation) is ArchiveCommentConfirmationComponent
        assert confirmation.model_obj == comment

    def test_no_delete_component_refuses_to_delete(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        with pytest.raises(PermissionDenied, match='UndeletableCommentCrudScrollComponent'):
            UndeletableCommentCrudScrollComponent().delete_confirmation(pk=comment.pk)

    def test_the_item_form_is_built_from_the_component_options(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = CommentCrudScrollComponent()

        create_form = component.item_form()
        edit_form = component.item_form(pk=comment.pk)

        assert type(create_form) is ModelFormComponent
        assert create_form.form_class is CommentForm
        assert create_form.model.instance.pk is None
        assert edit_form.model.instance == comment

    def test_a_list_without_component_options_refuses_to_build_a_form(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        for component_class in (
            FormlessCommentCrudScrollComponent,
            PagedCommentCrudScrollComponent,
        ):
            with pytest.raises(PermissionDenied, match=component_class.__name__):
                component_class().item_form()

            with pytest.raises(PermissionDenied, match=component_class.__name__):
                component_class().item_form(pk=comment.pk)

    def test_a_row_outside_the_queryset_cannot_be_edited_or_deleted(self) -> None:
        kept = create_test_comment_example(name='Kept Notes')
        dropped = create_test_comment_example(name='Dropped Notes')
        component = KeptCommentCrudScrollComponent()

        assert component.delete_confirmation(pk=kept.pk).model_obj == kept
        assert component.item_form(pk=kept.pk).model.instance == kept

        with pytest.raises(CommentExample.DoesNotExist):
            component.delete_confirmation(pk=dropped.pk)

        with pytest.raises(CommentExample.DoesNotExist):
            component.item_form(pk=dropped.pk)

    def test_checking_that_a_row_can_be_edited_costs_one_query(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = CommentCrudScrollComponent()

        with self.assertNumQueries(1):
            component.item_form(pk=comment.pk)

    def test_each_action_needs_its_access_and_hands_down_the_lists(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        request = RequestFactory().get('/')
        request.user = self.super_user
        request.session = self.client.session
        component = Glue.object(request, CommentCrudScrollComponent(access=Glue.Access.DELETE))
        required_access = {
            name: component._resolve_required_access(
                component._bound_attributes[name].definition.required_access
            )
            for name in ('delete_confirmation', 'item_form')
        }

        assert required_access == {
            'delete_confirmation': Glue.Access.DELETE,
            'item_form': Glue.Access.CHANGE,
        }
        assert component.delete_confirmation(pk=comment.pk).access == Glue.Access.DELETE
        assert component.item_form(pk=comment.pk).access == Glue.Access.DELETE

    def test_item_form_options_of_another_kind_are_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='item_form_options must be'):

            class MisconfiguredCrudScrollComponent(FormlessCommentCrudScrollComponent):
                item_form_options = CommentForm
