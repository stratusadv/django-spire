from django_spire.contrib.navigation.navigation import Navigation
from test_project.app.task.models import Task


class TaskNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.breadcrumbs.add_breadcrumb_from_model_name(model=Task, url='task:page:list')
