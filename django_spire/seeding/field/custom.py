from django.utils import timezone
from faker import Faker

from django_spire.seeding.field.base import BaseFieldSeeder
from django_spire.seeding.field.enums import FieldSeederTypesEnum


class CustomFieldSeeder(BaseFieldSeeder):
    keyword = FieldSeederTypesEnum.CUSTOM

    def in_order(self, values: list, index: int) -> any:
        if index >= len(values):
            raise IndexError("Index exceeds the list length in 'in_order'")
        return values[index]

    def date_time_between(self, start_date: str, end_date: str):
        faker = Faker()
        naive_dt = faker.date_time_between(start_date=start_date, end_date=end_date)
        aware_dt = timezone.make_aware(naive_dt)
        return aware_dt

    def seed(self, manager, count) -> list[dict]:
        data = []
        for i in range(count):
            row = {}
            for field_name, config in self.seeder_fields.items():
                method_name = config[1] if len(config) > 1 else field_name
                kwargs = config[2] if len(config) > 2 else {}
                method = getattr(self, method_name, None)

                if not callable(method):
                    raise ValueError(f"Custom method '{method_name}' not found for field '{field_name}'")

                if method_name == "in_order":
                    kwargs["index"] = i

                row[field_name] = method(**kwargs)

            data.append(row)
        return data
