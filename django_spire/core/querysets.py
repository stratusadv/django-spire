from django.db.models import QuerySet, Q


class SearchQuerySetMixin:
    def search(self, search_value: str) -> QuerySet:
        words = search_value.split(' ')

        filtered_query = self

        char_fields = [
            field.name for field in self.model._meta.fields
            if field.get_internal_type() == 'CharField'
        ]

        for word in words:
            or_conditions = Q()
            for field in char_fields:
                or_conditions |= Q(**{f"{field}__icontains": word})
            filtered_query = filtered_query.filter(or_conditions)