from __future__ import annotations

from django.apps import AppConfig

from django_spire.tools import check_required_apps


class VisualConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_metric_visual'
    name = 'django_spire.metric.visual'
    verbose_name = 'DJANGO_SPIRE_METRIC_VISUAL'

    MODEL_PERMISSIONS = (
        {
            'name': 'metric_visual',
            'model_class_path': 'django_spire.metric.visual.models.Visual',
            'is_proxy_model': False,
        },
        {
            'name': 'metric_visual_condition',
            'verbose_name': 'Metric Visual Condition',
            'model_class_path': 'django_spire.metric.visual.models.VisualCondition',
            'is_proxy_model': False,
        },
        {
            'name': 'indicator_visual',
            'verbose_name': 'Indicator Visual',
            'model_class_path': 'django_spire.metric.visual.models.IndicatorVisual',
            'is_proxy_model': True,
        },
        {
            'name': 'line_chart_visual',
            'verbose_name': 'Line Chart Visual',
            'model_class_path': 'django_spire.metric.visual.models.LineChartVisual',
            'is_proxy_model': True,
        },
        {
            'name': 'bar_chart_visual',
            'verbose_name': 'Bar Chart Visual',
            'model_class_path': 'django_spire.metric.visual.models.BarChartVisual',
            'is_proxy_model': True,
        },
        {
            'name': 'area_chart_visual',
            'verbose_name': 'Area Chart Visual',
            'model_class_path': 'django_spire.metric.visual.models.AreaChartVisual',
            'is_proxy_model': True,
        },
        {
            'name': 'pie_chart_visual',
            'verbose_name': 'Pie Chart Visual',
            'model_class_path': 'django_spire.metric.visual.models.PieChartVisual',
            'is_proxy_model': True,
        },
        {
            'name': 'gauge_chart_visual',
            'verbose_name': 'Gauge Chart Visual',
            'model_class_path': 'django_spire.metric.visual.models.GaugeChartVisual',
            'is_proxy_model': True,
        },
    )

    REQUIRED_APPS = ('django_spire_core', 'django_spire_metric_domain')

    def ready(self) -> None:
        check_required_apps(self.label)
