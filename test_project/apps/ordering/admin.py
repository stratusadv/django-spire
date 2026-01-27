from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.apps.ordering.models import Duck


@admin.register(Duck)
class DuckAdmin(SpireModelAdmin):
    model_class = Duck