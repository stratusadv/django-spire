from django.test import TestCase

from django_spire.contrib.seeding.field.seed.mutate.choices import MutateSeverity


class TestMutateSeverity(TestCase):
    def test_mild_value(self):
        assert MutateSeverity.MILD.value == 'mild'

    def test_moderate_value(self):
        assert MutateSeverity.MODERATE.value == 'moderate'

    def test_chaos_value(self):
        assert MutateSeverity.CHAOS.value == 'chaos'

    def test_is_enum_member(self):
        assert MutateSeverity.MILD in MutateSeverity

    def test_all_severities_exist(self):
        assert len(MutateSeverity) == 3

    def test_string_representation(self):
        assert str(MutateSeverity.MILD) == 'MutateSeverity.MILD'

    def test_value_representation(self):
        assert MutateSeverity.MILD.value == 'mild'
        assert MutateSeverity.MODERATE.value == 'moderate'
        assert MutateSeverity.CHAOS.value == 'chaos'

    def test_equality_by_value(self):
        assert MutateSeverity.MILD == MutateSeverity('mild')
        assert MutateSeverity.MODERATE == MutateSeverity('moderate')
        assert MutateSeverity.CHAOS == MutateSeverity('chaos')