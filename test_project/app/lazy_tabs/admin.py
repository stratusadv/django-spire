from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.app.lazy_tabs.models import LazyTabs


@admin.register(LazyTabs)
class LazyTabsAdmin(SpireModelAdmin):
    model_class = LazyTabs
