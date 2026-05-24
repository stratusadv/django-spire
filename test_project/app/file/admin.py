from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.app.file.models import FileExample


@admin.register(FileExample)
class FileExampleAdmin(SpireModelAdmin):
    model_class = FileExample
