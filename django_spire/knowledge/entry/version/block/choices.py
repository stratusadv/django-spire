from django.db.models import TextChoices


class BlockTypeChoices(TextChoices):
    TEXT = 'text'
    HEADING = 'heading'
    SUB_HEADING = 'sub_heading'
    LIST_ITEM = 'list_item',
    LIST = 'list',
    CODE = 'code'
