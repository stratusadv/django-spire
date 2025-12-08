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
            username='testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com'
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
        assert 'active_user_list' in response.context
        assert 'inactive_user_list' in response.context

    def test_list_view_separates_active_inactive(self) -> None:
        inactive_user = create_user(username='inactiveuser', is_active=False)
        response = self.client.get(reverse('django_spire:auth:user:page:list'))
        active_ids = [u.pk for u in response.context['active_user_list']]
        inactive_ids = [u.pk for u in response.context['inactive_user_list']]
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


class UserFormViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )

    def test_register_form_view_get(self) -> None:
        response = self.client.get(reverse('django_spire:auth:user:form:register'))
        assert response.status_code == 200

    def test_register_form_view_post_creates_user(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:register'),
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        assert response.status_code == 302
        assert AuthUser.objects.filter(email='newuser@example.com').exists() is True

    def test_register_form_view_post_invalid_password(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:register'),
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'short'
            }
        )
        assert response.status_code == 200
        assert AuthUser.objects.filter(email='newuser@example.com').exists() is False

    def test_register_form_view_post_invalid_email(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:register'),
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'invalid-email',
                'password': 'securepassword123'
            }
        )
        assert response.status_code == 200

    def test_register_form_requires_permission(self) -> None:
        normal_user = create_user(username='normaluser')
        self.client.force_login(normal_user)
        response = self.client.get(reverse('django_spire:auth:user:form:register'))
        assert response.status_code == 403

    def test_update_form_view_get(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:update', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 200

    def test_update_form_view_404(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:update', kwargs={'pk': 99999})
        )
        assert response.status_code == 404

    def test_update_form_requires_permission(self) -> None:
        normal_user = create_user(username='normaluser')
        self.client.force_login(normal_user)
        response = self.client.get(
            reverse('django_spire:auth:user:form:update', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 403

    def test_group_form_view_get(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk})
        )
        assert response.status_code == 200

    def test_group_form_view_post_updates_groups(self) -> None:
        group = AuthGroup.objects.create(name='Test Group')
        response = self.client.post(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk}),
            data={'group_list': [group.pk]}
        )
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert group in self.user.groups.all()

    def test_group_form_view_post_multiple_groups(self) -> None:
        group1 = AuthGroup.objects.create(name='Group 1')
        group2 = AuthGroup.objects.create(name='Group 2')
        response = self.client.post(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk}),
            data={'group_list': [group1.pk, group2.pk]}
        )
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert group1 in self.user.groups.all()
        assert group2 in self.user.groups.all()

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
