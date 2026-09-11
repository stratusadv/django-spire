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
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'django_spire/api/page/access_list_page.html')
        assert self.test_access in response.context['api_accesses']

    def test_access_list_view_shows_user_and_no_user(self):
        linked_access = ApiAccess.objects.create(name='Linked Access', user=self.super_user)
        html = self.client.get(path=reverse('django_spire:api:page:list')).content.decode()

        assert str(linked_access.user) in html
        assert 'No User' in html
