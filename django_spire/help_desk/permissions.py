import dataclasses

from django.contrib.auth.models import AbstractUser, AnonymousUser

from django_spire.help_desk.models import HelpDeskTicket


@dataclasses.dataclass
class HelpDeskAuthorization:
    is_helpdesk_admin: bool
    can_delete_tickets: bool
    can_change_tickets: bool
    should_deny_ticket_detail_access: bool

class BaseHelpDeskAuthorizationController:
    def __init__(self, user: AbstractUser | AnonymousUser = None, ticket: HelpDeskTicket = None):
        self.user = user
        self.ticket = ticket

    def check_authorization(
        self,
        user: AbstractUser,
        ticket: HelpDeskTicket = None
    ) -> HelpDeskAuthorization:
        self.user = user
        self.ticket = ticket

        return HelpDeskAuthorization(
            is_helpdesk_admin=self.is_helpdesk_admin,
            can_delete_tickets=self.can_delete_tickets,
            can_change_tickets=self.can_change_tickets,
            should_deny_ticket_detail_access=self.should_deny_ticket_detail_access,
        )

    @property
    def is_helpdesk_admin(self) -> bool:
        return True

    @property
    def can_delete_tickets(self) -> bool:
        return True

    @property
    def can_change_tickets(self) -> bool:
        return True

    @property
    def should_deny_ticket_detail_access(self) -> bool:
        return True