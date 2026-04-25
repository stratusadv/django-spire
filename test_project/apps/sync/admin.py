from __future__ import annotations

from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin

from test_project.apps.sync.models import Client, Site, Stake, SurveyPlan


@admin.register(Client)
class ClientAdmin(SpireModelAdmin):
    model_class = Client
    list_display = ('name', 'contact_name', 'contact_email')


@admin.register(Site)
class SiteAdmin(SpireModelAdmin):
    model_class = Site
    list_display = ('name', 'region', 'status')


@admin.register(SurveyPlan)
class SurveyPlanAdmin(SpireModelAdmin):
    model_class = SurveyPlan
    list_display = ('plan_number', 'site', 'status')


@admin.register(Stake)
class StakeAdmin(SpireModelAdmin):
    model_class = Stake
    list_display = ('label', 'stake_type', 'is_placed')
