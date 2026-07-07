from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.tests.factories import create_test_domain, create_test_subdomain


class DomainUrlTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_create_view_url_path(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:form:create'))
        assert response.status_code == 200

    def test_update_view_url_path(self):
        domain = create_test_domain()
        response = self.client.get(
            path=reverse('django_spire:metric:domain:form:update', kwargs={'pk': domain.pk})
        )

    def test_delete_view_url_path(self):
        domain = create_test_domain()
        response = self.client.get(
            path=reverse('django_spire:metric:domain:form:delete', kwargs={'pk': domain.pk})
        )
        assert response.status_code == 200


class SubDomainUrlTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()

    def test_create_view_url_path(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:form:create_subdomain', kwargs={'domain_pk': self.domain.pk}
            )
        )
        assert response.status_code == 200

    def test_update_view_url_path(self):
        subdomain = create_test_subdomain(self.domain)
        response = self.client.get(
            path=reverse('django_spire:metric:domain:form:update_subdomain',
            kwargs={'domain_pk': self.domain.pk, 'pk': subdomain.pk}),
        )

    def test_delete_view_url_path(self):
        subdomain = create_test_subdomain(self.domain)
        response = self.client.get(
            path=reverse('django_spire:metric:domain:form:delete_subdomain',
            kwargs={'domain_pk': self.domain.pk, 'pk': subdomain.pk}),
        )
        assert response.status_code == 200
