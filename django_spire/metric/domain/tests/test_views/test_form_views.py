from __future__ import annotations

from django.test import RequestFactory
from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.forms import DomainForm, SubDomainForm
from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.tests.factories import create_test_domain, create_test_subdomain


class DomainViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.request = RequestFactory().post('/')
        self.request.user = self.super_user

    def test_create_view(self):
        response = self.client.get(
            reverse('django_spire:metric:domain:form:form', kwargs={'pk': 0})
        )

        assert response.status_code == 200
        assert Domain.objects.count() == 0

    def test_create_form_saves_domain(self):
        form = DomainForm(
            data={
                'name': 'test_domain',
                'description': 'test_domain_description',
                'sub_domain_description': 'test_domain_sub_domain_description',
            }
        )
        response = form.save_model_obj(self.request)

        domain_created = Domain.objects.first()

        assert domain_created.name == 'test_domain'
        assert domain_created.description == 'test_domain_description'
        assert domain_created.sub_domain_description == 'test_domain_sub_domain_description'
        assert response.result['redirect_url'] == reverse(
            'django_spire:metric:domain:page:detail', kwargs={'pk': domain_created.pk}
        )

    def test_update_view(self):
        domain = create_test_domain()
        response = self.client.get(
            reverse('django_spire:metric:domain:form:form', kwargs={'pk': domain.pk})
        )

        assert response.status_code == 200

    def test_update_form_saves_domain(self):
        domain = create_test_domain()

        form = DomainForm(
            data={
                'name': 'updated_domain',
                'description': 'updated_domain_description',
                'sub_domain_description': 'updated_sub_domain_description',
            },
            instance=domain,
        )
        form.save_model_obj(self.request)

        domain.refresh_from_db()
        assert domain.name == 'updated_domain'
        assert domain.description == 'updated_domain_description'
        assert domain.sub_domain_description == 'updated_sub_domain_description'

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

    def test_create_form_invalid_data(self):
        form = DomainForm(data={'name': '', 'description': '', 'sub_domain_description': ''})
        response = form.save_model_obj(self.request)

        assert response.result is None
        assert Domain.objects.count() == 0


class SubDomainViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.request = RequestFactory().post('/')
        self.request.user = self.super_user

    def test_create_subdomain_view(self):
        domain = create_test_domain()
        response = self.client.get(
            reverse(
                'django_spire:metric:domain:form:subdomain_form',
                kwargs={'domain_pk': domain.pk, 'pk': 0},
            )
        )

        assert response.status_code == 200
        assert SubDomain.objects.count() == 0

    def test_create_subdomain_form_saves_subdomain(self):
        domain = create_test_domain()

        form = SubDomainForm(
            data={
                'domain': domain.pk,
                'name': 'subdomain_name',
                'description': 'testing subdomain_description',
            }
        )
        response = form.save_model_obj(self.request)

        subdomain_created = SubDomain.objects.first()

        assert subdomain_created.domain == domain
        assert subdomain_created.name == 'subdomain_name'
        assert subdomain_created.description == 'testing subdomain_description'
        assert response.result['redirect_url'] == reverse(
            'django_spire:metric:domain:page:detail', kwargs={'pk': domain.pk}
        )

    def test_update_subdomain_view(self):
        domain = create_test_domain()
        subdomain = create_test_subdomain(domain=domain)

        response = self.client.get(
            reverse(
                'django_spire:metric:domain:form:subdomain_form',
                kwargs={'domain_pk': domain.pk, 'pk': subdomain.pk},
            )
        )

        assert response.status_code == 200

    def test_update_subdomain_form_saves_subdomain(self):
        domain = create_test_domain()
        subdomain = create_test_subdomain(domain=domain)

        form = SubDomainForm(
            data={
                'domain': domain.pk,
                'name': 'updated_subdomain',
                'description': 'updated_subdomain_description',
            },
            instance=subdomain,
        )
        form.save_model_obj(self.request)

        subdomain.refresh_from_db()
        assert subdomain.domain == domain
        assert subdomain.name == 'updated_subdomain'
        assert subdomain.description == 'updated_subdomain_description'

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

    def test_create_subdomain_form_invalid_data(self):
        form = SubDomainForm(data={'domain': '', 'name': '', 'description': ''})
        response = form.save_model_obj(self.request)

        assert response.result is None
        assert SubDomain.objects.count() == 0
