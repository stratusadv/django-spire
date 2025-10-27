from django.contrib import admin

from django_spire.ai.context import models


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_datetime', 'is_deleted')


@admin.register(models.People)
class PeopleAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'created_datetime', 'is_deleted')