from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.apps.model_and_service.models import Adult, Kid


@admin.register(Adult)
class AdultAdmin(SpireModelAdmin):
    model_class = Adult


@admin.register(Kid)
class KidAdmin(SpireModelAdmin):
    model_class = Kid
