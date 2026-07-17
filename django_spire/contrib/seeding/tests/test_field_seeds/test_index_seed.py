import pytest

from django_spire.contrib.seeding.field.seed.index_seed import IndexFieldSeed


class TestIndexFieldSeed:
    @pytest.mark.parametrize(
        ('index_start', 'index_step', 'expected'),
        [
            (0, 1, [0, 1, 2]),
            (1, 1, [1, 2, 3]),
            (0, 2, [0, 2, 4]),
            (2, 3, [2, 5, 8]),
            (10, 5, [10, 15, 20]),
        ],
    )
    def test_generate_value_produces_correct_sequence(self, index_start, index_step, expected):
        seed = IndexFieldSeed(index_start=index_start, index_step=index_step)
        results = [seed.generate_value(i) for i in range(3)]
        assert results == expected

    def test_default_values_start_at_zero_step_one(self):
        seed = IndexFieldSeed()
        assert seed.generate_value(0) == 0
        assert seed.generate_value(5) == 5
        assert seed.generate_value(10) == 10

    def test_negative_index_start(self):
        seed = IndexFieldSeed(index_start=-5, index_step=1)
        assert seed.generate_value(0) == -5
        assert seed.generate_value(5) == 0

    def test_negative_index_step(self):
        seed = IndexFieldSeed(index_start=10, index_step=-1)
        assert seed.generate_value(0) == 10
        assert seed.generate_value(5) == 5

    def test_large_values(self):
        seed = IndexFieldSeed(index_start=1000000, index_step=100)
        assert seed.generate_value(0) == 1000000
        assert seed.generate_value(10) == 2000000