from django.contrib import admin

from example.cookbook.recipe import models


admin.site.register(models.Recipe)
admin.site.register(models.Ingredient)
