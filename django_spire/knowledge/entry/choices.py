from django.db.models import TextChoices


class EntryVersionTypeChoices(TextChoices):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'