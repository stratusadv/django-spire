from typing import Callable

from django.utils import timezone

from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed
from django_spire.contrib.seeding.field.seed.helper.helper import FieldSeedHelper


class FakeFieldSeedHelper(FieldSeedHelper):
    def boolean(self) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.boolean)

    def city(self) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.city)

    def company(self) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.company)

    def date_between(self, start_date: str = '-30d', end_date: str = '+30d') -> CallableFieldSeed:
        return CallableFieldSeed(
            callable_=self.faker.date_between,
            wrapper=timezone.make_aware,
            start_date=start_date,
            end_date=end_date,
        )

    def date_time_between(
        self, start_date: str = '-30d', end_date: str = '+30d'
    ) -> CallableFieldSeed:
        return CallableFieldSeed(
            callable_=self.faker.date_time_between,
            wrapper=timezone.make_aware,
            start_date=start_date,
            end_date=end_date,
        )

    def email(self) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.email)

    def first_name(self) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.first_name)

    def last_name(self) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.last_name)

    def name(self) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.name)

    def paragraph(self, nb_sentences: int = 3) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.paragraph, nb_sentences=nb_sentences)

    def provider(
        self, provider_callable: str, wrapper: Callable | None = None, **kwargs
    ) -> CallableFieldSeed:
        return CallableFieldSeed(
            callable_=getattr(self.faker, provider_callable), wrapper=wrapper, **kwargs
        )

    def sentence(self, nb_words: int = 5) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.sentence, nb_words=nb_words)

    def text(self, max_nb_chars: int = 200) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.text, max_nb_chars=max_nb_chars)

    def url(self) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.url)

    def uuid4(self) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.uuid4)

    def word(self) -> CallableFieldSeed:
        return CallableFieldSeed(callable_=self.faker.word)
