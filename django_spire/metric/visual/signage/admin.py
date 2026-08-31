from __future__ import annotations

from django.contrib import admin

from django_spire.metric.visual.signage.models import Signage, SignagePresentation


class SignagePresentationInline(admin.TabularInline):
    model = SignagePresentation
    extra = 0
    ordering = ('order',)


@admin.register(Signage)
class SignageAdmin(admin.ModelAdmin):
    inlines = (SignagePresentationInline,)
    list_display = ('pk', 'name', 'title', 'key', 'slide_display_seconds', 'created_datetime')
    list_filter = ('is_active', 'is_deleted')
    ordering = ('-created_datetime',)
    readonly_fields = ('created_datetime', 'is_active', 'is_deleted', 'key')
    search_fields = ('name', 'title', 'description')


@admin.register(SignagePresentation)
class SignagePresentationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'signage', 'presentation', 'order')
    list_filter = ('is_active', 'is_deleted')
    ordering = ('signage', 'order')
    search_fields = ('signage__name', 'presentation__name')
