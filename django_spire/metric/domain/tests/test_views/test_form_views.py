from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.tests.factories import create_test_domain, create_test_subdomain


class DomainViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.subdomain = create_test_subdomain(domain=self.domain)

    def test_create_view(self):
        response = self.client.post(
            reverse('django_spire:metric:domain:form:create'),
            data={
                'name': self.domain.name,
                'description': self.domain.description,
                'sub_domain_description': self.domain.sub_domain_description,
            },
        )

        domain_created = Domain.objects.first()

        assert response.status_code == 302
        assert response.url == reverse('django_spire:metric:domain:page:list')
        assert domain_created == self.domain

    def test_update_view(self):
        response = self.client.post(
            reverse('django_spire:metric:domain:form:create'),
            data={
                'name': self.domain.name,
                'description': self.domain.description,
                'sub_domain_description': self.domain.sub_domain_description,
            },
        )

        domain_created = Domain.objects.first()

        assert response.status_code == 302
        assert response.url == reverse('django_spire:metric:domain:page:list')
        assert domain_created == self.domain

    def test_delete_view(self):
        pass

    def test_create_view_invalid_data(self):
        invalid_data = {'name': '', 'description': '', 'sub_domain_description': ''}

        response = self.client.post(
            reverse('django_spire:help_desk:form:create'), data=invalid_data
        )

        assert response.status_code == 200
        assert Domain.objects.count() == 1



class SubDomainViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.subdomain = create_test_subdomain(domain=self.domain)

    def test_create_subdomain_view(self):
        pass

    def test_update_subdomain_view(self):
        pass

    def test_delete_subdomain_view(self):
        pass
