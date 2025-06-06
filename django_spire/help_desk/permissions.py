from django.contrib.auth.models import User


class HelpDeskTicketPermissionHandler:
    @classmethod
    def is_helpdesk_admin(cls,user: User):
        return True

    @classmethod
    def can_delete_tickets(cls, user):
        return True

    @classmethod
    def can_change_tickets(cls, user: User):
        return True

    @classmethod
    def should_deny_ticket_detail_access(cls, user, ticket):
        return False

    @classmethod
    def get_ticket_perms(cls, user):
        return {
            'can_delete': cls.can_delete_tickets(user),
            'can_change': cls.can_change_tickets(user),
        }