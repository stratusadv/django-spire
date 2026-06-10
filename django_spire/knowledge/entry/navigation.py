from django_spire.contrib.navigation.navigation import Navigation


class EntryNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-file-text'
        self.breadcrumbs.add(
            name='Knowledge',
            url='django_spire:knowledge:page:home',
        )
