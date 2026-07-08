from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.tests.factories import create_test_domain, create_test_subdomain


class DomainUrlTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_list_view_url_path(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:page:list'))
        assert response.status_code == 200

    def test_detail_view_url_path(self):
        domain = create_test_domain()
        response = self.client.get(
            path=reverse('django_spire:metric:domain:page:detail', kwargs={'pk': domain.pk})
        )
        assert response.status_code == 200


class SubDomainUrlTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_subdomain_detail_view_url_path(self):
        domain = create_test_domain()
        subdomain = create_test_subdomain(domain)
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:page:subdomain_detail',
                kwargs={'domain_pk': domain.pk, 'pk': subdomain.pk},
            )
        )
        assert response.status_code == 200
