from __future__ import annotations

from django.contrib import admin

from django_spire.metric.visual.models import Visual, VisualCondition, VisualReference, VisualRegion


class VisualConditionInline(admin.TabularInline):
    model = VisualCondition
    extra = 0
    ordering = ('order',)


class VisualReferenceInline(admin.TabularInline):
    model = VisualReference
    extra = 0
    ordering = ('order',)


class VisualRegionInline(admin.TabularInline):
    model = VisualRegion
    extra = 0
    ordering = ('key',)


@admin.register(Visual)
class VisualAdmin(admin.ModelAdmin):
    inlines = (VisualReferenceInline, VisualConditionInline, VisualRegionInline)
    list_display = ('pk', 'name', 'statistic', 'date', 'created_datetime')
    list_filter = ('is_active', 'is_deleted')
    list_select_related = ('statistic',)
    ordering = ('-created_datetime',)
    readonly_fields = ('created_datetime', 'is_active', 'is_deleted')
    search_fields = ('name', 'description')


@admin.register(VisualRegion)
class VisualRegionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'key', 'visual', 'is_live_updated', 'title', 'created_datetime')
    list_filter = ('is_live_updated', 'is_active', 'is_deleted')
    list_select_related = ('visual',)
    ordering = ('key',)
    readonly_fields = ('created_datetime', 'is_active', 'is_deleted')
    search_fields = ('key', 'title', 'visual__name')


@admin.register(VisualCondition)
class VisualConditionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'visual', 'state', 'operator', 'target', 'tolerance', 'order')
    list_filter = ('state', 'operator')
    list_select_related = ('visual',)
    ordering = ('visual', 'order')
    search_fields = ('visual__name',)


@admin.register(VisualReference)
class VisualReferenceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'visual', 'reference', 'label', 'order')
    list_select_related = ('visual',)
    ordering = ('visual', 'order')
    search_fields = ('visual__name', 'reference', 'label')
