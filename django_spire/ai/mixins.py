from django.db import models


class AiUsageMixin(models.Model):
    event_count = models.IntegerField(default=0)
    token_usage = models.IntegerField(default=0)
    run_time_seconds = models.FloatField(default=0.0)

    class Meta:
        abstract = True