from django_spire.seeding.seeder import BaseSeeder


class CustomSeeder(BaseSeeder):
    keyword = "custom"

    @classmethod
    @staticmethod
    def in_order(values: list, index: int) -> any:
        if index >= len(values):
            raise IndexError("Index exceeds the list length in 'in_order'")
        return values[index]

    @classmethod
    def seed(cls, manager_seeder_cls, count) -> list[dict]:
        data = []
        for i in range(count):
            row = {}
            for field_name, config in cls.seeder_fields().items():
                method_name = config[1] if len(config) > 1 else field_name
                kwargs = config[2] if len(config) > 2 else {}
                method = getattr(cls, method_name, None)

                if not callable(method):
                    raise ValueError(f"Custom method '{method_name}' not found for field '{field_name}'")

                if method_name == "in_order":
                    kwargs["index"] = i

                row[field_name] = method(**kwargs)

            data.append(row)
        return data
