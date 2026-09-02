from django_spire.contrib.navigation.navigation import Navigation


class ShowcaseNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-palette'
        self.breadcrumbs.add('Widget Showcase', 'showcase:page:form')
