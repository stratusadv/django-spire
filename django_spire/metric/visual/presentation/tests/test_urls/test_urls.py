from __future__ import annotations

from django.urls import reverse

from django_spire.metric.visual.presentation.apps import PresentationConfig


class PresentationAppTestCase:
    def test_app_config(self):
        assert PresentationConfig.label == 'django_spire_metric_visual_presentation'
        assert PresentationConfig.name == 'django_spire.metric.visual.presentation'
        assert PresentationConfig.REQUIRED_APPS == (
            'django_spire_core',
            'django_spire_metric_domain',
            'django_spire_metric_visual',
        )

    def test_list_page_url(self):
        assert (
            reverse('django_spire:metric:visual:presentation:page:list')
            == '/django_spire/metric/visual/presentation/page/list/'
        )

    def test_detail_page_url(self):
        assert (
            reverse('django_spire:metric:visual:presentation:page:detail', kwargs={'pk': 1})
            == '/django_spire/metric/visual/presentation/page/1/detail/'
        )

    def test_create_form_url(self):
        assert (
            reverse('django_spire:metric:visual:presentation:form:create')
            == '/django_spire/metric/visual/presentation/form/create/'
        )

    def test_slide_create_form_url(self):
        assert (
            reverse('django_spire:metric:visual:presentation:form:create_slide')
            == '/django_spire/metric/visual/presentation/form/slide/create/'
        )

    def test_section_create_form_url(self):
        assert (
            reverse('django_spire:metric:visual:presentation:form:create_section')
            == '/django_spire/metric/visual/presentation/form/section/create/'
        )
