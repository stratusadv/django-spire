from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.tests.factories import create_test_domain, create_test_subdomain


class DomainViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.subdomain = create_test_subdomain(domain=self.domain)

    def test_list_view(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:page:list'))
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'django_spire/metric/domain/page/list_page.html')
        assert self.domain in response.context['domains']
        assert 'scroll' in response.context['responsive_mode']

    def test_detail_view(self):
        response = self.client.get(
            path=reverse('django_spire:metric:domain:page:detail', kwargs={'pk': self.domain.pk})
        )
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'django_spire/metric/domain/page/detail_page.html')
        assert self.domain == response.context['domain']
        assert self.subdomain in response.context['subdomains']


class SubDomainViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.subdomain = create_test_subdomain(domain=self.domain)

    def test_subdomain_detail_view(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:page:subdomain_detail',
                kwargs={'pk': self.subdomain.pk, 'domain_pk': self.domain.pk},
            )
        )
        assert response.status_code == 200
        assert self.subdomain == response.context['subdomain']
        assert self.subdomain.domain.pk == response.context['domain_pk']
