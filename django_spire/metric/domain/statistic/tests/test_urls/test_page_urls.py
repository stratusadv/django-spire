from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
)


class StatisticGroupUrlTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.group = create_test_statistic_group(domain=self.domain)

    def test_group_list_view_url_path(self):
        response = self.client.get(
            path=reverse('django_spire:metric:domain:statistic:page:group_list')
        )
        assert response.status_code == 200

    def test_group_detail_view_url_path(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:page:group_detail',
                kwargs={'pk': self.group.pk},
            )
        )
        assert response.status_code == 200

    def test_group_create_view_url_path(self):
        response = self.client.get(
            path=reverse('django_spire:metric:domain:statistic:form:group_create')
        )
        assert response.status_code == 200

    def test_group_update_view_url_path(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:form:group_update',
                kwargs={'pk': self.group.pk},
            )
        )
        assert response.status_code == 200

    def test_group_delete_view_url_path(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:form:group_delete',
                kwargs={'pk': self.group.pk},
            )
        )
        assert response.status_code == 200


class StatisticUrlTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_list_view_url_path(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:statistic:page:list'))
        assert response.status_code == 200

    def test_detail_view_url_path(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:page:detail', kwargs={'pk': self.statistic.pk}
            )
        )
        assert response.status_code == 200

    def test_create_view_url_path(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:statistic:form:create'))
        assert response.status_code == 200

    def test_update_view_url_path(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:form:update', kwargs={'pk': self.statistic.pk}
            )
        )
        assert response.status_code == 200

    def test_delete_view_url_path(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:form:delete', kwargs={'pk': self.statistic.pk}
            )
        )
        assert response.status_code == 200
