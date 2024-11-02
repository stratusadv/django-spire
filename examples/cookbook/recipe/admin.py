from django.contrib import admin

from examples.cookbook.recipe import models


admin.site.register(models.Recipe)
admin.site.register(models.Ingredient)
