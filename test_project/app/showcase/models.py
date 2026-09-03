from __future__ import annotations

import uuid as uuid_lib

from django.contrib.auth.models import User
from django.db import models
from django_glue import Glue

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.querysets import HistoryQuerySet

from test_project.app.showcase.choices import PriorityChoices


class ShowcaseCategory(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Showcase Category'
        verbose_name_plural = 'Showcase Categories'
        db_table = 'test_project_showcase_category'

    def __str__(self) -> str:
        return self.name


class ShowcaseTag(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Showcase Tag'
        verbose_name_plural = 'Showcase Tags'
        db_table = 'test_project_showcase_tag'

    def __str__(self) -> str:
        return self.name


class WidgetShowcase(ActivityMixin, HistoryModelMixin):
    """
    One model field per template under
    django_spire/core/templates/django_spire/glue/form/field/, so
    showcase/form/form.html can render every glue form widget in one page.
    """

    # boolean/field.html
    boolean_field = models.BooleanField(default=False)

    # char/*
    char_field = models.CharField(max_length=255, blank=True, default='')
    color_field = models.CharField(max_length=7, blank=True, default='#0d6efd')
    email_field = models.EmailField(blank=True, default='')
    password_field = models.CharField(max_length=255, blank=True, default='')
    postal_code_field = models.CharField(max_length=20, blank=True, default='')
    search_field = models.CharField(max_length=255, blank=True, default='')
    slug_field = models.SlugField(blank=True, default='')
    telephone_field = models.CharField(max_length=20, blank=True, default='')
    url_field = models.URLField(blank=True, default='')
    uuid_field = models.UUIDField(default=uuid_lib.uuid4)

    # choice/*
    select_choice = models.CharField(
        max_length=4, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM
    )
    checkbox_tags = models.ManyToManyField(
        ShowcaseTag, blank=True, related_name='checkbox_showcases'
    )
    search_tags = models.ManyToManyField(ShowcaseTag, blank=True, related_name='search_showcases')
    radio_choice = models.CharField(
        max_length=4, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM
    )
    category = models.ForeignKey(
        ShowcaseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='showcases'
    )
    watchers = models.ManyToManyField(User, blank=True, related_name='watched_showcases')
    assigned_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_showcases'
    )

    # datetime/*
    date_field = models.DateField(null=True, blank=True)
    datetime_field = models.DateTimeField(null=True, blank=True)
    time_field = models.TimeField(null=True, blank=True)

    # decimal/*
    currency_field = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    decimal_field = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # float/field.html
    float_field = models.FloatField(null=True, blank=True)

    # hidden_field.html
    hidden_field = models.CharField(max_length=64, blank=True, default='')

    # integer/*
    big_integer_field = models.BigIntegerField(null=True, blank=True)
    integer_field = models.IntegerField(null=True, blank=True)
    positive_integer_field = models.PositiveIntegerField(null=True, blank=True)
    small_integer_field = models.SmallIntegerField(null=True, blank=True)

    # text/field.html
    text_field = models.TextField(blank=True, default='')

    objects = HistoryQuerySet.as_manager()

    class Meta:
        verbose_name = 'Widget Showcase'
        verbose_name_plural = 'Widget Showcases'
        db_table = 'test_project_showcase_widget_showcase'

    def __str__(self) -> str:
        return f'Widget Showcase #{self.pk}'

    # Read-only display strings for the relation fields, exposed to the live
    # model panel instead of full nested proxies -- avoids putting all of
    # auth.User on the wire (assigned_user/watchers) and keeps the panel's
    # bindings uniform (every relation reads as a plain string, same as the
    # scalar fields).
    @Glue.property
    def category_display(self) -> str:
        return self.category.name if self.category_id else '—'

    @Glue.property
    def assigned_user_display(self) -> str:
        return self.assigned_user.username if self.assigned_user_id else '—'

    @Glue.property
    def watchers_display(self) -> str:
        if self.pk is None:
            return '—'
        return ', '.join(self.watchers.values_list('username', flat=True)) or '—'

    @Glue.property
    def checkbox_tags_display(self) -> str:
        if self.pk is None:
            return '—'
        return ', '.join(self.checkbox_tags.values_list('name', flat=True)) or '—'

    @Glue.property
    def search_tags_display(self) -> str:
        if self.pk is None:
            return '—'
        return ', '.join(self.search_tags.values_list('name', flat=True)) or '—'
