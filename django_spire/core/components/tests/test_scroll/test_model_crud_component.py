from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.forms import ModelForm
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.urls import reverse
from django_glue import Glue
from django_glue.exceptions import GlueModelInstanceNotFoundError

from django_spire.core.components import (
    ComponentDeleteOptions,
    ComponentFormOptions,
    ModelFormComponent,
    PageDeleteOptions,
    PageFormOptions,
)
from django_spire.core.components.confirmation import ModelSetDeletedConfirmationComponent
from django_spire.core.components.scroll import ModelCrudScrollComponent
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
    item_form_options = ComponentFormOptions(form_class=CommentForm, template=FORM_TEMPLATE)


class PagedCommentCrudScrollComponent(FormlessCommentCrudScrollComponent):
    item_form_options = PageFormOptions('order:update', create_url_name='order:create')


class ArchiveCommentConfirmationComponent(ModelSetDeletedConfirmationComponent):
    pass


class ArchivingCommentCrudScrollComponent(CommentCrudScrollComponent):
    item_delete_options = ComponentDeleteOptions(component=ArchiveCommentConfirmationComponent)


class PageDeletingCommentCrudScrollComponent(CommentCrudScrollComponent):
    item_delete_options = PageDeleteOptions('order:delete', return_url_name='order:list')


class UndeletableCommentCrudScrollComponent(CommentCrudScrollComponent):
    item_delete_options = None


class KeptCommentCrudScrollComponent(CommentCrudScrollComponent):
    def get_queryset(self) -> QuerySet[CommentExample]:
        return CommentExample.objects.filter(name__startswith='Kept').order_by('name')


class ModelCrudScrollComponentTestCase(BaseTestCase):
    def test_the_delete_confirmation_holds_the_row_by_default(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        confirmation = CommentCrudScrollComponent().load_item_delete_confirmation(pk=comment.pk)

        assert type(confirmation) is ModelSetDeletedConfirmationComponent
        assert confirmation.instance == comment

    def test_confirming_the_delete_confirmation_soft_deletes_the_row(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        CommentCrudScrollComponent().load_item_delete_confirmation(pk=comment.pk).confirm()

        comment.refresh_from_db()

        assert comment.is_deleted is True

    def test_a_declared_delete_component_is_used_in_its_place(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        component = ArchivingCommentCrudScrollComponent()

        confirmation = component.load_item_delete_confirmation(pk=comment.pk)

        assert type(confirmation) is ArchiveCommentConfirmationComponent
        assert confirmation.instance == comment

    def test_a_list_without_component_options_refuses_to_build_a_confirmation(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        for component_class in (
            UndeletableCommentCrudScrollComponent,
            PageDeletingCommentCrudScrollComponent,
        ):
            with pytest.raises(PermissionDenied, match=component_class.__name__):
                component_class().load_item_delete_confirmation(pk=comment.pk)

    def test_page_options_reach_the_template_as_urls(self) -> None:
        paged = PagedCommentCrudScrollComponent()
        page_deleting = PageDeletingCommentCrudScrollComponent()

        paged_html = render_to_string(paged.template, {'component': paged})
        page_deleting_html = render_to_string(page_deleting.template, {'component': page_deleting})

        assert f"createUrl: '{reverse('order:create')}'" in paged_html
        assert 'editUrl: key => `/' in paged_html
        assert 'formReturnUrl' not in paged_html
        assert 'deleteUrl' not in paged_html
        assert 'deleteUrl: key => `/' in page_deleting_html
        assert f"deleteReturnUrl: '{reverse('order:list')}'" in page_deleting_html
        assert 'createUrl' not in page_deleting_html

    def test_the_item_form_is_built_from_the_component_options(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = CommentCrudScrollComponent()

        create_form = component.load_item_form()
        edit_form = component.load_item_form(pk=comment.pk)

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
                component_class().load_item_form()

            with pytest.raises(PermissionDenied, match=component_class.__name__):
                component_class().load_item_form(pk=comment.pk)

    def test_a_row_outside_the_queryset_cannot_be_edited_or_deleted(self) -> None:
        kept = create_test_comment_example(name='Kept Notes')
        dropped = create_test_comment_example(name='Dropped Notes')
        component = KeptCommentCrudScrollComponent()

        assert component.load_item_delete_confirmation(pk=kept.pk).instance == kept
        assert component.load_item_form(pk=kept.pk).model.instance == kept

        with pytest.raises(GlueModelInstanceNotFoundError) as delete_error:
            component.load_item_delete_confirmation(pk=dropped.pk)

        with pytest.raises(GlueModelInstanceNotFoundError) as edit_error:
            component.load_item_form(pk=dropped.pk)

        assert delete_error.value.status == 404
        assert delete_error.value.pk == dropped.pk
        assert edit_error.value.pk == dropped.pk

    def test_checking_that_a_row_can_be_edited_costs_one_query(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = CommentCrudScrollComponent()

        with self.assertNumQueries(1):
            component.load_item_form(pk=comment.pk)

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
            for name in ('load_item_delete_confirmation', 'load_item_form')
        }

        assert required_access == {
            'load_item_delete_confirmation': Glue.Access.DELETE,
            'load_item_form': Glue.Access.CHANGE,
        }
        assert component.load_item_delete_confirmation(pk=comment.pk).access == Glue.Access.DELETE
        assert component.load_item_form(pk=comment.pk).access == Glue.Access.DELETE

    def test_item_delete_options_of_another_kind_are_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='item_delete_options must be'):

            class MisconfiguredDeleteCrudScrollComponent(FormlessCommentCrudScrollComponent):
                item_delete_options = ArchiveCommentConfirmationComponent

    def test_item_form_options_of_another_kind_are_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='item_form_options must be'):

            class MisconfiguredCrudScrollComponent(FormlessCommentCrudScrollComponent):
                item_form_options = CommentForm
