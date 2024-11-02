from django.db import models


class NutritionFactType(models.TextChoices):
    PROTEIN = ('prot', 'Protein')
    CARB = ('carb', 'Carbohydrate')
    FAT = ('fat', 'Fat')
