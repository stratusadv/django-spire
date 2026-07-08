from django_spire.contrib.navigation.navigation import Navigation


class DomainNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-globe'
        self.breadcrumbs.add(name='Domains', view_name='django_spire:metric:domain:page:list')
        self.page_title = 'Domains'
