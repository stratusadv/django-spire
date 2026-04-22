from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.app.history.models import HistoryExample


@admin.register(HistoryExample)
class HistoryExampleAdmin(SpireModelAdmin):
    model_class = HistoryExample
