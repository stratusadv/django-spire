from django_spire.contrib.navigation.navigation import Navigation


class AuthUserNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.breadcrumbs.add('Users', 'django_spire:auth:user:page:list')
        self.icon_class = 'bi bi-person'
