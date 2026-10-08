from __future__ import annotations

from decimal import Decimal

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.history.activity.context import activity_user
from django_spire.metric.visual.presentation.models import Slide, SlideSection
from django_spire.metric.visual.presentation.tests.factories import (
    create_test_presentation,
    create_test_section,
    create_test_slide,
)
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
    create_test_visual,
)


class PresentationPageViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.presentation = create_test_presentation()

    def test_list_view(self):
        response = self.client.get(reverse('django_spire:metric:visual:presentation:page:list'))

        assert response.status_code == 200
        assert 'Glue.querySet.presentations' in response.content.decode()

    def test_detail_view(self):
        slide = create_test_slide(self.presentation)
        section = create_test_section(slide, row=1, col=1)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:presentation:page:detail',
                kwargs={'pk': self.presentation.pk},
            )
        )

        assert response.status_code == 200
        assert response.context_data['presentation'] == self.presentation
        assert len(response.context_data['slides']) == 1
        assert len(response.context_data['slides'][0]['sections']) == 1

        section_data = response.context_data['slides'][0]['sections'][0]
        assert 'chart' in section_data
        assert 'grid_style' in section_data
        assert response.context_data['slides'][0]['row_count'] == 1

        content = response.content.decode()
        assert 'Row 1, Col 1' in content

        edit_url = reverse(
            'django_spire:metric:visual:presentation:form:update_section', kwargs={'pk': section.pk}
        )
        delete_url = reverse(
            'django_spire:metric:visual:presentation:form:delete_section', kwargs={'pk': section.pk}
        )
        assert edit_url in content
        assert delete_url in content
        assert 'grid-auto-rows: 48rem' in content

    def test_detail_view_empty_section_shows_placeholder(self):
        slide = create_test_slide(self.presentation)
        create_test_section(slide, row=0, col=0, with_visual=False)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:presentation:page:detail',
                kwargs={'pk': self.presentation.pk},
            )
        )

        content = response.content.decode()
        assert 'Row 0, Col 0' in content
        assert 'Empty' in content

    def test_detail_view_row_count_with_two_rows(self):
        slide = create_test_slide(self.presentation)
        create_test_section(slide, row=0, col=0, with_visual=False)
        create_test_section(slide, row=1, col=0, with_visual=False)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:presentation:page:detail',
                kwargs={'pk': self.presentation.pk},
            )
        )

        assert response.status_code == 200
        assert response.context_data['slides'][0]['row_count'] == 2
        assert 'grid-auto-rows: 24rem' in response.content.decode()

    def test_detail_view_no_matching_data_shows_caption(self):
        slide = create_test_slide(self.presentation)

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        sub_domain = create_test_subdomain(domain=domain)
        statistic = create_test_statistic(group=group)
        visual = create_test_visual(statistic=statistic, reference='/live/')
        SlideSection.objects.create(slide=slide, visual=visual, row=1, col=1)

        statistic.services.processor.add_value(
            reference='/home/', value=Decimal(10), sub_domain=sub_domain
        )

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:presentation:page:detail',
                kwargs={'pk': self.presentation.pk},
            )
        )

        assert response.status_code == 200
        assert response.context_data['slides'][0]['sections'][0]['no_matching_data'] is True

        assert 'No matching data' in response.content.decode()

    def test_slide_and_section_deletes_show_in_presentation_activity_log(self):
        with activity_user(self.super_user):
            slide_a = create_test_slide(self.presentation, name='alpha', order=0)
            slide_b = create_test_slide(self.presentation, name='beta', order=1)
            section_b = create_test_section(slide_b, row=0, col=0)

        detail_url = reverse(
            'django_spire:metric:visual:presentation:page:detail',
            kwargs={'pk': self.presentation.pk},
        )
        activities = [
            a.information for a in self.client.get(detail_url).context_data['activity_log']
        ]
        assert any('created Slide' in info for info in activities)
        assert any('created Slide Section' in info for info in activities)

        self.client.post(
            reverse(
                'django_spire:metric:visual:presentation:form:delete_slide',
                kwargs={'pk': slide_a.pk},
            ),
            data={'should_delete': 'on'},
        )
        self.client.post(
            reverse(
                'django_spire:metric:visual:presentation:form:delete_section',
                kwargs={'pk': section_b.pk},
            ),
            data={'should_delete': 'on'},
        )

        assert not Slide.objects.filter(pk=slide_a.pk).exists()
        assert not SlideSection.objects.filter(pk=section_b.pk).exists()

        activities = [
            a.information for a in self.client.get(detail_url).context_data['activity_log']
        ]
        assert any('deleted Slide "alpha"' in info for info in activities)
        assert any('deleted Slide Section' in info for info in activities)
