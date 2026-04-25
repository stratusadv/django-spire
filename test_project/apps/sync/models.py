from __future__ import annotations

from django.db import models
from django.urls import reverse

from django_spire.contrib.breadcrumb import Breadcrumbs
from django_spire.contrib.sync.django.mixin import SyncableMixin

from test_project.apps.sync import choices


class Client(SyncableMixin):
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, default='')
    contact_email = models.EmailField(default='')

    class Meta:
        app_label = 'test_project_sync'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_breadcrumb('Clients', reverse('sync:page:list', kwargs={'model': 'client'}))
        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)
        if self.pk:
            crumbs.add_breadcrumb(str(self), reverse('sync:page:detail', kwargs={'model': 'client', 'pk': self.pk}))
        return crumbs

    def get_absolute_url(self) -> str:
        return reverse('sync:page:detail', kwargs={'model': 'client', 'pk': self.pk})


class Site(SyncableMixin):
    client = models.ForeignKey(
        'test_project_sync.Client',
        on_delete=models.CASCADE,
        related_name='sites',
        related_query_name='site',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(default='')
    region = models.CharField(max_length=100, default='')
    status = models.CharField(
        max_length=20,
        choices=choices.SiteStatusChoices.choices,
        default=choices.SiteStatusChoices.PLANNING,
    )

    class Meta:
        app_label = 'test_project_sync'
        ordering = ['-sync_field_last_modified']

    def __str__(self) -> str:
        return self.name

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_breadcrumb('Sites', reverse('sync:page:list', kwargs={'model': 'site'}))
        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)
        if self.pk:
            crumbs.add_breadcrumb(str(self), reverse('sync:page:detail', kwargs={'model': 'site', 'pk': self.pk}))
        return crumbs

    def get_absolute_url(self) -> str:
        return reverse('sync:page:detail', kwargs={'model': 'site', 'pk': self.pk})


class SurveyPlan(SyncableMixin):
    site = models.ForeignKey(
        'test_project_sync.Site',
        on_delete=models.CASCADE,
        related_name='plans',
        related_query_name='plan',
    )
    plan_number = models.CharField(max_length=20, default='')

    # Office configures
    stake_spacing_m = models.DecimalField(default=50, decimal_places=1, max_digits=6)
    line_direction = models.CharField(
        max_length=5,
        choices=choices.LineDirectionChoices.choices,
        default=choices.LineDirectionChoices.NS,
    )
    headland_offset_m = models.DecimalField(default=0, decimal_places=1, max_digits=6)
    office_notes = models.TextField(default='')

    # Crew sets in the field
    baseline_a_latitude = models.FloatField(default=0)
    baseline_a_longitude = models.FloatField(default=0)
    baseline_b_latitude = models.FloatField(default=0)
    baseline_b_longitude = models.FloatField(default=0)
    heading_degrees = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    crew_notes = models.TextField(default='')

    status = models.CharField(
        max_length=20,
        choices=choices.PlanStatusChoices.choices,
        default=choices.PlanStatusChoices.DRAFT,
    )

    class Meta:
        app_label = 'test_project_sync'
        ordering = ['-sync_field_last_modified']

    def __str__(self) -> str:
        return f'{self.site.name} — {self.plan_number}' if self.plan_number else str(self.site)

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_breadcrumb('Survey Plans', reverse('sync:page:list', kwargs={'model': 'surveyplan'}))
        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)
        if self.pk:
            crumbs.add_breadcrumb(str(self), reverse('sync:page:detail', kwargs={'model': 'surveyplan', 'pk': self.pk}))
        return crumbs

    def get_absolute_url(self) -> str:
        return reverse('sync:page:detail', kwargs={'model': 'surveyplan', 'pk': self.pk})


class Stake(SyncableMixin):
    survey_plan = models.ForeignKey(
        'test_project_sync.SurveyPlan',
        on_delete=models.CASCADE,
        related_name='stakes',
        related_query_name='stake',
    )

    # Crew places
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    elevation = models.FloatField(default=0)
    is_placed = models.BooleanField(default=False)

    # Office configures
    stake_type = models.CharField(
        max_length=20,
        choices=choices.StakeTypeChoices.choices,
        default=choices.StakeTypeChoices.BOUNDARY,
    )
    label = models.CharField(max_length=50, default='')

    class Meta:
        app_label = 'test_project_sync'
        ordering = ['label']

    def __str__(self) -> str:
        return self.label or f'Stake ({self.latitude:.4f}, {self.longitude:.4f})'

    @classmethod
    def base_breadcrumb(cls) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_breadcrumb('Stakes', reverse('sync:page:list', kwargs={'model': 'stake'}))
        return crumbs

    def breadcrumbs(self) -> Breadcrumbs:
        crumbs = Breadcrumbs()
        crumbs.add_base_breadcrumb(self._meta.model)
        if self.pk:
            crumbs.add_breadcrumb(str(self), reverse('sync:page:detail', kwargs={'model': 'stake', 'pk': self.pk}))
        return crumbs

    def get_absolute_url(self) -> str:
        return reverse('sync:page:detail', kwargs={'model': 'stake', 'pk': self.pk})
