from faker import Faker


class FieldSeedHelper:
    def __init__(self, locale: str | list[str] = 'en_CA') -> None:
        self.faker = Faker(locale=locale)
