from django.db.models import QuerySet
from django.utils.timezone import localtime


class MfaCodeQuerySet(QuerySet):
    def valid_code(self, user):
        return self.filter(user=user, expiration_datetime__gte=localtime()).first()