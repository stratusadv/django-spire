from django.db import models


class PersonSeedingModel(models.Model):
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=16)
    age = models.IntegerField()
    birth_date = models.DateField()

    class Meta:
        db_table = 'spire_person_seeding'
        verbose_name = 'Person Seeding'
        verbose_name_plural = 'Person Seeding'
        managed = False
