from django.db import models


class Collection(models.Model):
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        related_query_name='child',
        null=True,
        blank=True
    )

    name = models.CharField(max_length=255)
    description = models.TextField()