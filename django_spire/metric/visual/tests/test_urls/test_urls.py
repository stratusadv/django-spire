from __future__ import annotations

from django.urls import reverse

from django_spire.metric.visual.apps import VisualConfig


class VisualAppTestCase:
    def test_app_config(self):
        assert VisualConfig.label == 'django_spire_metric_visual'
        assert VisualConfig.name == 'django_spire.metric.visual'
        assert VisualConfig.REQUIRED_APPS == ('django_spire_core', 'django_spire_metric_domain')

    def test_list_page_url(self):
        assert (
            reverse('django_spire:metric:visual:page:list')
            == '/django_spire/metric/visual/page/list/'
        )

    def test_detail_page_url(self):
        assert (
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': 1})
            == '/django_spire/metric/visual/page/1/detail/'
        )

    def test_create_form_url(self):
        assert (
            reverse('django_spire:metric:visual:form:create')
            == '/django_spire/metric/visual/form/create/'
        )
