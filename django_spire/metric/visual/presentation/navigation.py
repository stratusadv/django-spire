from django_spire.contrib.navigation.navigation import Navigation


class PresentationNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-presentation'
        self.breadcrumbs.add(name='Presentations', view_name='django_spire:metric:visual:presentation:page:list')
        self.page_title = 'Presentations'
