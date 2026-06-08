from django_spire.contrib.navigation.navigation import Navigation


class ChangelogNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-clock-history'
