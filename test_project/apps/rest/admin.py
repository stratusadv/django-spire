from django.contrib import admin
from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.apps.rest.models import TestRestUser


@admin.register(TestRestUser)
class TestRestUserAdmin(SpireModelAdmin):
    model_class = TestRestUser
    list_display = ['username', 'first_name', 'last_name', 'email']
    search_fields = ['username', 'first_name', 'last_name', 'email']
