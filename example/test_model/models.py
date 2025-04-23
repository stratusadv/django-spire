from __future__ import annotations

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.timezone import localdate, now

from django_spire.history.mixins import HistoryModelMixin


class TestModel(HistoryModelMixin):
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    description = models.TextField()
    personality_type = models.CharField(
        max_length=3,
        choices=[('int', 'Introvert'), ('ext', 'Extrovert')],
        default='int',
    )
    email = models.EmailField(blank=True, null=True)
    favorite_number = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(999)])
    anniversary_datetime = models.DateTimeField(default=now)
    birth_date = models.DateField(default=localdate)
    weight_lbs = models.DecimalField(max_digits=7, decimal_places=3)

    best_friend = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    bed_time = models.TimeField(default='20:00')
    likes_to_party = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def is_lighter_than(self, check_weight: float) -> bool:
        return self.weight_lbs < check_weight

    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    class Meta:
        db_table = 'django_spire_test_model'
        verbose_name = 'Test Model'
        verbose_name_plural = 'Test Model'
