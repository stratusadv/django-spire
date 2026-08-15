from __future__ import annotations

from django.urls import reverse

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.models import AuthUser
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class UserPageViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.user = create_user(
            username='testuser', first_name='Test', last_name='User', email='test@example.com'
        )

    def test_list_view_requires_permission(self) -> None:
        normal_user = create_user(username='normaluser')
        self.client.force_login(normal_user)
        response = self.client.get(reverse('django_spire:auth:user:page:list'))
        assert response.status_code == 403

    def test_list_view_with_permission(self) -> None:
        response = self.client.get(reverse('django_spire:auth:user:page:list'))
        assert response.status_code == 200

    def test_list_view_context_contains_users(self) -> None:
        response = self.client.get(reverse('django_spire:auth:user:page:list'))
        assert 'active_users' in response.context
        assert 'inactive_users' in response.context

    def test_list_view_separates_active_inactive(self) -> None:
        inactive_user = create_user(username='inactiveuser', is_active=False)
        response = self.client.get(reverse('django_spire:auth:user:page:list'))
        active_ids = [u.pk for u in response.context['active_users']]
        inactive_ids = [u.pk for u in response.context['inactive_users']]
        assert inactive_user.pk in inactive_ids
        assert inactive_user.pk not in active_ids

    def test_detail_view_requires_permission(self) -> None:
        normal_user = create_user(username='normaluser')
        self.client.force_login(normal_user)
        response = self.client.get(
            reverse('django_spire:auth:user:page:detail', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 403

    def test_detail_view_with_permission(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:page:detail', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 200

    def test_detail_view_context_contains_user(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:page:detail', kwargs={'pk': self.user.pk})
        )
        assert 'user' in response.context

    def test_detail_view_context_contains_groups(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:page:detail', kwargs={'pk': self.user.pk})
        )
        assert 'group_list' in response.context

    def test_detail_view_context_contains_permissions(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:page:detail', kwargs={'pk': self.user.pk})
        )
        assert 'user_perm_data' in response.context

    def test_detail_view_404_for_nonexistent_user(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:page:detail', kwargs={'pk': 99999})
        )
        assert response.status_code == 404

    def test_list_view_contains_active_user(self) -> None:
        response = self.client.get(reverse('django_spire:auth:user:page:list'))
        active_ids = [u.pk for u in response.context['active_users']]
        assert self.user.pk in active_ids

    def test_list_view_context_contains_counts(self) -> None:
        create_user(username='inactiveuser', is_active=False)
        response = self.client.get(reverse('django_spire:auth:user:page:list'))
        assert response.context['active_user_count'] == len(response.context['active_users'])
        assert response.context['inactive_user_count'] == len(response.context['inactive_users'])

    def test_detail_view_with_groups(self) -> None:
        group = AuthGroup.objects.create(name='Test Group')
        self.user.groups.add(group)
        response = self.client.get(
            reverse('django_spire:auth:user:page:detail', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 200
        assert group in response.context['group_list']

    def test_detail_view_context_contains_group_permission_data(self) -> None:
        group = AuthGroup.objects.create(name='Test Group')
        self.user.groups.add(group)
        response = self.client.get(
            reverse('django_spire:auth:user:page:detail', kwargs={'pk': self.user.pk})
        )
        assert 'group_list_permission_data' in response.context

    def test_list_view_multiple_users(self) -> None:
        create_user(username='user1', first_name='User', last_name='One')
        create_user(username='user2', first_name='User', last_name='Two')
        response = self.client.get(reverse('django_spire:auth:user:page:list'))
        assert len(response.context['active_users']) >= 2


class UserFormViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.user = create_user(
            username='testuser', first_name='Test', last_name='User', email='test@example.com'
        )

    def test_create_form_view_get(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:form', kwargs={'pk': 0})
        )
        assert response.status_code == 200

    def test_create_form_view_post_renders_page(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:form', kwargs={'pk': 0}),
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'is_active': True,
            },
        )
        assert response.status_code == 200

    def test_create_form_view_post_does_not_save_user(self) -> None:
        self.client.post(
            reverse('django_spire:auth:user:form:form', kwargs={'pk': 0}),
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'is_active': True,
            },
        )
        assert not AuthUser.objects.filter(email='newuser@example.com').exists()

    def test_create_form_requires_permission(self) -> None:
        normal_user = create_user(username='normaluser')
        self.client.force_login(normal_user)
        response = self.client.get(
            reverse('django_spire:auth:user:form:form', kwargs={'pk': 0})
        )
        assert response.status_code == 403

    def test_update_form_view_get(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:form', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 200

    def test_update_form_view_unknown_pk_renders_create_page(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:form', kwargs={'pk': 99999})
        )
        assert response.status_code == 200

    def test_update_form_requires_permission(self) -> None:
        normal_user = create_user(username='normaluser')
        self.client.force_login(normal_user)
        response = self.client.get(
            reverse('django_spire:auth:user:form:form', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 403

    def test_group_form_view_get(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 200

    def test_group_form_view_post_renders_page(self) -> None:
        group = AuthGroup.objects.create(name='Test Group')
        response = self.client.post(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk}),
            data={'groups': [group.pk]},
        )
        assert response.status_code == 200

    def test_group_form_view_post_does_not_save_groups(self) -> None:
        group = AuthGroup.objects.create(name='Test Group')
        self.client.post(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk}),
            data={'groups': [group.pk]},
        )
        self.user.refresh_from_db()
        assert group not in self.user.groups.all()

    def test_group_form_view_404(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': 99999})
        )
        assert response.status_code == 404

    def test_group_form_requires_permission(self) -> None:
        normal_user = create_user(username='normaluser')
        self.client.force_login(normal_user)
        response = self.client.get(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 403

    def test_group_form_view_post_invalid_group_id(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk}),
            data={'groups': [99999]},
        )
        assert response.status_code == 200

    def test_group_form_view_context_contains_user(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk})
        )
        assert response.context['user'].pk == self.user.pk

    def test_update_form_view_post_renders_page(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:form', kwargs={'pk': self.user.pk}),
            data={
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@example.com',
                'is_active': True,
            },
        )
        assert response.status_code == 200


class UserResetPasswordViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.user = create_user(
            username='resetuser', first_name='Reset', last_name='User', email='reset@example.com'
        )

    def test_reset_password_view_get_returns_200(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:reset_password', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 200

    def test_reset_password_view_get_shows_confirmation(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:reset_password', kwargs={'pk': self.user.pk})
        )
        assert response.context['password_reset_complete'] is False

    def test_reset_password_view_get_contains_user_in_context(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:reset_password', kwargs={'pk': self.user.pk})
        )
        assert 'user' in response.context
        assert response.context['user'].pk == self.user.pk

    def test_reset_password_view_post_resets_password(self) -> None:
        old_password_hash = self.user.password

        response = self.client.post(
            reverse('django_spire:auth:user:form:reset_password', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 200

        self.user.refresh_from_db()
        assert self.user.password != old_password_hash

    def test_reset_password_view_post_shows_new_password_in_context(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:reset_password', kwargs={'pk': self.user.pk})
        )
        assert response.context['password_reset_complete'] is True
        assert 'new_password' in response.context
        assert len(response.context['new_password']) == 8

    def test_reset_password_view_post_new_password_is_valid(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:reset_password', kwargs={'pk': self.user.pk})
        )
        password = response.context['new_password']
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)

    def test_reset_password_view_requires_permission(self) -> None:
        normal_user = create_user(username='normaluser')
        self.client.force_login(normal_user)
        response = self.client.get(
            reverse('django_spire:auth:user:form:reset_password', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 403

    def test_reset_password_view_404_for_nonexistent_user(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:reset_password', kwargs={'pk': 99999})
        )
        assert response.status_code == 404
