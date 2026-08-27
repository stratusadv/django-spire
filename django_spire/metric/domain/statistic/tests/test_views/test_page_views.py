from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

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
            reference='/home/',
            value=1,
            sub_domain=self.sub_domain,
            value_timestamp=timezone.now() - timedelta(hours=2),
        )
        self.statistic.services.processor.add_value(
            reference='/home/', value=2, sub_domain=self.sub_domain
        )
        self.statistic.services.processor.add_value(
            reference='/home/',
            value=3,
            sub_domain=self.sub_domain,
            value_timestamp=timezone.now() - timedelta(hours=5),
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
        values = response.context['values']
        assert [value.value for value in values] == [Decimal(2), Decimal(1), Decimal(3)]

    def test_detail_view_caps_values(self):
        for index in range(150):
            self.statistic.services.processor.add_value(
                reference='/home/',
                value=Decimal(index),
                sub_domain=self.sub_domain,
                value_timestamp=timezone.now() - timedelta(seconds=index),
            )
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:page:detail', kwargs={'pk': self.statistic.pk}
            )
        )
        assert response.status_code == 200
        values = list(response.context['values'])
        assert len(values) == 100
        assert values[0].value == 0
        assert values[-1].value == 99

    def test_detail_view_renders_right_aligned_values(self):
        self.statistic.services.processor.add_value(
            reference='/home/', value=1, sub_domain=self.sub_domain
        )
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:page:detail', kwargs={'pk': self.statistic.pk}
            )
        )
        content = response.content.decode()
        assert '<th class="text-end">Value</th>' in content
        assert 'text-end' in content
