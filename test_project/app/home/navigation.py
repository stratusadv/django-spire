from django_spire.contrib.navigation.navigation import Navigation


class HomeNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-house-door'
