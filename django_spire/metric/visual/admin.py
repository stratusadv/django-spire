from __future__ import annotations

from django.contrib import admin

from django_spire.metric.visual.models import Visual, VisualCondition


class VisualConditionInline(admin.TabularInline):
    model = VisualCondition
    extra = 0
    ordering = ('order',)


@admin.register(Visual)
class VisualAdmin(admin.ModelAdmin):
    inlines = (VisualConditionInline,)
    list_display = ('pk', 'name', 'statistic', 'reference', 'date', 'created_datetime')
    list_filter = ('is_active', 'is_deleted')
    ordering = ('-created_datetime',)
    readonly_fields = ('created_datetime', 'is_active', 'is_deleted')
    search_fields = ('name', 'description')


@admin.register(VisualCondition)
class VisualConditionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'visual', 'state', 'operator', 'target', 'tolerance', 'order')
    list_filter = ('state', 'operator')
    ordering = ('visual', 'order')
    search_fields = ('visual__name',)
