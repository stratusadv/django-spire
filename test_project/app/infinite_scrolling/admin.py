from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.apps.infinite_scrolling.models import InfiniteScrolling


@admin.register(InfiniteScrolling)
class InfiniteScrollingAdmin(SpireModelAdmin):
    model_class = InfiniteScrolling
