from __future__ import annotations

from django.contrib.contenttypes.models import ContentType

from django_spire.comment.models import Comment
from django_spire.core.tests.test_cases import BaseTestCase


class TestCommentQuerySet(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.content_type = ContentType.objects.get_for_model(self.super_user)
        self.comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Test comment'
        )

    def test_active(self) -> None:
        comments = Comment.objects.active()
        assert self.comment in comments

    def test_active_excludes_deleted(self) -> None:
        comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Deleted comment',
            is_deleted=True
        )
        comments = Comment.objects.active()
        assert comment not in comments

    def test_top_level(self) -> None:
        parent_comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Parent'
        )
        child_comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            parent=parent_comment,
            information='Child'
        )
        top_level = Comment.objects.top_level()
        assert parent_comment in top_level
        assert child_comment not in top_level

    def test_prefetch_user(self) -> None:
        comments = Comment.objects.prefetch_user()
        assert self.comment in comments

    def test_prefetch_parent(self) -> None:
        parent_comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Parent'
        )
        child_comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            parent=parent_comment,
            information='Child'
        )
        comments = Comment.objects.prefetch_parent()
        assert child_comment in comments

    def test_prefetch_replies(self) -> None:
        parent_comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Parent'
        )
        comments = Comment.objects.prefetch_replies()
        assert parent_comment in comments

    def test_chained_querysets(self) -> None:
        parent_comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Parent'
        )
        child_comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            parent=parent_comment,
            information='Child'
        )
        comments = Comment.objects.active().top_level().prefetch_user()
        assert parent_comment in comments
        assert child_comment not in comments
