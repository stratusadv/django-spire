from __future__ import annotations

from django.urls import reverse
from django_glue.templatetags.django_glue import js_url

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_statistic,
    create_test_statistic_group,
)
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

    def test_detail_view(self):
        response = self.client.get(
            path=reverse('django_spire:metric:domain:page:detail', kwargs={'pk': self.domain.pk})
        )
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'django_spire/metric/domain/page/detail_page.html')
        assert self.domain == response.context['domain']
        assert self.subdomain in response.context['subdomains']

    def test_detail_view_subdomain_links_use_glue_item_state(self):
        response = self.client.get(
            path=reverse('django_spire:metric:domain:page:detail', kwargs={'pk': self.domain.pk})
        )
        assert response.status_code == 200

        html = response.content.decode()
        for url_name in (
            'django_spire:metric:domain:page:subdomain_detail',
            'django_spire:metric:domain:form:subdomain_form',
        ):
            href = str(js_url(url_name, domain_pk='item.domain_id', pk='item.id'))
            assert f':href="{href}"' in html

        delete_link = (
            str(
                js_url(
                    'django_spire:metric:domain:form:delete_subdomain',
                    domain_pk='item.domain_id',
                    pk='item.id',
                    template_literal=True,
                )
            )
            + '?return_url='
            + str(
                js_url(
                    'django_spire:metric:domain:page:detail',
                    pk='item.domain_id',
                    template_literal=True,
                )
            )
        )
        assert f':href="`{delete_link}`"' in html


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

    def test_subdomain_detail_view_lists_domain_statistics(self):
        group = create_test_statistic_group(domain=self.domain)
        statistic = create_test_statistic(group=group)

        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:page:subdomain_detail',
                kwargs={'pk': self.subdomain.pk, 'domain_pk': self.domain.pk},
            )
        )
        assert response.status_code == 200
        assert statistic in response.context['statistics']

        href = reverse(
            'django_spire:metric:domain:statistic:page:detail', kwargs={'pk': statistic.pk}
        )
        assert f'href="{href}"' in response.content.decode()
        assert f'{group.name} / {statistic.name}' in response.content.decode()
