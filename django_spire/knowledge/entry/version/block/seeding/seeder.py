from __future__ import annotations

from module import models

from django_spire.contrib.seeding import DjangoModelSeeder


class SpireChildAppSeeder(DjangoModelSeeder):
     model_class = models.SpireChildApp
     fields = {

     }

