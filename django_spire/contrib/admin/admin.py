from typing import Type, Tuple

from django.contrib import admin
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class SpireModelAdmin(admin.ModelAdmin):
    model_class: Type[models.Model] = None

    max_search_fields: int = 5
    max_list_display: int = 10

    trailing_fields = ('is_active', 'is_deleted')

    auto_readonly_fields: Tuple[str] = (
        'created_datetime', 'is_active', 'is_deleted',
    )

    filter_field_types = (
        models.BooleanField,
        models.DateField,
        models.DateTimeField,
        models.ForeignKey,
        models.CharField,
    )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.model_fields = cls.model_class._meta.get_fields()

        if cls.model_class is None:
            raise ValueError(f'{cls.__name__} must define model_class')

        if not hasattr(cls, '_spire_configured'):
            cls._configure_list_display()
            cls._configure_list_filter()
            cls._configure_search_fields()
            cls._configure_readonly_fields()
            cls._configure_ordering()
            cls._configure_list_per_page()
            cls._spire_configured = True

    @classmethod
    def _configure_list_display(cls):
        if cls.list_display != ('__str__',):
            return

        fields = []

        for field in cls.model_fields:
            if not isinstance(
                field,
                (models.ManyToManyField, models.ManyToOneRel, GenericRelation),
            ):
                if hasattr(field, 'name') and not field.name.startswith('_'):
                    if field.name not in cls.trailing_fields:
                        fields.append(field.name)

        for trailing_field in cls.trailing_fields:
            if trailing_field in [field.name for field in cls.model_fields]:
                fields.append(trailing_field)

        cls.list_display = tuple(fields[:cls.max_list_display])

    @classmethod
    def _configure_list_filter(cls):
        if hasattr(cls, 'list_filter') and cls.list_filter:
            return

        filters = []

        for field in cls.model_fields:
            if not isinstance(field, (models.ManyToManyField, models.ManyToOneRel)):
                if isinstance(field, models.BooleanField):
                    filters.append(field.name)

                elif isinstance(field, (models.DateField, models.DateTimeField)):
                    filters.append(field.name)

                elif isinstance(field, models.ForeignKey):
                    filters.append(field.name)

                elif (
                    isinstance(field, models.CharField)
                    and hasattr(field, 'choices')
                    and field.choices
                ):
                    filters.append(field.name)

        cls.list_filter = tuple(filters)

    @classmethod
    def _configure_search_fields(cls):
        if hasattr(cls, 'search_fields') and cls.search_fields:
            return

        search_fields = []

        for field in cls.model_fields:
            if isinstance(field, (models.CharField, models.TextField)):
                if not field.name.startswith('_'):
                    search_fields.append(field.name)

                    if len(search_fields) >= cls.max_search_fields:
                        break

        cls.search_fields = tuple(search_fields)

    @classmethod
    def _configure_readonly_fields(cls):
        if hasattr(cls, 'readonly_fields') and cls.readonly_fields:
            return

        readonly = []

        for field in cls.model_fields:
            if hasattr(field, 'name') and field.name in cls.auto_readonly_fields:
                readonly.append(field.name)

        cls.readonly_fields = tuple(readonly)

    @classmethod
    def _configure_ordering(cls):
        if hasattr(cls, 'ordering') and cls.ordering:
            return

        cls.ordering = ('-id',)
        return

    @classmethod
    def _configure_list_per_page(cls):
        if not hasattr(cls, 'list_per_page') or cls.list_per_page == 100:
            cls.list_per_page = 25
