import json

from django.db.models import TextChoices


class SpireTextChoices(TextChoices):
    @classmethod
    def to_glue_choices(cls) -> str:
        return json.dumps(cls.choices)