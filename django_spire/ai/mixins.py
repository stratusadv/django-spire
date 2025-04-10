from django.db import models


class AiUsageMixin(models.Model):
    token_usage = models.IntegerField(default=0)
    run_time_seconds = models.IntegerField(default=0)

    class Meta:
        abstract = True