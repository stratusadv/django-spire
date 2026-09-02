from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.tests.factories import (
    create_test_presentation,
    create_test_section,
    create_test_slide,
)


class PresentationFormViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()

    def test_create_view(self):
        response = self.client.get(reverse('django_spire:metric:visual:presentation:form:create'))

        assert response.status_code == 200

    def test_update_view(self):
        response = self.client.get(
            reverse(
                'django_spire:metric:visual:presentation:form:update',
                kwargs={'pk': self.presentation.pk},
            )
        )

        assert response.status_code == 200

    def test_delete_view(self):
        response = self.client.post(
            reverse(
                'django_spire:metric:visual:presentation:form:delete',
                kwargs={'pk': self.presentation.pk},
            ),
            data={'should_delete': 'on'},
        )

        assert response.status_code == 302
        self.presentation.refresh_from_db()
        assert self.presentation.is_deleted is True

    def test_create_slide_view(self):
        response = self.client.get(
            reverse(
                'django_spire:metric:visual:presentation:form:create_slide',
                kwargs={'presentation_pk': self.presentation.pk},
            )
        )

        assert response.status_code == 200

    def test_update_slide_view(self):
        slide = create_test_slide(self.presentation)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:presentation:form:update_slide', kwargs={'pk': slide.pk}
            )
        )

        assert response.status_code == 200

    def test_delete_slide_view(self):
        slide = create_test_slide(self.presentation)

        response = self.client.post(
            reverse(
                'django_spire:metric:visual:presentation:form:delete_slide', kwargs={'pk': slide.pk}
            ),
            data={'should_delete': 'on'},
        )

        assert response.status_code == 302
        slide.refresh_from_db()
        assert slide.is_deleted is True

    def test_create_section_view(self):
        slide = create_test_slide(self.presentation)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:presentation:form:create_section',
                kwargs={'slide_pk': slide.pk},
            )
        )

        assert response.status_code == 200

    def test_update_section_view(self):
        slide = create_test_slide(self.presentation)
        section = create_test_section(slide)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:presentation:form:update_section',
                kwargs={'pk': section.pk},
            )
        )

        assert response.status_code == 200

    def test_delete_section_view(self):
        slide = create_test_slide(self.presentation)
        section = create_test_section(slide)

        response = self.client.post(
            reverse(
                'django_spire:metric:visual:presentation:form:delete_section',
                kwargs={'pk': section.pk},
            ),
            data={'should_delete': 'on'},
        )

        assert response.status_code == 302
        section.refresh_from_db()
        assert section.is_deleted is True
