from __future__ import annotations

from django.contrib.contenttypes.models import ContentType

from django_spire.comment.models import Comment
from django_spire.core.tests.test_cases import BaseTestCase


class TestCommentModel(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.content_type = ContentType.objects.get_for_model(self.super_user)
        self.comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='This is a test comment.'
        )

    def test_str(self) -> None:
        assert str(self.comment) == 'This is a ...'

    def test_str_short_information(self) -> None:
        comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Short'
        )
        assert str(comment) == 'Short...'

    def test_scrape_username_list(self) -> None:
        comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Hello @john_doe and @jane_doe'
        )
        usernames = comment.scrape_username_list()
        assert usernames == ['john_doe', 'jane_doe']

    def test_scrape_username_list_empty(self) -> None:
        usernames = self.comment.scrape_username_list()
        assert usernames == []

    def test_scrape_username_list_single(self) -> None:
        comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Hello @stratus'
        )
        usernames = comment.scrape_username_list()
        assert usernames == ['stratus']

    def test_find_user_list(self) -> None:
        comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Hello @stratus'
        )
        users = comment.find_user_list()
        assert self.super_user in users

    def test_find_user_list_empty(self) -> None:
        users = self.comment.find_user_list()
        assert users.count() == 0

    def test_update(self) -> None:
        self.comment.update('Updated information')
        self.comment.refresh_from_db()
        assert self.comment.information == 'Updated information'
        assert self.comment.is_edited is True

    def test_update_sets_is_edited(self) -> None:
        assert self.comment.is_edited is False
        self.comment.update('New content')
        assert self.comment.is_edited is True

    def test_parent_relationship(self) -> None:
        parent_comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Parent comment'
        )
        child_comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            parent=parent_comment,
            information='Child comment'
        )
        assert child_comment.parent == parent_comment
        assert child_comment in parent_comment.children.all()

    def test_default_ordering(self) -> None:
        comment1 = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='First'
        )

        comment2 = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Second'
        )

        comments = list(Comment.objects.order_by('-pk')[:2])
        assert comments == [comment2, comment1]


class TestCommentRelationships(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.content_type = ContentType.objects.get_for_model(self.super_user)
        self.comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Test comment'
        )

    def test_comment_user_relationship(self) -> None:
        assert self.comment.user == self.super_user
        assert self.comment in self.super_user.comment_list.all()

    def test_comment_content_object(self) -> None:
        assert self.comment.content_object == self.super_user
        assert self.comment.object_id == self.super_user.pk

    def test_nested_replies(self) -> None:
        parent_comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Parent'
        )
        child1 = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            parent=parent_comment,
            information='Child 1'
        )
        child2 = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            parent=parent_comment,
            information='Child 2'
        )
        assert parent_comment.children.count() == 2
        assert child1 in parent_comment.children.all()
        assert child2 in parent_comment.children.all()

    def test_cascade_delete_parent(self) -> None:
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
        child_pk = child_comment.pk
        parent_comment.delete()
        assert Comment.objects.filter(pk=child_pk).exists() is False


class TestCommentDefaults(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.content_type = ContentType.objects.get_for_model(self.super_user)
        self.comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user,
            information='Test comment'
        )

    def test_default_is_active(self) -> None:
        assert self.comment.is_active is True

    def test_default_is_deleted(self) -> None:
        assert self.comment.is_deleted is False

    def test_default_is_edited(self) -> None:
        assert self.comment.is_edited is False

    def test_default_information(self) -> None:
        comment = Comment.objects.create(
            content_type=self.content_type,
            object_id=self.super_user.pk,
            user=self.super_user
        )
        assert comment.information == ''

    def test_created_datetime_auto_set(self) -> None:
        assert self.comment.created_datetime is not None

    def test_parent_default_null(self) -> None:
        assert self.comment.parent is None
