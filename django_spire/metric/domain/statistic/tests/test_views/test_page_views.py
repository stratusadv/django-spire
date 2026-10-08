from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils import timezone

from django_spire.auth.user.tests.factories import create_user
from django_spire.conf import settings
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.models import StatisticValue
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)
from django_spire.metric.visual.tests.factories import create_test_visual


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
        assert 'Glue.querySet.groups' in response.content.decode()

    def test_group_list_view_uses_glue_groups_scroll(self):
        response = self.client.get(
            path=reverse('django_spire:metric:domain:statistic:page:group_list')
        )
        assert response.status_code == 200

        html = response.content.decode()
        href = (
            f'`'
            f'{reverse("django_spire:metric:domain:statistic:page:group_detail", kwargs={"pk": 0})}'
            f"`.replace('0', item.id)"
        )
        assert f':href="{href}"' in html

    def test_group_list_view_shows_storage_details_button(self):
        response = self.client.get(
            path=reverse('django_spire:metric:domain:statistic:page:group_list')
        )

        href = reverse('django_spire:metric:domain:statistic:page:storage')
        assert f'href="{href}"' in response.content.decode()

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
        assert '<th class="text-end fw-medium">Value</th>' in content
        assert 'text-end' in content

    def test_detail_view_links_sub_domains_to_subdomain_detail(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:page:detail', kwargs={'pk': self.statistic.pk}
            )
        )
        assert response.status_code == 200

        href = reverse(
            'django_spire:metric:domain:page:subdomain_detail',
            kwargs={'domain_pk': self.domain.pk, 'pk': self.sub_domain.pk},
        )
        assert f'href="{href}"' in response.content.decode()

    def test_detail_view_lists_tied_visuals(self):
        visual = create_test_visual(statistic=self.statistic)

        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:page:detail', kwargs={'pk': self.statistic.pk}
            )
        )
        assert response.status_code == 200
        assert visual in list(response.context['visuals'])

        href = reverse('django_spire:metric:visual:page:detail', kwargs={'pk': visual.pk})
        assert f'href="{href}"' in response.content.decode()


class StatisticStoragePageViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def _storage_url(self) -> str:
        return reverse('django_spire:metric:domain:statistic:page:storage')

    def test_storage_view_counts_stored_values(self):
        for _ in range(2):
            self.statistic.services.processor.add_value(
                reference='/home/', value=1, sub_domain=self.sub_domain
            )
        other_statistic = create_test_statistic(group=self.group, name='other_statistic')
        other_statistic.services.processor.add_value(
            reference='/home/', value=1, sub_domain=self.sub_domain
        )

        response = self.client.get(path=self._storage_url())

        assert response.status_code == 200
        self.assertTemplateUsed(
            response, 'django_spire/metric/domain/statistic/page/storage_page.html'
        )
        assert response.context['value_total'] == 3
        statistics = {statistic.pk: statistic for statistic in response.context['statistics']}
        assert statistics[self.statistic.pk].value_count == 2
        assert statistics[other_statistic.pk].value_count == 1
        ordered_pks = [statistic.pk for statistic in response.context['statistics']]
        assert ordered_pks[0] == self.statistic.pk

        detail_href = reverse(
            'django_spire:metric:domain:statistic:page:detail', kwargs={'pk': self.statistic.pk}
        )
        group_detail_href = reverse(
            'django_spire:metric:domain:statistic:page:group_detail', kwargs={'pk': self.group.pk}
        )
        domain_detail_href = reverse(
            'django_spire:metric:domain:page:detail', kwargs={'pk': self.domain.pk}
        )
        content = response.content.decode()
        assert f'href="{detail_href}"' in content
        assert f'href="{group_detail_href}"' in content
        assert f'href="{domain_detail_href}"' in content

    def test_storage_view_shows_prune_context(self):
        retention_days = settings.DJANGO_SPIRE_METRIC_RETENTION_DAYS

        if retention_days and retention_days > 0:
            self.statistic.services.processor.add_value(
                reference='/home/',
                value=1,
                sub_domain=self.sub_domain,
                value_timestamp=timezone.now() - timedelta(days=retention_days + 1),
            )
        self.statistic.services.processor.add_value(
            reference='/home/', value=1, sub_domain=self.sub_domain
        )

        response = self.client.get(path=self._storage_url())

        assert response.status_code == 200
        assert response.context['retention_days'] == retention_days
        assert response.context['tracking_values_max'] == (
            settings.DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX
        )
        if retention_days and retention_days > 0:
            assert response.context['prune_eligible_count'] == 1
        else:
            assert response.context['prune_eligible_count'] == 0
        assert isinstance(response.context['value_size_gb'], float)
        assert response.context['value_size_gb'] >= 0

    def test_storage_view_formats_counts_with_thousands_commas(self):
        StatisticValue.objects.bulk_create(
            [
                StatisticValue(
                    statistic=self.statistic,
                    sub_domain=self.sub_domain,
                    reference=f'reference_{index}',
                    value=1,
                )
                for index in range(1001)
            ]
        )

        response = self.client.get(path=self._storage_url())

        assert response.status_code == 200
        assert '<td class="text-end">1,001</td>' in response.content.decode()

    def test_storage_view_denied_without_permission(self):
        self.client.force_login(create_user(username='storage_view_denied_user'))

        response = self.client.get(path=self._storage_url())

        assert response.status_code == 302
        assert response.url.startswith(reverse('django_spire:auth:admin:login'))

    def test_storage_view_allowed_with_permission(self):
        user = create_user(username='storage_view_allowed_user')
        user.user_permissions.add(
            Permission.objects.get(
                codename='view_statistic', content_type__app_label='django_spire_metric_domain'
            )
        )
        self.client.force_login(user)

        response = self.client.get(path=self._storage_url())

        assert response.status_code == 200
