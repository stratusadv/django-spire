from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin
from django.db import models

if TYPE_CHECKING:
    from django.db.models import Field


class SpireModelAdmin(admin.ModelAdmin):
    model_class: type[models.Model] | None = None

    max_list_display: int = 10
    max_list_filter: int = 6
    max_search_fields: int = 5

    auto_readonly_fields: tuple[str, ...] = ('created_datetime', 'is_active', 'is_deleted')
    trailing_fields: tuple[str, ...] = ('is_active', 'is_deleted')

    sensitive_field_markers: tuple[str, ...] = (
        'api_key',
        'hashed_key',
        'passwd',
        'password',
        'private_key',
        'secret',
    )
    sensitive_field_names: tuple[str, ...] = ('code_hash', 'salt', 'token')

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        if cls.model_class is None:
            message = f'{cls.__name__} must define model_class'
            raise ValueError(message)

        cls.model_fields = cls.model_class._meta.get_fields()

        cls._configure_list_display()
        cls._configure_list_filter()
        cls._configure_list_per_page()
        cls._configure_list_select_related()
        cls._configure_ordering()
        cls._configure_readonly_fields()
        cls._configure_search_fields()

    @classmethod
    def _concrete_fields(cls) -> list[Field]:
        return [
            field
            for field in cls.model_fields
            if getattr(field, 'concrete', False) and not field.many_to_many
        ]

    @classmethod
    def _configure_list_display(cls) -> None:
        if cls._is_declared('list_display'):
            return

        field_names = [field.name for field in cls._concrete_fields()]

        trailing = [name for name in cls.trailing_fields if name in field_names]
        leading = [
            name
            for name in field_names
            if name not in cls.trailing_fields
            and not name.startswith('_')
            and not cls._is_sensitive(name)
        ]

        leading_limit = max(cls.max_list_display - len(trailing), 0)

        cls.list_display = tuple(leading[:leading_limit] + trailing)

    @classmethod
    def _configure_list_filter(cls) -> None:
        if cls._is_declared('list_filter'):
            return

        filters = [field.name for field in cls._concrete_fields() if cls._is_filterable(field)]

        cls.list_filter = tuple(filters[: cls.max_list_filter])

    @classmethod
    def _configure_list_per_page(cls) -> None:
        if cls._is_declared('list_per_page'):
            return

        cls.list_per_page = 25

    @classmethod
    def _configure_list_select_related(cls) -> None:
        if cls._is_declared('list_select_related'):
            return

        cls.list_select_related = [
            field.name
            for field in cls._concrete_fields()
            if field.many_to_one and field.name in cls.list_display
        ]

    @classmethod
    def _configure_ordering(cls) -> None:
        if cls._is_declared('ordering'):
            return

        cls.ordering = ('-pk',)

    @classmethod
    def _configure_readonly_fields(cls) -> None:
        if cls._is_declared('readonly_fields'):
            return

        cls.readonly_fields = tuple(
            field.name
            for field in cls._concrete_fields()
            if field.name in cls.auto_readonly_fields
        )

    @classmethod
    def _configure_search_fields(cls) -> None:
        if cls._is_declared('search_fields'):
            return

        search_fields = [
            field.name
            for field in cls._concrete_fields()
            if isinstance(field, (models.CharField, models.TextField))
            and not field.name.startswith('_')
            and not cls._is_sensitive(field.name)
        ]

        cls.search_fields = tuple(search_fields[: cls.max_search_fields])

    @classmethod
    def _is_declared(cls, option: str) -> bool:
        return option in cls.__dict__

    @classmethod
    def _is_filterable(cls, field: Field) -> bool:
        if isinstance(field, models.BooleanField):
            return True

        if isinstance(field, (models.DateField, models.DateTimeField)):
            return True

        return isinstance(field, models.CharField) and bool(field.choices)

    @classmethod
    def _is_sensitive(cls, field_name: str) -> bool:
        if field_name in cls.sensitive_field_names:
            return True

        return any(marker in field_name for marker in cls.sensitive_field_markers)
