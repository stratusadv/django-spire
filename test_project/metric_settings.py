from django_spire.metric.domain.seeding.constants import INTERNAL_TRACKING_STATISTIC_KEY, \
    INTERNAL_TRACKING_SUB_DOMAIN_KEY

DJANGO_SPIRE_METRIC_VISUAL_REGIONS = ['home:dashboard:hero', 'home:dashboard:conversion']

# Metric Internal Tracking Settings
# The statistic + sub-domain the metric click-tracking middleware records against.
# Both keys come from the seeded metric data (django_spire/metric/domain/seeding).
DJANGO_SPIRE_METRIC_STATISTIC_KEY = INTERNAL_TRACKING_STATISTIC_KEY
DJANGO_SPIRE_METRIC_SUB_DOMAIN_KEY = INTERNAL_TRACKING_SUB_DOMAIN_KEY

# Report Registry
DJANGO_SPIRE_REPORT_REGISTRIES = [
    'test_project.app.task.reports.task_report_registry.TaskReportRegistry'
]

# Metric Registry
DJANGO_SPIRE_METRIC_REGISTRY = [
    'test_project.app.metrics.metrics.StoreMetric',
    'test_project.app.task.metrics.TaskMetric',
]

