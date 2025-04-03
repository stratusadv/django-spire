from django.db import models


class DummyModel(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True, default='')
    favorite_number = models.IntegerField(default=0)

    class Meta:
        app_label = 'dummy'

    def __str__() -> str:
        return 'dummy'
