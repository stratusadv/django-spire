from __future__ import annotations

from test_project.apps.theme import models

from django_spire.contrib.seeding import DjangoModelSeeder


class ThemeModelSeeder(DjangoModelSeeder):
     model_class = models.Theme
     fields = {

     }

