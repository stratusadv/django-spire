from django.test import TestCase
from django.utils import timezone

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed


class TestFakeFieldSeedHelper(TestCase):
    def test_first_name_returns_callable_field_seed(self):
        seed = Seeder.fake.first_name()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.first_name
        assert seed.kwargs == {}

    def test_last_name_returns_callable_field_seed(self):
        seed = Seeder.fake.last_name()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.last_name

    def test_sentence_default_nb_words(self):
        seed = Seeder.fake.sentence()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.sentence
        assert seed.kwargs == {'nb_words': 5}

    def test_sentence_custom_nb_words(self):
        seed = Seeder.fake.sentence(nb_words=10)
        assert seed.kwargs == {'nb_words': 10}

    def test_boolean_returns_callable_field_seed(self):
        seed = Seeder.fake.boolean()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.boolean

    def test_date_between_returns_callable_with_make_aware(self):
        seed = Seeder.fake.date_between()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.date_between
        assert seed.wrapper is timezone.make_aware

    def test_date_time_between_returns_callable_with_make_aware(self):
        seed = Seeder.fake.date_time_between()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.date_time_between
        assert seed.wrapper is timezone.make_aware

    def test_date_time_between_returns_aware_datetime(self):
        seed = Seeder.fake.date_time_between()
        value = seed.generate_value(0)
        assert timezone.is_aware(value)

    def test_text_returns_callable_field_seed(self):
        seed = Seeder.fake.text()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.text
        assert seed.kwargs == {'max_nb_chars': 200}

    def test_text_custom_max_chars(self):
        seed = Seeder.fake.text(max_nb_chars=100)
        assert seed.kwargs == {'max_nb_chars': 100}

    def test_provider_valid_method(self):
        seed = Seeder.fake.provider('city')
        assert isinstance(seed, CallableFieldSeed)
        assert seed.kwargs == {}

    def test_city_returns_callable_field_seed(self):
        seed = Seeder.fake.city()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.city

    def test_company_returns_callable_field_seed(self):
        seed = Seeder.fake.company()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.company

    def test_email_returns_callable_field_seed(self):
        seed = Seeder.fake.email()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.email

    def test_name_returns_callable_field_seed(self):
        seed = Seeder.fake.name()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.name

    def test_url_returns_callable_field_seed(self):
        seed = Seeder.fake.url()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.url

    def test_uuid4_returns_callable_field_seed(self):
        seed = Seeder.fake.uuid4()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.uuid4

    def test_word_returns_callable_field_seed(self):
        seed = Seeder.fake.word()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.word

    def test_paragraph_default(self):
        seed = Seeder.fake.paragraph()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.paragraph
        assert seed.kwargs == {'nb_sentences': 3}

    def test_paragraph_custom_sentences(self):
        seed = Seeder.fake.paragraph(nb_sentences=5)
        assert seed.kwargs == {'nb_sentences': 5}

    def test_provider_with_kwargs(self):
        seed = Seeder.fake.provider('pyfloat', min=1, max=10)
        assert seed.kwargs == {'min': 1, 'max': 10}

    def test_address_returns_callable(self):
        seed = Seeder.fake.provider('address')
        assert isinstance(seed, CallableFieldSeed)

    def test_phone_number_returns_callable(self):
        seed = Seeder.fake.provider('phone_number')
        assert isinstance(seed, CallableFieldSeed)

    def test_safe_email_returns_callable(self):
        seed = Seeder.fake.provider('safe_email')
        assert isinstance(seed, CallableFieldSeed)

    def test_date_object_returns_callable_with_wrapper(self):
        seed = Seeder.fake.provider('date_object', wrapper=timezone.make_aware)
        assert isinstance(seed, CallableFieldSeed)
        assert seed.wrapper is timezone.make_aware