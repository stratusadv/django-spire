from django.db import models


class AiComputeUsageMixin(models.Model):
    token_usage = models.IntegerField(default=0)
    compute_seconds = models.IntegerField(default=0)

    class Meta:
        abstract = True