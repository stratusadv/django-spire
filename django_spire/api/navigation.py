from django_spire.contrib.navigation.navigation import Navigation


class ApiNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-key'
        self.breadcrumbs.add(name='API Access', view_name='django_spire:api:page:list')
        self.page_title = 'API Access'