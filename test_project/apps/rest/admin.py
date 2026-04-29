from django.contrib import admin
from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.apps.rest.models import Pirate


@admin.register(Pirate)
class PirateAdmin(SpireModelAdmin):
    model_class = Pirate
    list_display = ['username', 'first_name', 'last_name', 'email']
    search_fields = ['username', 'first_name', 'last_name', 'email']
