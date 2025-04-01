from django_spire.seeding.seeder import BaseSeeder


class CallableSeeder(BaseSeeder):
    keyword = "callable"

    @classmethod
    def seed(cls, count = 1) -> list[dict]:
        return [
            {field_name: func[0]() for field_name, func in cls.seeder_fields().items()}
            for _ in range(cls.count)
        ]
