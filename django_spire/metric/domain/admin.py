from __future__ import annotations

from django.contrib import admin

from django_spire.metric.domain.models import Domain, SubDomain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description', 'sub_domain_description', 'created_datetime')
    list_filter = ('is_active', 'is_deleted')
    ordering = ('-created_datetime',)
    readonly_fields = ('created_datetime', 'is_active', 'is_deleted')
    search_fields = ('name', 'description')


@admin.register(SubDomain)
class SubDomainAdmin(admin.ModelAdmin):
    list_display = ('pk', 'domain', 'name', 'description', 'created_datetime')
    list_filter = ('is_active', 'is_deleted')
    list_select_related = ('domain',)
    ordering = ('-created_datetime',)
    readonly_fields = ('created_datetime', 'is_active', 'is_deleted')
    search_fields = ('name', 'description', 'domain__name')
