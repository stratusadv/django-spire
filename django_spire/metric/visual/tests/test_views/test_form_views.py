from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_visual,
)


class VisualFormViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic)

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
        assert self.visual.conditions.filter(pk=condition.pk).count() == 0

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
