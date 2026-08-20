from __future__ import annotations

import pytest

from django.contrib.auth.models import User
from django.test import TestCase

from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.app.task.models import Task


class SpireModelAdminConfigurationTests(TestCase):
    def test_missing_model_class_raises_value_error(self):
        with pytest.raises(ValueError, match='must define model_class'):

            class NoModelAdmin(SpireModelAdmin):
                pass

    def test_subclass_reconfigures_for_its_own_model(self):
        class TaskAdmin(SpireModelAdmin):
            model_class = Task

        class UserAdmin(TaskAdmin):
            model_class = User

        assert UserAdmin.list_display != TaskAdmin.list_display
        assert 'username' in UserAdmin.list_display

    def test_declared_options_are_preserved(self):
        class DeclaredAdmin(SpireModelAdmin):
            model_class = Task

            list_display = ('name',)
            list_per_page = 100
            ordering = ('name',)
            search_fields = ('name',)

        assert DeclaredAdmin.list_display == ('name',)
        assert DeclaredAdmin.list_per_page == 100
        assert DeclaredAdmin.ordering == ('name',)
        assert DeclaredAdmin.search_fields == ('name',)

    def test_foreign_keys_are_select_related_not_filtered(self):
        class TaskAdmin(SpireModelAdmin):
            model_class = Task

        assert 'parent' in TaskAdmin.list_display
        assert 'parent' in TaskAdmin.list_select_related
        assert 'parent' not in TaskAdmin.list_filter

    def test_sensitive_fields_are_not_auto_exposed(self):
        class UserAdmin(SpireModelAdmin):
            model_class = User

        assert 'password' not in UserAdmin.list_display
        assert 'password' not in UserAdmin.search_fields

    def test_trailing_fields_survive_display_truncation(self):
        class NarrowAdmin(SpireModelAdmin):
            model_class = Task

            max_list_display = 3

        assert NarrowAdmin.list_display[-2:] == ('is_active', 'is_deleted')
        assert len(NarrowAdmin.list_display) == 3

    def test_reverse_relations_are_excluded_from_list_display(self):
        class TaskAdmin(SpireModelAdmin):
            model_class = Task

        for name in TaskAdmin.list_display:
            assert Task._meta.get_field(name).concrete
