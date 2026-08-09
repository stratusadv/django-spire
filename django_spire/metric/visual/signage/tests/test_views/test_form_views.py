from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.signage.tests.factories import create_test_link, create_test_signage


class SignageFormViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.signage = create_test_signage()

    def test_create_view(self):
        response = self.client.get(reverse('django_spire:metric:visual:signage:form:create'))

        assert response.status_code == 200

    def test_update_view(self):
        response = self.client.get(
            reverse(
                'django_spire:metric:visual:signage:form:update', kwargs={'pk': self.signage.pk}
            )
        )

        assert response.status_code == 200

    def test_delete_view(self):
        response = self.client.post(
            reverse(
                'django_spire:metric:visual:signage:form:delete', kwargs={'pk': self.signage.pk}
            ),
            data={'should_delete': 'on'},
        )

        assert response.status_code == 302
        self.signage.refresh_from_db()
        assert self.signage.is_deleted is True

    def test_create_link_view(self):
        response = self.client.get(
            reverse('django_spire:metric:visual:signage:form:create_link'),
            data={'signage': self.signage.pk},
        )

        assert response.status_code == 200

    def test_update_link_view(self):
        link = create_test_link(self.signage)

        response = self.client.get(
            reverse('django_spire:metric:visual:signage:form:update_link', kwargs={'pk': link.pk})
        )

        assert response.status_code == 200

    def test_delete_link_view(self):
        link = create_test_link(self.signage)

        response = self.client.post(
            reverse('django_spire:metric:visual:signage:form:delete_link', kwargs={'pk': link.pk}),
            data={'should_delete': 'on'},
        )

        assert response.status_code == 302
        link.refresh_from_db()
        assert link.is_deleted is True
