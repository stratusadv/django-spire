

class FieldOverride:
    def __init__(self, seeder_cls):
        self.seeder_cls = seeder_cls
        self.overrides = {}

    def filter(self, **kwargs):
        self.overrides.update(kwargs)
        return self

    def seed(self, count=1):
        return self.seeder_cls.seed(count=count, fields=self.overrides)

    def seed_database(self, count=1):
        return self.seeder_cls.seed_database(count=count, fields=self.overrides)
