from __future__ import annotations

from django.urls import reverse
from django_glue.templatetags.django_glue import js_url

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.tests.factories import create_test_statistic, create_test_statistic_group
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
        assert 'Glue.querySet.domains' in response.content.decode()

    def test_detail_view(self):
        response = self.client.get(
            path=reverse('django_spire:metric:domain:page:detail', kwargs={'pk': self.domain.pk})
        )
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'django_spire/metric/domain/page/detail_page.html')
        assert self.domain == response.context['domain']
        assert 'Glue.querySet.subdomains' in response.content.decode()

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
            + str(js_url('django_spire:metric:domain:page:detail', pk='item.domain_id', template_literal=True))
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
        assert response.context['group'].pk == 0

        html = response.content.decode()
        group_href = reverse('django_spire:metric:domain:statistic:page:group_detail', kwargs={'pk': group.pk})
        href = reverse('django_spire:metric:domain:statistic:page:detail', kwargs={'pk': statistic.pk})
        assert f'href="{group_href}"' in html
        assert f'href="{href}"' in html
        assert group.name in html
        assert statistic.name in html

    def test_subdomain_detail_view_group_uses_create_url(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:page:subdomain_detail',
                kwargs={'pk': self.subdomain.pk, 'domain_pk': self.domain.pk},
            )
        )
        assert response.status_code == 200
        assert response.context['group'].pk == 0

        create_href = reverse('django_spire:metric:domain:statistic:form:create', kwargs={'group_pk': 0})
        assert f'href="{create_href}"' in response.content.decode()


class OrphanBadgeViewTestCase(BaseTestCase):
    BADGE_TITLE = 'Not present in any configured Metric registry as of the last metric_build run.'

    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.subdomain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def _set_orphaned(self, *objs: object) -> None:
        for obj in objs:
            obj.is_orphaned = True
            obj.save()

    def _badge_count(self, html: str) -> int:
        return html.count(self.BADGE_TITLE)

    def test_domain_detail_card_shows_orphan_badge(self):
        url = reverse('django_spire:metric:domain:page:detail', kwargs={'pk': self.domain.pk})

        html = self.client.get(url).content.decode()
        # One badge comes from the Alpine sub-domain scroll row template.
        assert self._badge_count(html) == 1

        self._set_orphaned(self.domain)
        html = self.client.get(url).content.decode()
        assert self._badge_count(html) == 2

    def test_domain_list_page_has_orphan_badge_row_markup(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:page:list'))
        html = response.content.decode()
        assert 'x-show="item.is_orphaned"' in html
        assert 'badge text-bg-warning' in html

    def test_subdomain_detail_shows_orphan_badges(self):
        url = reverse(
            'django_spire:metric:domain:page:subdomain_detail',
            kwargs={'pk': self.subdomain.pk, 'domain_pk': self.domain.pk},
        )

        assert self._badge_count(self.client.get(url).content.decode()) == 0

        self._set_orphaned(self.subdomain, self.statistic)
        html = self.client.get(url).content.decode()
        # Detail card + statistics table row.
        assert self._badge_count(html) == 2

    def test_group_detail_shows_orphan_badges(self):
        url = reverse('django_spire:metric:domain:statistic:page:group_detail', kwargs={'pk': self.group.pk})

        assert self._badge_count(self.client.get(url).content.decode()) == 0

        self._set_orphaned(self.group, self.statistic)
        html = self.client.get(url).content.decode()
        # Detail card + statistics table row.
        assert self._badge_count(html) == 2

    def test_group_list_page_has_orphan_badge_row_markup(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:statistic:page:group_list'))
        html = response.content.decode()
        assert 'x-show="item.is_orphaned"' in html
        assert 'badge text-bg-warning' in html

    def test_statistic_detail_card_shows_orphan_badge(self):
        url = reverse('django_spire:metric:domain:statistic:page:detail', kwargs={'pk': self.statistic.pk})

        assert self._badge_count(self.client.get(url).content.decode()) == 0

        self._set_orphaned(self.statistic)
        assert self._badge_count(self.client.get(url).content.decode()) == 1

    def test_storage_page_shows_orphan_badge(self):
        url = reverse('django_spire:metric:domain:statistic:page:storage')

        assert self._badge_count(self.client.get(url).content.decode()) == 0

        self._set_orphaned(self.statistic)
        assert self._badge_count(self.client.get(url).content.decode()) == 1
