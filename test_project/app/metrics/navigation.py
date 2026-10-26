from django_spire.contrib.navigation.navigation import Navigation


class MetricsNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-graph-up'
        self.breadcrumbs.add('Metrics', 'metrics:page:record_test')
