from django.db import models
from django.contrib.postgres.fields import JSONField

from django_spire.ai.prompt.tuning.choices import OutcomeRatingChoices


class PromptTrainingMixin(models.Model):
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children'
    )

    # Fields for prompt training
    version = models.IntegerField(default=1)
    prompt = models.TextField(default='', blank=True)
    feedback = models.TextField(default='', blank=True)

    rating = models.IntegerField(
        choices=OutcomeRatingChoices.choices,
        null=True,
    )

    run_data = JSONField(null=True, blank=True)

    class Meta:
        abstract = True
