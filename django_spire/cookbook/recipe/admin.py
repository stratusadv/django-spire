from django.contrib import admin

from django_spire.cookbook.recipe import models

admin.site.register(models.Recipe)
admin.site.register(models.Ingredient)
