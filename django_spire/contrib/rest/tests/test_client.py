"""
Tests for the refactored REST client architecture.
"""
import pytest

from django_spire.contrib.rest.tests.example_pokemon import (
    PokemonClient,
    PokemonRestModel,
)
from django_spire.contrib.rest.queryset import RestQuerySet


class TestPokemonClient:
    """Test the Pokemon client with the new architecture."""

    def test_client_initialization(self):
        client = PokemonClient()
        assert client.base_url == 'https://pokeapi.co/api/v2'
        assert client.base_path == 'pokemon'

    def test_read_one_by_name(self):
        client = PokemonClient()
        pokemon = client.fetch_one("pikachu")

        assert isinstance(pokemon, PokemonRestModel)
        assert pokemon.id == 25
        assert pokemon.name == "pikachu"
        assert pokemon.weight == 60

    def test_read_one_by_id(self):
        client = PokemonClient()
        pokemon = client.fetch_one("25")

        assert isinstance(pokemon, PokemonRestModel)
        assert pokemon.name == "pikachu"

    def test_pokemon_has_types(self):
        client = PokemonClient()
        pokemon = client.fetch_one("pikachu")

        type_names = [t.type.name for t in pokemon.types]
        assert "electric" in type_names

    def test_read_many(self):
        client = PokemonClient()
        pokemon_list = client.fetch_many(limit=5)

        assert isinstance(pokemon_list, list)
        assert len(pokemon_list) <= 5
        assert all(isinstance(p, PokemonRestModel) for p in pokemon_list)

    def test_get_queryset(self):
        client = PokemonClient()
        qs = client.objects

        assert isinstance(qs, RestQuerySet)
