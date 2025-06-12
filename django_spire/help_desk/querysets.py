from django_spire.history.querysets import HistoryQuerySet


class HelpDeskTicketQuerySet(HistoryQuerySet):
    def sort_by_date(self, descending=False):
        return self.order_by('-created_datetime' if descending else 'created_datetime')

    def filter_by_user(self, user):
        return self.filter(created_by=user)