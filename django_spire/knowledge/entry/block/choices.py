from django.db.models import TextChoices


class BlockTypeChoices(TextChoices):
    TEXT = 'text'
    HEADING = 'heading'
    SUB_HEADING = 'sub_heading'