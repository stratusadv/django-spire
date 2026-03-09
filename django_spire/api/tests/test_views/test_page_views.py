from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.api.models import ApiAccess


class ApiPageViewsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.test_access = ApiAccess.objects.create(name='Test Access')

    def test_access_list_view(self):
        response = self.client.get(path=reverse('django_spire:api:page:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django_spire/api/page/access_list_page.html')
        self.assertIn(self.test_access, response.context['api_accesses'])

    def test_access_delete_view_get(self):
        response = self.client.get(
            path=reverse(
                'django_spire:api:page:delete',
                kwargs={'pk': self.test_access.pk}
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_access_delete_view_post(self):
        response = self.client.post(
            path=reverse(
                'django_spire:api:page:delete',
                kwargs={'pk': self.test_access.pk}
            ),
            data={'should_delete': True}
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ApiAccess.objects.filter(pk=self.test_access.pk, is_deleted=False).exists())
        self.assertTrue(ApiAccess.objects.get(pk=self.test_access.pk).is_deleted)
