from django_spire.contrib.navigation.navigation import Navigation


class FileNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-chat'
        self.breadcrumbs.add(name='Files', view_name='file:page:list')
        self.page_title = 'Files'
