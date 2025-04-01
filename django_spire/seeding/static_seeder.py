from django_spire.seeding.seeder import BaseSeeder


class StaticSeeder(BaseSeeder):
    keyword = "static"

    @classmethod
    def seed(cls, count = 1) -> list:
        return [
            {field_name: value[1] for field_name, value in cls.seeder_fields().items()}
            for _ in range(count)
        ]
