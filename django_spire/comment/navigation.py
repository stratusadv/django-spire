from django_spire.contrib.navigation.navigation import Navigation


class CommentNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-chat'
