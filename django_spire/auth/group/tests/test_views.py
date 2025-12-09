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

    def test_list_view_contains_permission_data(self) -> None:
        response = self.client.get(reverse('django_spire:auth:group:page:list'))
        assert 'group_list_permission_data' in response.context

    def test_list_view_multiple_groups(self) -> None:
        AuthGroup.objects.create(name='Group 2')
        AuthGroup.objects.create(name='Group 3')
        response = self.client.get(reverse('django_spire:auth:group:page:list'))
        assert len(response.context['group_list']) >= 3

    def test_detail_view_with_users_in_group(self) -> None:
        user = create_user(username='groupmember')
        self.group.user_set.add(user)
        response = self.client.get(
            reverse('django_spire:auth:group:page:detail', kwargs={'pk': self.group.pk})
        )
        assert response.status_code == 200

    def test_detail_view_separates_active_inactive_users(self) -> None:
        active_user = create_user(username='activeuser', is_active=True)
        inactive_user = create_user(username='inactiveuser', is_active=False)
        self.group.user_set.add(active_user, inactive_user)
        response = self.client.get(
            reverse('django_spire:auth:group:page:detail', kwargs={'pk': self.group.pk})
        )
        active_ids = [u.pk for u in response.context['active_user_list']]
        inactive_ids = [u.pk for u in response.context['inactive_user_list']]
        assert active_user.pk in active_ids
        assert inactive_user.pk in inactive_ids


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
        assert AuthGroup.objects.filter(name='New Group').exists()

    def test_add_form_view_post_invalid_name(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:group:form:add'),
            data={'name': 'All Users'}
        )
        assert response.status_code == 200
        assert not AuthGroup.objects.filter(name='All Users').exists()

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

    def test_update_form_requires_permission(self) -> None:
        user = create_user(username='normaluser')
        self.client.force_login(user)
        response = self.client.get(
            reverse('django_spire:auth:group:form:update', kwargs={'pk': self.group.pk})
        )
        assert response.status_code == 403

    def test_delete_form_requires_permission(self) -> None:
        user = create_user(username='normaluser')
        self.client.force_login(user)
        response = self.client.get(
            reverse('django_spire:auth:group:form:delete', kwargs={'pk': self.group.pk})
        )
        assert response.status_code == 403

    def test_user_form_requires_permission(self) -> None:
        user = create_user(username='normaluser')
        self.client.force_login(user)
        response = self.client.get(
            reverse('django_spire:auth:group:form:user', kwargs={'pk': self.group.pk})
        )
        assert response.status_code == 403

    def test_add_form_view_post_duplicate_name(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:group:form:add'),
            data={'name': 'Test Group'}
        )
        assert response.status_code == 200

    def test_update_form_view_post_to_reserved_name(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:group:form:update', kwargs={'pk': self.group.pk}),
            data={'name': 'All Users'}
        )
        assert response.status_code == 200
        self.group.refresh_from_db()
        assert self.group.name != 'All Users'

    def test_add_form_view_post_unicode_name(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:group:form:add'),
            data={'name': 'Tëst Grøup 日本語'}
        )
        assert response.status_code == 302
        assert AuthGroup.objects.filter(name='Tëst Grøup 日本語').exists()

    def test_add_form_view_post_special_characters(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:group:form:add'),
            data={'name': 'Group & Co <Test>'}
        )
        assert response.status_code == 302

    def test_user_form_view_post_adds_users(self) -> None:
        user = create_user(username='newgroupuser')
        response = self.client.post(
            reverse('django_spire:auth:group:form:user', kwargs={'pk': self.group.pk}),
            data={'users': [user.pk]}
        )
        assert response.status_code == 302
        assert user in self.group.user_set.all()

    def test_user_form_view_post_removes_users(self) -> None:
        user = create_user(username='removeuser')
        self.group.user_set.add(user)
        response = self.client.post(
            reverse('django_spire:auth:group:form:user', kwargs={'pk': self.group.pk}),
            data={'users': []}
        )
        assert response.status_code == 302
        assert user not in self.group.user_set.all()


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

    def test_permission_form_ajax_requires_permission(self) -> None:
        user = create_user(username='normaluser')
        self.client.force_login(user)
        response = self.client.post(
            reverse(
                'django_spire:auth:group:json:group_permission_ajax',
                kwargs={'pk': self.group.pk, 'app_name': 'group'}
            ),
            data='{"perm_level": "View"}',
            content_type='application/json'
        )
        assert response.status_code == 403

    def test_special_role_ajax_requires_permission(self) -> None:
        user = create_user(username='normaluser')
        self.client.force_login(user)
        response = self.client.post(
            reverse(
                'django_spire:auth:group:json:group_special_role_ajax',
                kwargs={'pk': self.group.pk, 'app_name': 'group'}
            ),
            data='{"codename": "test", "grant_special_role_access": true}',
            content_type='application/json'
        )
        assert response.status_code == 403

    def test_permission_form_ajax_all_perm_levels(self) -> None:
        for perm_level in ['None', 'View', 'Add', 'Change', 'Delete']:
            response = self.client.post(
                reverse(
                    'django_spire:auth:group:json:group_permission_ajax',
                    kwargs={'pk': self.group.pk, 'app_name': 'group'}
                ),
                data=f'{{"perm_level": "{perm_level}"}}',
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_permission_form_ajax_invalid_perm_level_defaults_to_none(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:auth:group:json:group_permission_ajax',
                kwargs={'pk': self.group.pk, 'app_name': 'group'}
            ),
            data='{"perm_level": "InvalidLevel"}',
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 200
