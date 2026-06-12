from django_spire.contrib.navigation.navigation import Navigation


class TaskNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-list-task'
        self.breadcrumbs.add('Tasks', url='task:page:list')
