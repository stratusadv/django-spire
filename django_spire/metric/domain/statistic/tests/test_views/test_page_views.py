from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)


class StatisticGroupPageViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.group = create_test_statistic_group(domain=self.domain)

    def test_group_list_view(self):
        response = self.client.get(
            path=reverse('django_spire:metric:domain:statistic:page:group_list')
        )
        assert response.status_code == 200
        self.assertTemplateUsed(
            response, 'django_spire/metric/domain/statistic/page/group_list_page.html'
        )
        assert self.group in response.context['groups']

    def test_group_detail_view(self):
        statistic = create_test_statistic(group=self.group)
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:page:group_detail',
                kwargs={'pk': self.group.pk},
            )
        )
        assert response.status_code == 200
        self.assertTemplateUsed(
            response, 'django_spire/metric/domain/statistic/page/group_detail_page.html'
        )
        assert self.group == response.context['group']
        assert statistic in response.context['statistics']


class StatisticPageViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_list_view(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:statistic:page:list'))
        assert response.status_code == 200
        self.assertTemplateUsed(
            response, 'django_spire/metric/domain/statistic/page/list_page.html'
        )
        assert self.statistic in response.context['statistics']

    def test_detail_view(self):
        self.statistic.services.processor.add_value(
            reference='/home/', value=1, sub_domain=self.sub_domain
        )
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:page:detail', kwargs={'pk': self.statistic.pk}
            )
        )
        assert response.status_code == 200
        self.assertTemplateUsed(
            response, 'django_spire/metric/domain/statistic/page/detail_page.html'
        )
        assert self.statistic == response.context['statistic']
        assert response.context['values'].count() == 1
