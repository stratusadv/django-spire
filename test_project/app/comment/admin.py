from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.app.comment.models import CommentExample


@admin.register(CommentExample)
class CommentExampleAdmin(SpireModelAdmin):
    model_class = CommentExample
