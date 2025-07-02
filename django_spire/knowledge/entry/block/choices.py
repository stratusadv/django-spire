from django.db.models import TextChoices


class EntryBlockTypeChoices(TextChoices):
    TEXT = 'text'
    HEADING = 'heading'
