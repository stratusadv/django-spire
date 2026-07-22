from faker import Faker


class FieldSeedHelper:
    def __init__(self, locale: str | list[str] = 'en_CA') -> None:
        self.locale = locale

    @property
    def faker(self) -> Faker:
        return Faker(locale=self.locale)
