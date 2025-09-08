from django.db.models import TextChoices


class EntryVersionStatusChoices(TextChoices):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
