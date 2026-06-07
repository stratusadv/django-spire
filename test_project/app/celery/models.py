from django.db import models


class CeleryStalk(models.Model):
    is_crisp = models.BooleanField(default=True)
    length_inches = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        string = f'{self.length_inches} inches'

        if self.is_crisp:
            string += ' and crispy'

        return string
