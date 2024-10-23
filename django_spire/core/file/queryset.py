from django.db.models import QuerySet, Q


class FileQuerySet(QuerySet):
    def active(self):
        return self.filter(is_deleted=False, is_active=True)

    def related_field(self, field_name: str):
        return self.filter(related_field=field_name)
