from django.db import models

class ChangeLogTypeChoices(models.TextChoices):
    BUG_FIX = ('bug', 'Bug Fix')
    CHANGE = ('chan', 'Change')
    FEATURE = ('feat', 'Feature')
