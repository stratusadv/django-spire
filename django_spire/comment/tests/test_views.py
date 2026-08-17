from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from django_spire.auth.user.models import AuthUser
from django_spire.comment.models import Comment
from django_spire.core.tests.test_cases import BaseTestCase

from test_project.app.task.models import Task


class CommentDeleteFormViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.task = Task.objects.create(name='One')

        self.comment = Comment.objects.create(
            content_type=ContentType.objects.get_for_model(Task),
            object_id=self.task.pk,
            user=self.super_user,
            information='hello',
        )

        self.url = self.delete_url(self.comment)

    def delete_url(self, comment: Comment) -> str:
        kwargs = {
            'comment_pk': comment.pk,
            'obj_pk': self.task.pk,
            'app_label': 'test_project_task',
            'model_name': 'task',
        }

        return reverse('django_spire:comment:delete_form', kwargs=kwargs)

    def test_get_renders_confirmation(self) -> None:
        response = self.client.get(self.url)

        assert response.status_code == 200

    def test_post_soft_deletes_comment(self) -> None:
        response = self.client.post(self.url, data={'should_delete': 'true'})

        assert response.status_code == 302

        self.comment.refresh_from_db()

        assert self.comment.is_deleted is True

    def test_post_without_should_delete_keeps_comment(self) -> None:
        response = self.client.post(self.url, data={'should_delete': 'false'})

        assert response.status_code == 302

        self.comment.refresh_from_db()

        assert self.comment.is_deleted is False

    def test_other_users_comment_is_not_deletable(self) -> None:
        other_user = AuthUser.objects.create_user(username='othercommenter')

        other_comment = Comment.objects.create(
            content_type=ContentType.objects.get_for_model(Task),
            object_id=self.task.pk,
            user=other_user,
            information='not yours',
        )

        response = self.client.post(
            self.delete_url(other_comment),
            data={'should_delete': 'true'},
        )

        assert response.status_code == 302

        other_comment.refresh_from_db()

        assert other_comment.is_deleted is False
