from django_spire.core.controllers import BaseUrlController, BaseViewController


class HelpDeskUrlController(BaseUrlController):
    def __init__(self, view_controller: BaseViewController):
        self.view_controller = view_controller

    @property
    def url_pattern(self):
        return '/url'