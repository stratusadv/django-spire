from django_spire.contrib.navigation.navigation import Navigation


class StatisticNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-bar-chart'
        self.breadcrumbs.add(
            name='Statistics', view_name='django_spire:metric:domain:statistic:page:group_list'
        )
        self.page_title = 'Statistics'


class StatisticGroupNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-collection'
        self.breadcrumbs.add(
            name='Statistics', view_name='django_spire:metric:domain:statistic:page:group_list'
        )
        self.page_title = 'Statistic Groups'
