from django_spire.contrib.navigation.navigation import Navigation


class AppNotificationNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-bell'
        self.breadcrumbs.add(name='Notification', view_name='test_project_notification:page:list')
        self.page_title = 'Notification'
