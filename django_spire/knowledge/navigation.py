from django_spire.contrib.navigation.navigation import Navigation


class KnowledgeNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.page_title = "Knowledge"
        self.icon_class = 'bi bi-folder'
        self.breadcrumbs.add('Collections')
