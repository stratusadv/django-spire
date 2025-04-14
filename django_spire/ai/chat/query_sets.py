from django.db.models import QuerySet, Q, Count


class ChatQuerySet(QuerySet):
    def by_user(self, user):
        return self.filter(
            user=user,
        )

    def get_empty_or_create(self, user):
        try:
            return (
                self.filter(user=user)
                .annotate(num_messages=Count('message'))
                .filter(num_messages=0)
                .earliest('-id')
            )
        except self.model.DoesNotExist:
            return self.create(user=user)

    def search(self, query: str):
        return self.filter(
            Q(name__icontains=query)
        )