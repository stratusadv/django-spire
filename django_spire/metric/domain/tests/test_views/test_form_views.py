from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.tests.factories import create_test_domain, create_test_subdomain


class DomainViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_create_view(self):
        domain = create_test_domain()
        response = self.client.post(
            reverse('django_spire:metric:domain:form:create'),
            data={
                'name': domain.name,
                'description': domain.description,
                'sub_domain_description': domain.sub_domain_description,
            },
        )

        domain_created = Domain.objects.first()

        assert response.status_code == 302
        assert response.url == reverse('django_spire:metric:domain:page:list')
        assert domain_created.name == domain.name
        assert domain_created.description == domain.description
        assert domain_created.sub_domain_description == domain.sub_domain_description

    def test_update_view(self):
        domain = create_test_domain()
        updated_domain = create_test_domain(
            name='updated_domain',
            description='updated_domain_description',
            sub_domain_description='updated_sub_domain_description',
        )

        response = self.client.post(
            reverse('django_spire:metric:domain:form:update', kwargs={'pk': domain.pk}),
            data={
                'name': updated_domain.name,
                'description': updated_domain.description,
                'sub_domain_description': updated_domain.sub_domain_description,
            },
            kwargs={'pk': domain.pk},
        )

        assert response.status_code == 302
        assert response.url == reverse('django_spire:metric:domain:page:list')

        domain.refresh_from_db()
        assert domain.name == updated_domain.name
        assert domain.description == updated_domain.description
        assert domain.sub_domain_description == updated_domain.sub_domain_description

    def test_delete_view(self):
        domain = create_test_domain()
        response = self.client.post(
            reverse('django_spire:metric:domain:form:delete', kwargs={'pk': domain.pk})
        )

        assert response.status_code == 302
        assert response.url == reverse('django_spire:metric:domain:page:list')

        domain.refresh_from_db()
        assert Domain.objects.count() == 1
        assert domain.is_deleted == True

    def test_create_view_invalid_data(self):
        invalid_data = {'name': '', 'description': '', 'sub_domain_description': ''}

        response = self.client.post(
            reverse('django_spire:metric:domain:form:create'), data=invalid_data
        )

        assert response.status_code == 200
        assert Domain.objects.count() == 0


class SubDomainViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_create_subdomain_view(self):
        domain = create_test_domain()
        subdomain = create_test_subdomain(domain=domain)
        response = self.client.post(
            reverse(
                'django_spire:metric:domain:form:create_subdomain', kwargs={'domain_pk': domain.pk}
            ),
            data={
                'domain': domain.pk,
                'name': subdomain.name,
                'description': subdomain.description,
            },
        )

        subdomain_created = SubDomain.objects.first()

        assert response.status_code == 302
        assert response.url == reverse(
            'django_spire:metric:domain:page:detail', kwargs={'pk': domain.pk}
        )
        assert subdomain_created.domain == subdomain.domain
        assert subdomain_created.name == subdomain.name
        assert subdomain_created.description == subdomain.description

    def test_update_subdomain_view(self):
        domain = create_test_domain()
        subdomain = create_test_subdomain(domain=domain)
        updated_subdomain = create_test_subdomain(
            name='updated_subdomain', description='updated_subdomain_description', domain=domain
        )

        response = self.client.post(
            reverse(
                'django_spire:metric:domain:form:update_subdomain',
                kwargs={'domain_pk': domain.pk, 'pk': subdomain.pk},
            ),
            data={
                'domain': updated_subdomain.domain,
                'name': updated_subdomain.name,
                'description': updated_subdomain.description,
            },
        )

        assert response.status_code == 302
        assert response.url == reverse(
            'django_spire:metric:domain:page:detail', kwargs={'pk': domain.pk}
        )

        subdomain.refresh_from_db()
        assert subdomain.domain == updated_subdomain.domain
        assert subdomain.name == updated_subdomain.name
        assert subdomain.description == updated_subdomain.description

    def test_delete_subdomain_view(self):
        domain = create_test_domain()
        subdomain = create_test_subdomain(domain=domain)
        response = self.client.post(
            reverse(
                'django_spire:metric:domain:form:delete_subdomain',
                kwargs={'domain_pk': domain.pk, 'pk': subdomain.pk},
            )
        )

        assert response.status_code == 302
        assert response.url == reverse(
            'django_spire:metric:domain:page:detail', kwargs={'pk': domain.pk}
        )

        subdomain.refresh_from_db()
        assert SubDomain.objects.count() == 1
        assert subdomain.is_deleted == True

    def test_create_subdomain_view_invalid_data(self):
        domain = create_test_domain()
        invalid_data = {'domain': '', 'name': '', 'description': ''}

        response = self.client.post(
            reverse(
                'django_spire:metric:domain:form:create_subdomain', kwargs={'domain_pk': domain.pk}
            ),
            data=invalid_data,
        )

        assert response.status_code == 200
        assert SubDomain.objects.count() == 0
