from __future__ import annotations

from test_project.apps.ordering import models

from django_spire.contrib.seeding import DjangoModelSeeder


class OrderingSeeder(DjangoModelSeeder):
     model_class = models.Ordering
     fields = {

     }

