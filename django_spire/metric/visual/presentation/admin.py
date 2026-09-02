from __future__ import annotations

from django.contrib import admin

from django_spire.metric.visual.presentation.models import Presentation, Slide, SlideSection


class SlideInline(admin.TabularInline):
    model = Slide
    extra = 0
    ordering = ('order',)


class SlideSectionInline(admin.TabularInline):
    model = SlideSection
    extra = 0
    ordering = ('row', 'col')


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    inlines = (SlideInline,)
    list_display = ('pk', 'name', 'created_datetime')
    list_filter = ('is_active', 'is_deleted')
    ordering = ('-created_datetime',)
    readonly_fields = ('created_datetime', 'is_active', 'is_deleted')
    search_fields = ('name', 'description')


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    inlines = (SlideSectionInline,)
    list_display = ('pk', 'presentation', 'name', 'order')
    list_filter = ('is_active', 'is_deleted')
    list_select_related = ('presentation',)
    ordering = ('presentation', 'order')
    readonly_fields = ('created_datetime', 'is_active', 'is_deleted')
    search_fields = ('name', 'presentation__name')


@admin.register(SlideSection)
class SlideSectionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'slide', 'visual', 'row', 'col')
    list_filter = ('is_active', 'is_deleted')
    list_select_related = ('slide', 'visual')
    ordering = ('slide', 'row', 'col')
    search_fields = ('slide__name', 'visual__name')
