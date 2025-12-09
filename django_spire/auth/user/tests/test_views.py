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

    def test_list_view_contains_active_user(self) -> None:
        response = self.client.get(reverse('django_spire:auth:user:page:list'))
        active_ids = [u.pk for u in response.context['active_user_list']]
        assert self.user.pk in active_ids

    def test_list_view_pagination(self) -> None:
        response = self.client.get(reverse('django_spire:auth:user:page:list'))
        assert 'active_user_list' in response.context
        assert hasattr(response.context['active_user_list'], 'paginator')

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
        assert len(response.context['active_user_list']) >= 2


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
        assert AuthUser.objects.filter(email='newuser@example.com').exists()

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
        assert not AuthUser.objects.filter(email='newuser@example.com').exists()

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

    def test_register_form_view_post_empty_password(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:register'),
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': ''
            }
        )
        assert response.status_code == 200

    def test_register_form_view_post_empty_email(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:register'),
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': '',
                'password': 'securepassword123'
            }
        )
        assert response.status_code == 200

    def test_register_form_view_post_unicode_names(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:register'),
            data={
                'first_name': 'Tëst',
                'last_name': 'Üsér',
                'email': 'unicode@example.com',
                'password': 'securepassword123'
            }
        )
        assert response.status_code == 302
        user = AuthUser.objects.get(email='unicode@example.com')
        assert user.first_name == 'Tëst'
        assert user.last_name == 'Üsér'

    def test_group_form_view_post_removes_existing_groups(self) -> None:
        group1 = AuthGroup.objects.create(name='Group 1')
        group2 = AuthGroup.objects.create(name='Group 2')
        self.user.groups.add(group1)

        response = self.client.post(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk}),
            data={'group_list': [group2.pk]}
        )
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert group1 not in self.user.groups.all()
        assert group2 in self.user.groups.all()

    def test_group_form_view_post_invalid_group_id(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk}),
            data={'group_list': [99999]}
        )
        assert response.status_code == 200

    def test_register_redirects_after_success(self) -> None:
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
        assert 'list' in response.url or 'user' in response.url

    def test_group_form_redirects_after_success(self) -> None:
        group = AuthGroup.objects.create(name='Test Group')
        response = self.client.post(
            reverse('django_spire:auth:user:form:group_form', kwargs={'pk': self.user.pk}),
            data={'group_list': [group.pk]}
        )
        assert response.status_code == 302
        assert str(self.user.pk) in response.url

    def test_update_form_view_post_updates_user(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:update', kwargs={'pk': self.user.pk}),
            data={
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@example.com',
                'is_active': True
            }
        )
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert self.user.first_name == 'Updated'
        assert self.user.last_name == 'Name'
        assert self.user.email == 'updated@example.com'

    def test_update_form_view_post_deactivates_user(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:user:form:update', kwargs={'pk': self.user.pk}),
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'is_active': False
            }
        )
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert not self.user.is_active

    def test_register_form_adds_to_all_users_group(self) -> None:
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
        user = AuthUser.objects.get(email='newuser@example.com')
        group_names = [g.name for g in user.groups.all()]
        assert 'All Users' in group_names
