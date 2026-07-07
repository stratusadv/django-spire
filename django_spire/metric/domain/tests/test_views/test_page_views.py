from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.tests.factories import create_test_domain, create_test_subdomain


class DomainViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.subdomain = create_test_subdomain()

    def test_list_view(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:page:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django_spire/metric/domain/page/list_page.html')
        self.assertIn(self.domain, response.context['domains'])
        self.assertIn('scroll', response.context['responsive_mode'])

    def test_detail_view(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:page:detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'django_spire/metric/domain/page/detail_page.html')
        self.assertIn(self.domain, response.context['domain'])
        self.assertIn(self.subdomain, response.context['subdomains'])


class SubDomainViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.subdomains = create_test_subdomain()

    def test_subdomain_detail_view(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:page:detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.subdomain, response.context['subdomain'])
        self.assertIn(self.subdomains.domain_id, response.context['domain_pk'])