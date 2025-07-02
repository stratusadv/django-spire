from django.db.models import TextChoices


class EntryRevisionTypeChoices(TextChoices):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'