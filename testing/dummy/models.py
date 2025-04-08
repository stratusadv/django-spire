from django.db import models


class DummyModel(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        app_label = 'dummy'

    def __str__() -> str:
        return 'dummy'
