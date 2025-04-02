from django_spire.seeding.field.base import BaseFieldSeeder
from django_spire.seeding.field.enums import FieldSeederTypesEnum


class CustomFieldSeeder(BaseFieldSeeder):
    keyword = FieldSeederTypesEnum.CUSTOM

    @staticmethod
    def in_order(values: list, index: int) -> any:
        if index >= len(values):
            raise IndexError("Index exceeds the list length in 'in_order'")
        return values[index]

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
