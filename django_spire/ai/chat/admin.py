from django.contrib import admin

from django_spire.ai.chat import models

admin.site.register(models.Chat)
admin.site.register(models.ChatMessage)