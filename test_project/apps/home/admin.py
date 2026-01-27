from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.apps.home.models import HomeExample


@admin.register(HomeExample)
class HomeExampleAdmin(SpireModelAdmin):
    model_class = HomeExample
