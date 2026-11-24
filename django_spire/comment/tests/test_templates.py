from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.urls import reverse

from django_spire.comment.models import Comment
from django_spire.core.tests.test_cases import BaseTestCase

from test_project.app.task.models import Task


class CommentItemEllipsisTemplateTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.task = Task.objects.create(name='One')

        self.comment = Comment.objects.create(
            content_type=ContentType.objects.get_for_model(Task),
            object_id=self.task.pk,
            user=self.super_user,
            information='hello',
        )

    def render(self, user) -> str:
        return render_to_string(
            'django_spire/comment/item/comment_item_ellipsis.html',
            {'comment': self.comment, 'obj': self.task, 'user': user},
        )

    def test_the_authors_menu_opens_edit_and_delete_in_a_modal(self) -> None:
        html = self.render(self.super_user)

        kwargs = {
            'comment_pk': self.comment.pk,
            'obj_pk': self.task.pk,
            'app_label': 'test_project_task',
            'model_name': 'task',
        }
        edit_url = reverse('django_spire:comment:form_content', kwargs=kwargs)
        delete_url = reverse('django_spire:comment:delete_form', kwargs=kwargs)

        assert f"Spire.modal.dispatchView('{edit_url}')" in html
        assert f"Spire.modal.dispatchView('{delete_url}')" in html

    def test_another_users_menu_has_no_edit_or_delete(self) -> None:
        other = self.super_user.__class__.objects.create(username='other')

        html = self.render(other)

        assert 'Edit' not in html
        assert 'Delete' not in html
