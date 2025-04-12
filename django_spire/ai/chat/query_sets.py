from django.db.models import QuerySet, Q


class ChatQuerySet(QuerySet):
    def by_user(self, user):
        return self.filter(
            user=user,
        )

    def search(self, query: str):
        return self.filter(
            Q(name__icontains=query)
        )