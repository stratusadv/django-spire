from django_spire.contrib.seeding.field.base import BaseFieldSeeder


class StaticFieldSeeder(BaseFieldSeeder):
    keyword = "static"

    def seed(self, manager = None, count = 1) -> list:
        return [
            {field_name: value[1] for field_name, value in self.seeder_fields.items()}
            for _ in range(count)
        ]
