from __future__ import annotations

from django.test import RequestFactory
from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain import forms
from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.tests.factories import create_test_domain, create_test_subdomain


class DomainFormViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_create_view(self):
        response = self.client.get(
            path=reverse('django_spire:metric:domain:form:form', kwargs={'pk': 0})
        )
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'django_spire/metric/domain/page/form_page.html')

    def test_create_save_model_obj(self):
        request = RequestFactory().get('/')
        request.user = self.super_user

        form = forms.DomainForm(
            data={
                'name': 'new domain',
                'description': 'new domain description',
                'sub_domain_description': 'new subdomain description',
            }
        )
        assert form.is_valid()

        response = form.save_model_obj(request)

        domain = Domain.objects.get(name='new domain')
        assert response.result['redirect_url'] == reverse(
            'django_spire:metric:domain:page:detail', kwargs={'pk': domain.pk}
        )

    def test_update_view(self):
        domain = create_test_domain()
        response = self.client.get(
            path=reverse('django_spire:metric:domain:form:form', kwargs={'pk': domain.pk})
        )
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'django_spire/metric/domain/page/form_page.html')

    def test_update_save_model_obj(self):
        domain = create_test_domain()

        request = RequestFactory().get('/')
        request.user = self.super_user

        form = forms.DomainForm(
            instance=domain,
            data={
                'name': 'updated domain',
                'description': 'updated description',
                'sub_domain_description': 'updated subdomain description',
            },
        )
        assert form.is_valid()

        response = form.save_model_obj(request)

        domain.refresh_from_db()
        assert domain.name == 'updated domain'
        assert response.result['redirect_url'] == reverse(
            'django_spire:metric:domain:page:detail', kwargs={'pk': domain.pk}
        )

    def test_delete_view(self):
        domain = create_test_domain()
        response = self.client.post(
            reverse('django_spire:metric:domain:form:delete', kwargs={'pk': domain.pk})
        )

        assert response.status_code == 302
        assert response.url == reverse('django_spire:metric:domain:page:list')

        domain.refresh_from_db()
        assert Domain.objects.count() == 1
        assert domain.is_deleted


class SubDomainFormViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()

    def test_create_view(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:form:subdomain_form',
                kwargs={'domain_pk': self.domain.pk, 'pk': 0},
            )
        )
        assert response.status_code == 200
        self.assertTemplateUsed(
            response, 'django_spire/metric/domain/page/subdomain_form_page.html'
        )

    def test_create_save_model_obj(self):
        request = RequestFactory().get('/')
        request.user = self.super_user

        form = forms.SubDomainForm(
            instance=SubDomain(domain=self.domain),
            data={'name': 'new subdomain', 'description': 'new subdomain description'},
        )
        assert form.is_valid()

        response = form.save_model_obj(request)

        subdomain = SubDomain.objects.get(name='new subdomain')
        assert subdomain.domain == self.domain
        assert response.result['redirect_url'] == reverse(
            'django_spire:metric:domain:page:detail', kwargs={'pk': self.domain.pk}
        )

    def test_update_view(self):
        subdomain = create_test_subdomain(domain=self.domain)
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:form:subdomain_form',
                kwargs={'domain_pk': self.domain.pk, 'pk': subdomain.pk},
            )
        )
        assert response.status_code == 200
        self.assertTemplateUsed(
            response, 'django_spire/metric/domain/page/subdomain_form_page.html'
        )

    def test_update_save_model_obj(self):
        subdomain = create_test_subdomain(domain=self.domain)

        request = RequestFactory().get('/')
        request.user = self.super_user

        form = forms.SubDomainForm(
            instance=subdomain,
            data={'name': 'updated subdomain', 'description': 'updated description'},
        )
        assert form.is_valid()

        response = form.save_model_obj(request)

        subdomain.refresh_from_db()
        assert subdomain.name == 'updated subdomain'
        assert subdomain.domain == self.domain
        assert response.result['redirect_url'] == reverse(
            'django_spire:metric:domain:page:detail', kwargs={'pk': self.domain.pk}
        )

    def test_delete_view(self):
        subdomain = create_test_subdomain(domain=self.domain)
        response = self.client.post(
            reverse(
                'django_spire:metric:domain:form:delete_subdomain',
                kwargs={'domain_pk': self.domain.pk, 'pk': subdomain.pk},
            )
        )

        assert response.status_code == 302
        assert response.url == reverse(
            'django_spire:metric:domain:page:detail', kwargs={'pk': self.domain.pk}
        )

        subdomain.refresh_from_db()
        assert SubDomain.objects.count() == 1
        assert subdomain.is_deleted
