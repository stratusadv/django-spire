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

    def test_condition_create_form_url(self):
        assert (
            reverse('django_spire:metric:visual:form:create_condition', kwargs={'visual_pk': 1})
            == '/django_spire/metric/visual/form/condition/1/create/'
        )

    def test_reference_create_form_url(self):
        assert (
            reverse('django_spire:metric:visual:form:create_reference', kwargs={'visual_pk': 1})
            == '/django_spire/metric/visual/form/reference/1/create/'
        )

    def test_connect_region_url(self):
        assert (
            reverse('django_spire:metric:visual:form:connect_region', kwargs={'visual_pk': 1})
            == '/django_spire/metric/visual/form/region/1/connect/'
        )

    def test_connect_region_save_url(self):
        assert (
            reverse('django_spire:metric:visual:form:connect_region_save', kwargs={'visual_pk': 1})
            == '/django_spire/metric/visual/form/region/1/connect/save/'
        )
