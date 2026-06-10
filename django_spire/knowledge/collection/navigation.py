from django_spire.contrib.navigation.navigation import Navigation


class CollectionNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-folder'
        self.breadcrumbs.add(
            name='Knowledge',
            url='django_spire:knowledge:page:home',
        )
