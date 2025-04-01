

class SeederMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        raw_fields = namespace.get("fields", None)

        if raw_fields is not None:
            cls.fields = cls._normalize_fields(raw_fields)

        raw_seeders = namespace.get("_seeders", None)

        if raw_seeders is not None:
            cls._seeder_keywords = [seeder.keyword for seeder in raw_seeders]

        return cls
