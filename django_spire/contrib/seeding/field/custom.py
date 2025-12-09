from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils import timezone
from faker import Faker

from django_spire.contrib.seeding.field.base import BaseFieldSeeder
from django_spire.contrib.seeding.field.enums import FieldSeederTypesEnum

if TYPE_CHECKING:
    from datetime import datetime
    from typing_extensions import Any

    from django.db.models import Model


class CustomFieldSeeder(BaseFieldSeeder):
    keyword = FieldSeederTypesEnum.CUSTOM

    def in_order(self, values: list, index: int) -> Any:
        if not values:
            raise ValueError(
                "Cannot select from empty values list. "
                "Make sure the related model has existing records before seeding foreign keys."
            )
        index = index % len(values)  # Index loops back on itself
        return values[index]

    def date_time_between(self, start_date: str, end_date: str) -> datetime:
        faker = Faker()
        naive_dt = faker.date_time_between(start_date=start_date, end_date=end_date)
        return timezone.make_aware(naive_dt)

    def fk_random(self, model_class: type[Model], ids: list[int]) -> int:
        faker = Faker()
        return faker.random_element(elements=ids)

    def fk_in_order(self, model_class: type[Model], index: int, ids: list[int]) -> int:
        """Takes a queryset, calls it then returns a random id"""
        return self.in_order(values=ids, index=index)

    def seed(self, manager: Any, count: int) -> list[dict]:
        data = []

        foreign_keys = {}

        for i in range(count):
            row = {}

            for field_name, config in self.seeder_fields.items():
                method_name = config[1] if len(config) > 1 else field_name
                kwargs = config[2] if len(config) > 2 else {}
                method = getattr(self, method_name, None)

                if not callable(method):
                    message = f"Custom method '{method_name}' not found for field '{field_name}'"
                    raise TypeError(message)

                if method_name in ['in_order', 'fk_in_order']:
                    kwargs["index"] = i

                if method_name in ['fk_random', 'fk_in_order']:
                    model_class = kwargs["model_class"]

                    if model_class not in foreign_keys:
                        foreign_keys[model_class] = list(model_class.objects.all().values_list('id', flat=True))

                    kwargs['ids'] = foreign_keys[model_class]

                row[field_name] = method(**kwargs)

            data.append(row)

        return data
