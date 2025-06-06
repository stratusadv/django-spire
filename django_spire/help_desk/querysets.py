from django.http.response import Http404
from django.shortcuts import get_object_or_404

from django_spire.history.querysets import HistoryQuerySet


class HelpDeskTicketQuerySet(HistoryQuerySet):
    def sort_by_date(self, descending=False):
        return self.order_by('-created_datetime' if descending else 'created_datetime')

    def filter_by_user(self, user):
        return self.filter(created_by=user)

    def get_ticket_detail_for_user(
            self,
            ticket_pk,
            user,
            permission_handler
    ):
        ticket = get_object_or_404(self.model, pk=ticket_pk)

        if permission_handler.should_deny_ticket_detail_access(user, ticket):
            raise Http404('The ticket could not be retrieved.')

        return ticket