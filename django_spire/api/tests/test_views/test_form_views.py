from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.api.models import ApiAccess


class ApiFormViewsTestCase(BaseTestCase):
    def test_access_create_form_view_get(self):
        response = self.client.get(path=reverse('django_spire:api:form:create'))
        self.assertEqual(response.status_code, 200)

    def test_access_create_form_view_post(self):
        data = {
            'name': 'New Access Key',
            'permission': 1,  # VIEW
        }
        response = self.client.post(path=reverse('django_spire:api:form:create'), data=data)
        self.assertEqual(response.status_code, 200)  # Returns template_view with success message

        self.assertTrue(ApiAccess.objects.filter(name='New Access Key').exists())
        api_access = ApiAccess.objects.get(name='New Access Key')

        self.assertIn('raw_key', response.context)
        self.assertEqual(api_access.hashed_key, response.context['api_access'].hashed_key)

        self.assertTemplateUsed(response, 'django_spire/api/page/access_created_page.html')

