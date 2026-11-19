from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm
from django.test import RequestFactory
from django_glue import Glue

from django_spire.core.components import ModelFormComponent
from django_spire.core.components.confirmation import ModelSetDeletedConfirmationComponent
from django_spire.core.components.scroll import ModelCrudScrollComponent
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.comment.models import CommentExample
from test_project.app.comment.tests.factories import create_test_comment_example
from test_project.app.task.models import Task

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet
    from django.http import HttpRequest


class CommentForm(ModelForm):
    class Meta:
        model = CommentExample
        fields = ('name',)


class CommentScrollComponent(ModelCrudScrollComponent):
    item_template = 'comment/item/scroll_item.html'

    def get_queryset(self) -> QuerySet[CommentExample]:
        return CommentExample.objects.order_by('name')


class CommentFormComponent(ModelFormComponent):
    template = 'task/component/task_form_modal.html'
    form_class = CommentForm


class PermittedCommentScrollComponent(Glue.ModelAccessMixin, CommentScrollComponent):
    pass


class PermittedCommentFormComponent(Glue.ModelAccessMixin, CommentFormComponent):
    pass


class TaskPermittedCommentScrollComponent(Glue.ModelAccessMixin, CommentScrollComponent):
    permission_model = Task


class PermittedCommentDeleteComponent(Glue.ModelAccessMixin, ModelSetDeletedConfirmationComponent):
    pass


class ModelAccessTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.comment = create_test_comment_example(name='Budget Review')

    def _request_for(self, *actions: str, model: type[Model] = CommentExample) -> HttpRequest:
        model_name = model._meta.model_name
        user = User.objects.create_user(username=f'{model_name}.{"_".join(actions) or "none"}')
        user.user_permissions.add(
            *Permission.objects.filter(
                content_type=ContentType.objects.get_for_model(model),
                codename__in=[f'{action}_{model_name}' for action in actions],
            )
        )

        request = RequestFactory().get('/')
        request.user = User.objects.get(pk=user.pk)
        request.session = self.client.session

        return request

    def test_each_model_component_names_the_model_it_works_on(self) -> None:
        confirmation = ModelSetDeletedConfirmationComponent(instance=self.comment)

        assert CommentScrollComponent().get_permission_model() is CommentExample
        assert CommentFormComponent().get_permission_model() is CommentExample
        assert confirmation.get_permission_model() is CommentExample

    def test_a_model_component_keeps_its_given_access_without_the_mixin(self) -> None:
        request = self._request_for('view')

        component = Glue.object(request, CommentScrollComponent(access=Glue.Access.DELETE))

        assert component.access is Glue.Access.DELETE

    def test_a_scroll_with_the_mixin_takes_the_users_access_on_its_rows(self) -> None:
        request = self._request_for('view', 'add', 'change')

        component = Glue.object(request, PermittedCommentScrollComponent())

        assert component.access is Glue.Access.CHANGE

    def test_a_permission_model_on_a_scroll_replaces_the_model_of_its_rows(self) -> None:
        request = self._request_for('view', 'add', model=Task)

        component = Glue.object(request, TaskPermittedCommentScrollComponent())

        assert component.access is Glue.Access.ADD

    def test_a_form_with_the_mixin_takes_the_users_access_on_its_model(self) -> None:
        request = self._request_for('view', 'add')

        component = Glue.object(request, PermittedCommentFormComponent())

        assert component.access is Glue.Access.ADD

    def test_a_confirmation_with_the_mixin_takes_the_users_access_on_its_row(self) -> None:
        request = self._request_for('view', 'add', 'change', 'delete')

        component = Glue.object(request, PermittedCommentDeleteComponent(instance=self.comment))

        assert component.access is Glue.Access.DELETE
