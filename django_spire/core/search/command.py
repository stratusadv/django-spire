from enum import Enum

class SearchCommand:
    class Action(Enum):
        DISPATCH_MODAL = 'dispatch_modal'
        OPEN_URL_CURRENT_TAB = 'open_url_in_current_tab'
        OPEN_URL_NEW_TAB = 'open_url_in_new_tab'

    def __init__(
            self,
            name: str,
            icon: str,
            url: str,
            action: Action,
            description: str | None = None,
            permission_required: str | None = None,
    ):
        self.name = name
        self.icon = icon
        self.url = url
        self.action = action
        self.description = description
        self.permission_required = permission_required
