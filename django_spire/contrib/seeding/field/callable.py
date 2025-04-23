from django_spire.contrib.seeding.field.base import BaseFieldSeeder
from django_spire.contrib.seeding.field.enums import FieldSeederTypesEnum


class CallableFieldSeeder(BaseFieldSeeder):
    keyword = FieldSeederTypesEnum.CALLABLE

    def seed(self, manager = None, count = 1) -> list[dict]:
        return [
            {field_name: func[1]() for field_name, func in self.seeder_fields.items()}
            for _ in range(count)
        ]
