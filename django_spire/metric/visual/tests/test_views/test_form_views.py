from __future__ import annotations

from decimal import Decimal

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
    create_test_visual,
)


class VisualFormViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic)
        self.domain = domain

    def test_create_view(self):
        response = self.client.get(reverse('django_spire:metric:visual:form:create'))
        assert response.status_code == 200

    def test_update_view(self):
        response = self.client.get(
            reverse('django_spire:metric:visual:form:update', kwargs={'pk': self.visual.pk})
        )
        assert response.status_code == 200

    def test_delete_view(self):
        response = self.client.post(
            reverse('django_spire:metric:visual:form:delete', kwargs={'pk': self.visual.pk}),
            data={'should_delete': 'on'},
        )

        assert response.status_code == 302
        self.visual.refresh_from_db()
        assert self.visual.is_deleted is True
        assert self.visual.activities.filter(verb='deleted').count() == 1

    def test_create_condition_view(self):
        response = self.client.get(
            reverse('django_spire:metric:visual:form:create_condition'),
            data={'visual': self.visual.pk},
        )
        assert response.status_code == 200

    def test_update_condition_view(self):
        condition = self.visual.conditions.first()

        response = self.client.get(
            reverse('django_spire:metric:visual:form:update_condition', kwargs={'pk': condition.pk})
        )
        assert response.status_code == 200

    def test_delete_condition_view(self):
        condition = self.visual.conditions.first()

        response = self.client.post(
            reverse(
                'django_spire:metric:visual:form:delete_condition', kwargs={'pk': condition.pk}
            ),
            data={'should_delete': 'on'},
        )

        assert response.status_code == 302
        condition.refresh_from_db()
        assert condition.is_deleted is True

    def test_set_default_conditions_view(self):
        self.visual.conditions.all().delete()

        response = self.client.post(
            reverse(
                'django_spire:metric:visual:form:set_default_conditions',
                kwargs={'pk': self.visual.pk},
            )
        )

        assert response.status_code == 302
        assert self.visual.conditions.count() == 3

    def test_create_reference_view_suggests_statistic_references(self):
        sub_domain = create_test_subdomain(domain=self.domain)
        self.visual.statistic.services.processor.add_value(
            reference='/home/', value=Decimal(5), sub_domain=sub_domain
        )
        self.visual.statistic.services.processor.add_value(
            reference='/dashboard/', value=Decimal(7), sub_domain=sub_domain
        )

        response = self.client.get(
            reverse('django_spire:metric:visual:form:create_reference'),
            data={'visual': self.visual.pk},
        )

        assert response.status_code == 200
        html = response.content.decode()
        assert 'id="reference-datalist"' in html
        assert '<option value="/home/">' in html
        assert '<option value="/dashboard/">' in html
