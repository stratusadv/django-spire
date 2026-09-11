from django_spire.contrib.navigation.navigation import Navigation


class VisualNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-gauge'
        self.breadcrumbs.add(name='Visuals', view_name='django_spire:metric:visual:page:list')
        self.page_title = 'Visuals'
