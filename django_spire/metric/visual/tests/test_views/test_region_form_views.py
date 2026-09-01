from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.models import VisualRegion
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_visual,
)


class VisualRegionFormViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic)

    def test_connect_region_view_lists_registry(self):
        response = self.client.get(
            reverse('django_spire:metric:visual:form:connect_region'),
            data={'visual': self.visual.pk},
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert 'home:dashboard:hero' in content
        assert 'home:dashboard:conversion' in content

    def test_connect_region_view_requires_visual(self):
        response = self.client.get(reverse('django_spire:metric:visual:form:connect_region'))
        assert response.status_code == 404

    def test_connect_view_creates_region(self):
        response = self.client.post(
            reverse('django_spire:metric:visual:form:connect_region_save'),
            data={'visual': self.visual.pk, 'key': 'home:dashboard:hero'},
        )

        assert response.status_code == 302
        region = VisualRegion.objects.get(key='home:dashboard:hero')
        assert region.visual == self.visual

    def test_connect_view_reassigns_taken_region(self):
        other_domain = create_test_domain(name='other')
        other_group = create_test_statistic_group(domain=other_domain)
        other_statistic = create_test_statistic(group=other_group)
        other_visual = create_test_visual(statistic=other_statistic, name='other_visual')

        VisualRegion.objects.create(key='home:dashboard:hero', visual=other_visual)

        response = self.client.post(
            reverse('django_spire:metric:visual:form:connect_region_save'),
            data={'visual': self.visual.pk, 'key': 'home:dashboard:hero'},
        )

        assert response.status_code == 302
        region = VisualRegion.objects.get(key='home:dashboard:hero')
        assert region.visual == self.visual
        assert VisualRegion.objects.filter(key='home:dashboard:hero').count() == 1

    def test_connect_view_rejects_unknown_key(self):
        response = self.client.post(
            reverse('django_spire:metric:visual:form:connect_region_save'),
            data={'visual': self.visual.pk, 'key': 'unknown:region'},
        )

        assert response.status_code == 302
        assert VisualRegion.objects.filter(key='unknown:region').count() == 0

    def test_update_view(self):
        region = VisualRegion.objects.create(key='home:dashboard:hero', visual=self.visual)

        response = self.client.get(
            reverse('django_spire:metric:visual:form:update_region', kwargs={'pk': region.pk})
        )

        assert response.status_code == 200
        assert response.context_data['region'] == region

    def test_disconnect_view(self):
        region = VisualRegion.objects.create(key='home:dashboard:hero', visual=self.visual)

        response = self.client.post(
            reverse('django_spire:metric:visual:form:disconnect_region', kwargs={'pk': region.pk})
        )

        assert response.status_code == 302
        region.refresh_from_db()
        assert region.visual_id is None
        assert VisualRegion.objects.filter(key='home:dashboard:hero').count() == 1

    def test_disconnect_view_requires_post(self):
        region = VisualRegion.objects.create(key='home:dashboard:hero', visual=self.visual)

        response = self.client.get(
            reverse('django_spire:metric:visual:form:disconnect_region', kwargs={'pk': region.pk})
        )

        assert response.status_code == 405
