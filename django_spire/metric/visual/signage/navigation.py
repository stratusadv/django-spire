from django_spire.contrib.navigation.navigation import Navigation


class SignageNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-easel'
        self.breadcrumbs.add(name='Signages', view_name='django_spire:metric:visual:signage:page:list')
        self.page_title = 'Signages'