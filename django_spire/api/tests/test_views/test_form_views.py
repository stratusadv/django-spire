from __future__ import annotations

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from django_spire.api.models import ApiAccess
from django_spire.auth.user.models import AuthUser
from django_spire.core.tests.test_cases import BaseTestCase


class ApiFormViewsTestCase(BaseTestCase):
    def test_access_create_form_view_get(self):
        response = self.client.get(path=reverse('django_spire:api:form:create'))
        assert response.status_code == 200

    def test_access_create_form_view_post(self):
        data = {
            'name': 'New Access Key',
            'permission': 1,  # VIEW
        }
        response = self.client.post(path=reverse('django_spire:api:form:create'), data=data)
        assert response.status_code == 200  # Returns template_view with success message

        assert ApiAccess.objects.filter(name='New Access Key').exists()
        api_access = ApiAccess.objects.get(name='New Access Key')

        assert 'raw_key' in response.context
        assert api_access.hashed_key == response.context['api_access'].hashed_key

        self.assertTemplateUsed(response, 'django_spire/api/page/access_created_page.html')

    def test_access_create_form_view_superuser_sees_super_access_field(self):
        response = self.client.get(path=reverse('django_spire:api:form:create'))
        assert 'has_super_access' in response.context['form'].fields

    def test_access_create_form_view_includes_optional_user_field(self):
        response = self.client.get(path=reverse('django_spire:api:form:create'))
        user_field = response.context['form'].fields['user']
        assert not user_field.required
        assert user_field.empty_label == 'No User'
        assert 'No User' in response.content.decode()

    def test_access_create_form_view_superuser_can_grant_super_access(self):
        response = self.client.post(
            path=reverse('django_spire:api:form:create'),
            data={'name': 'Super Key', 'permission': 1, 'has_super_access': True},
        )
        assert response.status_code == 200
        assert ApiAccess.objects.get(name='Super Key').has_super_access

    def test_access_create_form_view_hides_super_access_for_non_superuser(self):
        user = AuthUser.objects.create_user(username='regular')
        permission = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(ApiAccess), codename='add_apiaccess'
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

        response = self.client.get(path=reverse('django_spire:api:form:create'))
        assert response.status_code == 200
        assert 'has_super_access' not in response.context['form'].fields

        response = self.client.post(
            path=reverse('django_spire:api:form:create'),
            data={'name': 'Rebel Key', 'permission': 1, 'has_super_access': True},
        )
        assert response.status_code == 200
        assert not ApiAccess.objects.get(name='Rebel Key').has_super_access
