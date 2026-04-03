import pytest

from django_spire.contrib.rest.tests.example_pokemon import (
    PokemonClient,
    PokemonRestModel,
)
from django_spire.contrib.rest.queryset import RestQuerySet


class TestRestSchemaQuerySet:
    def test_queryset_iteration(self):
        pokemon_list = list(PokemonClient.objects.limit(3))

        assert len(pokemon_list) <= 3

    def test_first(self):
        pokemon = PokemonClient.objects.first()

        assert pokemon is not None

    def test_last(self):
        pokemon = PokemonClient.objects.last()

        assert pokemon is not None

    def test_count(self):
        count = PokemonClient.objects.limit(5).count()

        assert isinstance(count, int)
        assert count <= 5

    def test_exists(self):
        assert PokemonClient.objects.limit(1).exists() is True

    def test_chaining_returns_new_queryset(self):
        qs1 = PokemonClient.objects
        qs2 = qs1.filter(lambda x: True)
        qs3 = qs2.order_by("name")
        qs4 = qs3.limit(5)

        # Each should be a new instance (immutability)
        assert qs1 is not qs2
        assert qs2 is not qs3
        assert qs3 is not qs4
        assert all(isinstance(q, RestQuerySet) for q in [qs1, qs2, qs3, qs4])

    def test_filter_with_predicate(self):
        qs = PokemonClient.objects

        # Filter to names starting with 'b'
        filtered = list(qs.filter(lambda p: p.name.startswith('b')).limit(5))

        assert all(p.name.startswith('b') for p in filtered)

    def test_filter_with_kwargs(self):
        qs = PokemonClient.objects

        # Get first item and filter by its name
        first = qs.first()
        if first:
            filtered = list(qs.filter(name=first.name))
            assert len(filtered) >= 1
            assert filtered[0].name == first.name

    def test_limit(self):
        pokemon_list = list(PokemonClient.objects.limit(2))

        assert len(pokemon_list) <= 2

    def test_offset(self):
        all_pokemon = list(PokemonClient.objects.limit(3))
        offset_pokemon = list(PokemonClient.objects.limit(3).offset(1))

        # offset(1) should skip the first result
        if len(all_pokemon) > 1:
            assert offset_pokemon[0].name == all_pokemon[1].name

    def test_order_by_ascending(self):
        pokemon_list = list(PokemonClient.objects.order_by("name").limit(5))

        names = [p.name for p in pokemon_list]
        assert names == sorted(names)

    def test_order_by_descending(self):
        pokemon_list = list(PokemonClient.objects.order_by("-name").limit(5))

        names = [p.name for p in pokemon_list]
        assert names == sorted(names, reverse=True)

    def test_values_list_flat(self):
        names = PokemonClient.objects.limit(3).values_list("name", flat=True)

        assert isinstance(names, list)
        assert all(isinstance(n, str) for n in names)
        assert len(names) <= 3

    def test_values_list_tuple(self):
        values = PokemonClient.objects.limit(3).values_list("name", "weight")

        assert isinstance(values, list)
        assert all(isinstance(v, tuple) and len(v) == 2 for v in values)

    def test_indexing(self):
        client = PokemonClient()
        first = PokemonClient.objects[0]

        assert first is not None

    def test_slicing(self):
        sliced = PokemonClient.objects[1:4]

        assert isinstance(sliced, RestQuerySet)
        results = list(sliced)
        assert len(results) <= 3

    def test_complex_chain(self):
        """Test a complex chain of operations."""

        results = list(
            PokemonClient.objects
            .filter(lambda p: p.name is not None)
            .order_by("name")
            .limit(5)
        )

        assert isinstance(results, list)
        assert len(results) <= 5

        # Should be sorted
        if len(results) > 1:
            names = [p.name for p in results]
            assert names == sorted(names)
