from django.db.models import QuerySet
from django.utils import timezone
from faker import Faker

from django_spire.seeding.field.base import BaseFieldSeeder
from django_spire.seeding.field.enums import FieldSeederTypesEnum


class CustomFieldSeeder(BaseFieldSeeder):
    keyword = FieldSeederTypesEnum.CUSTOM

    def in_order(self, values: list, index: int) -> any:
        index = index % len(values) # Index loops back on itself
        return values[index]

    def date_time_between(self, start_date: str, end_date: str):
        faker = Faker()
        naive_dt = faker.date_time_between(start_date=start_date, end_date=end_date)
        aware_dt = timezone.make_aware(naive_dt)
        return aware_dt

    def fk_random(self, model_class, ids: list[int]):
        faker = Faker()
        return faker.random_element(elements=ids)

    def fk_in_order(self, model_class, index: int, ids: list[int]):
        """Takes a queryset, calls it then returns a random id"""
        return self.in_order(values=ids, index=index)

    def seed(self, manager, count) -> list[dict]:
        data = []

        foreign_keys = {}

        for i in range(count):
            row = {}

            for field_name, config in self.seeder_fields.items():

                method_name = config[1] if len(config) > 1 else field_name
                kwargs = config[2] if len(config) > 2 else {}
                method = getattr(self, method_name, None)

                if not callable(method):
                    raise ValueError(f"Custom method '{method_name}' not found for field '{field_name}'")

                if method_name in ['in_order', 'fk_in_order']:
                    kwargs["index"] = i

                if method_name in ['fk_random', 'fk_in_order']:
                    model_class = kwargs["model_class"]

                    if model_class not in foreign_keys.keys():
                        foreign_keys[model_class] = model_class.objects.all().values_list('id', flat=True)

                    kwargs['ids'] = foreign_keys[model_class]

                row[field_name] = method(**kwargs)

            data.append(row)
        return data
