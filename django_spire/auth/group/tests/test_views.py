from __future__ import annotations

from django.urls import reverse

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class GroupPageViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.group = AuthGroup.objects.create(name='Test Group')

    def test_list_view_requires_permission(self) -> None:
        user = create_user(username='normaluser')
        self.client.force_login(user)
        response = self.client.get(reverse('django_spire:auth:group:page:list'))
        assert response.status_code == 403

    def test_list_view_with_permission(self) -> None:
        response = self.client.get(reverse('django_spire:auth:group:page:list'))
        assert response.status_code == 200

    def test_list_view_context_contains_groups(self) -> None:
        response = self.client.get(reverse('django_spire:auth:group:page:list'))
        assert 'group_list' in response.context

    def test_list_view_contains_created_group(self) -> None:
        response = self.client.get(reverse('django_spire:auth:group:page:list'))
        group_names = [g.name for g in response.context['group_list']]
        assert 'Test Group' in group_names

    def test_detail_view_requires_permission(self) -> None:
        user = create_user(username='normaluser')
        self.client.force_login(user)
        response = self.client.get(
            reverse('django_spire:auth:group:page:detail', kwargs={'pk': self.group.pk})
        )
        assert response.status_code == 403

    def test_detail_view_with_permission(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:group:page:detail', kwargs={'pk': self.group.pk})
        )
        assert response.status_code == 200

    def test_detail_view_context_contains_group(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:group:page:detail', kwargs={'pk': self.group.pk})
        )
        assert 'group' in response.context
        assert response.context['group'] == self.group

    def test_detail_view_404_for_nonexistent_group(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:group:page:detail', kwargs={'pk': 99999})
        )
        assert response.status_code == 404

    def test_detail_view_contains_permission_data(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:group:page:detail', kwargs={'pk': self.group.pk})
        )
        assert 'permission_data' in response.context

    def test_detail_view_contains_user_lists(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:group:page:detail', kwargs={'pk': self.group.pk})
        )
        assert 'active_user_list' in response.context
        assert 'inactive_user_list' in response.context


class GroupFormViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group = AuthGroup.objects.create(name='Test Group')

    def test_add_form_view_get(self) -> None:
        response = self.client.get(reverse('django_spire:auth:group:form:add'))
        assert response.status_code == 200

    def test_add_form_view_post_creates_group(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:group:form:add'),
            data={'name': 'New Group'}
        )
        assert response.status_code == 302
        assert AuthGroup.objects.filter(name='New Group').exists() is True

    def test_add_form_view_post_invalid_name(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:group:form:add'),
            data={'name': 'All Users'}
        )
        assert response.status_code == 200
        assert AuthGroup.objects.filter(name='All Users').exists() is False

    def test_add_form_view_post_empty_name(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:group:form:add'),
            data={'name': ''}
        )
        assert response.status_code == 200

    def test_update_form_view_get(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:group:form:update', kwargs={'pk': self.group.pk})
        )
        assert response.status_code == 200

    def test_update_form_view_post_updates_group(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:group:form:update', kwargs={'pk': self.group.pk}),
            data={'name': 'Updated Group'}
        )
        assert response.status_code == 302
        self.group.refresh_from_db()
        assert self.group.name == 'Updated Group'

    def test_update_form_view_nonexistent_group_returns_200(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:group:form:update', kwargs={'pk': 99999})
        )
        assert response.status_code == 200

    def test_delete_form_view_get(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:group:form:delete', kwargs={'pk': self.group.pk})
        )
        assert response.status_code == 200

    def test_delete_form_view_404(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:group:form:delete', kwargs={'pk': 99999})
        )
        assert response.status_code == 404

    def test_user_form_view_get(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:group:form:user', kwargs={'pk': self.group.pk})
        )
        assert response.status_code == 200

    def test_user_form_view_404(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:group:form:user', kwargs={'pk': 99999})
        )
        assert response.status_code == 404

    def test_add_form_requires_permission(self) -> None:
        user = create_user(username='normaluser')
        self.client.force_login(user)
        response = self.client.get(reverse('django_spire:auth:group:form:add'))
        assert response.status_code == 403


class GroupJsonViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group = AuthGroup.objects.create(name='Test Group')

    def test_permission_form_ajax_invalid_app(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:auth:group:json:group_permission_ajax',
                kwargs={'pk': self.group.pk, 'app_name': 'invalid_app'}
            ),
            data={'perm_level': 'View'},
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 400

    def test_permission_form_ajax_valid_app(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:auth:group:json:group_permission_ajax',
                kwargs={'pk': self.group.pk, 'app_name': 'group'}
            ),
            data='{"perm_level": "View"}',
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_permission_form_ajax_requires_post(self) -> None:
        response = self.client.get(
            reverse(
                'django_spire:auth:group:json:group_permission_ajax',
                kwargs={'pk': self.group.pk, 'app_name': 'group'}
            )
        )
        assert response.status_code == 405

    def test_permission_form_ajax_404_group(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:auth:group:json:group_permission_ajax',
                kwargs={'pk': 99999, 'app_name': 'group'}
            ),
            data='{"perm_level": "View"}',
            content_type='application/json'
        )
        assert response.status_code == 404

    def test_special_role_ajax_invalid_app(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:auth:group:json:group_special_role_ajax',
                kwargs={'pk': self.group.pk, 'app_name': 'invalid_app'}
            ),
            data='{"codename": "test", "grant_special_role_access": true}',
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 400
