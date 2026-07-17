from django.test import TestCase

from django_spire.contrib.seeding.field.seed.llm_seed import LlmFieldSeed


class TestLlmFieldSeed(TestCase):
    def test_generate_value_returns_none(self):
        seed = LlmFieldSeed(field_type=str)
        assert seed.generate_value(0) is None

    def test_stores_field_type(self):
        seed = LlmFieldSeed(field_type=str)
        assert seed.field_type is str

    def test_stores_field_type_int(self):
        seed = LlmFieldSeed(field_type=int)
        assert seed.field_type is int

    def test_stores_prompt_none_by_default(self):
        seed = LlmFieldSeed(field_type=str)
        assert seed.prompt is None

    def test_stores_custom_prompt(self):
        seed = LlmFieldSeed(field_type=str, prompt='Test prompt')
        assert seed.prompt == 'Test prompt'

    def test_stores_locale_default(self):
        seed = LlmFieldSeed(field_type=str)
        assert seed.locale == 'en_CA'

    def test_stores_custom_locale(self):
        seed = LlmFieldSeed(field_type=str, locale='fr_FR')
        assert seed.locale == 'fr_FR'

    def test_field_type_can_be_list(self):
        seed = LlmFieldSeed(field_type=list)
        assert seed.field_type is list

    def test_field_type_can_be_dict(self):
        seed = LlmFieldSeed(field_type=dict)
        assert seed.field_type is dict

    def test_multiple_locales(self):
        seed = LlmFieldSeed(field_type=str, locale=['en_US', 'en_GB'])
        assert seed.locale == ['en_US', 'en_GB']

    def test_generate_value_ignores_seed_index(self):
        seed = LlmFieldSeed(field_type=str)
        for i in range(10):
            assert seed.generate_value(i) is None