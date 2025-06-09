from django_spire.core.controllers.options import BaseAppModifier


class HelpDeskModifier(BaseAppModifier):
    target_app_names = ['help_desk']
    view_decorators = {'help_desk': ['help_desk.decorators.help_desk']}