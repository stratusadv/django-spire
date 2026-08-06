from django_spire.contrib.navigation.navigation import Navigation
from django_spire.core.context_processors import django_spire


class AuthGroupNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.breadcrumbs.add('Groups', 'django_spire:auth:group:page:list')
        self.icon_class = 'bi bi-people'
