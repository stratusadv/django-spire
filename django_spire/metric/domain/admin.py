from __future__ import annotations

from django.contrib import admin

from django_spire.metric.domain.models import Domain, SubDomain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description', 'sub_domain_description', 'created_datetime')
    list_filter = ('is_active', 'is_deleted')
    ordering = ('-created_datetime',)
    readonly_fields = ('created_datetime', 'is_active', 'is_deleted')
    search_fields = ('description', 'created_by__username', 'created_by__email')


@admin.register(SubDomain)
class SubDomainAdmin(admin.ModelAdmin):
    list_display = ('pk', 'domain_id', 'name', 'description', 'created_datetime')
    list_filter = ('is_active', 'is_deleted')
    ordering = ('-created_datetime',)
    readonly_fields = ('created_datetime', 'is_active', 'is_deleted')
    search_fields = ('description', 'created_by__username', 'created_by__email')
