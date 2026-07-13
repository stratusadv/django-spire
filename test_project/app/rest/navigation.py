from django_spire.contrib.navigation.navigation import Navigation


class RestNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-person-badge'
        self.breadcrumbs.add('Pirates', 'rest:page:list')
