from __future__ import annotations

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from django_spire.auth.user.models import AuthUser
from django_spire.comment.models import Comment
from django_spire.comment.utils import (
    find_user_list_from_content_type,
    generate_comment_user_list_data,
    parse_user_id_to_int_list,
)
from django_spire.core.tests.test_cases import BaseTestCase


class TestGenerateCommentUserListData(BaseTestCase):
    def test_single_user(self) -> None:
        self.super_user.first_name = 'Test'
        self.super_user.last_name = 'User'
        self.super_user.save()
        user_list = [self.super_user]
        data = generate_comment_user_list_data(user_list)
        assert len(data) == 1
        assert data[0]['full_name'] == 'Test_User'
        assert data[0]['id'] == self.super_user.pk

    def test_empty_list(self) -> None:
        data = generate_comment_user_list_data([])
        assert data == []

    def test_multiple_users(self) -> None:
        self.super_user.first_name = 'Test'
        self.super_user.last_name = 'User'
        self.super_user.save()
        other_user = AuthUser.objects.create_user(
            username='other',
            first_name='Other',
            last_name='User'
        )
        user_list = [self.super_user, other_user]
        data = generate_comment_user_list_data(user_list)
        assert len(data) == 2
        full_names = [d['full_name'] for d in data]
        assert 'Test_User' in full_names
        assert 'Other_User' in full_names


class TestParseUserIdToIntList(BaseTestCase):
    def test_multiple_ids(self) -> None:
        other_user = AuthUser.objects.create_user(username='other')
        user_id_str = f'{self.super_user.pk},{other_user.pk}'
        users = parse_user_id_to_int_list(user_id_str)
        assert self.super_user in users
        assert other_user in users

    def test_single_id(self) -> None:
        user_id_str = str(self.super_user.pk)
        users = parse_user_id_to_int_list(user_id_str)
        assert self.super_user in users
        assert users.count() == 1


class TestFindUserListFromContentType(BaseTestCase):
    def test_find_users_with_permission(self) -> None:
        content_type = ContentType.objects.get_for_model(Comment)
        permission = Permission.objects.get(
            content_type=content_type,
            codename='view_comment'
        )
        group = Group.objects.create(name='test_group')
        group.permissions.add(permission)
        self.super_user.groups.add(group)

        users = find_user_list_from_content_type('django_spire_comment', 'comment')
        assert self.super_user in users

    def test_excludes_users_without_permission(self) -> None:
        other_user = AuthUser.objects.create_user(username='other')
        content_type = ContentType.objects.get_for_model(Comment)
        permission = Permission.objects.get(
            content_type=content_type,
            codename='view_comment'
        )
        group = Group.objects.create(name='test_group')
        group.permissions.add(permission)
        self.super_user.groups.add(group)

        users = find_user_list_from_content_type('django_spire_comment', 'comment')
        assert self.super_user in users
        assert other_user not in users
