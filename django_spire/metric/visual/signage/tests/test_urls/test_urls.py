from __future__ import annotations

from django.urls import reverse

from django_spire.metric.visual.signage.apps import SignageConfig


class SignageAppTestCase:
    def test_app_config(self):
        assert SignageConfig.label == 'django_spire_metric_visual_signage'
        assert SignageConfig.name == 'django_spire.metric.visual.signage'
        assert SignageConfig.REQUIRED_APPS == (
            'django_spire_core',
            'django_spire_metric_domain',
            'django_spire_metric_visual',
            'django_spire_metric_visual_presentation',
        )

    def test_list_page_url(self):
        assert (
            reverse('django_spire:metric:visual:signage:page:list')
            == '/django_spire/metric/visual/signage/page/list/'
        )

    def test_detail_page_url(self):
        assert (
            reverse('django_spire:metric:visual:signage:page:detail', kwargs={'pk': 1})
            == '/django_spire/metric/visual/signage/page/1/detail/'
        )

    def test_display_page_url(self):
        assert (
            reverse(
                'django_spire:metric:visual:signage:page:display',
                kwargs={'key': '11111111-1111-1111-1111-111111111111'},
            )
            == '/django_spire/metric/visual/signage/page/display/'
            '11111111-1111-1111-1111-111111111111/'
        )

    def test_create_link_form_url(self):
        assert (
            reverse('django_spire:metric:visual:signage:form:create_link')
            == '/django_spire/metric/visual/signage/form/link/create/'
        )
