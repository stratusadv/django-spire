from django.db.models import TextChoices


class BlockTypeChoices(TextChoices):
    TEXT = 'text'
    HEADING = 'heading'
    LIST = 'list',
    CODE = 'code'
