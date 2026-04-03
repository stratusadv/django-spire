from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from django_spire.contrib.rest.client.model import RestModelClient


class NamedAPIResourceRestModel(BaseModel):
    name: str
    url: str


class PokemonSpritesRestModel(BaseModel):
    front_default: Optional[str] = None
    front_shiny: Optional[str] = None
    back_default: Optional[str] = None


class PokemonAbilityRestModel(BaseModel):
    ability: NamedAPIResourceRestModel
    is_hidden: bool
    slot: int


class PokemonTypeRestModel(BaseModel):
    slot: int
    type: NamedAPIResourceRestModel


class PokemonStatRestModel(BaseModel):
    base_stat: int
    effort: int
    stat: NamedAPIResourceRestModel


class PokemonMoveRestModel(BaseModel):
    move: NamedAPIResourceRestModel


class PokemonRestModel(BaseModel):
    id: int
    name: str
    base_experience: Optional[int] = None
    height: int
    weight: int
    is_default: bool
    order: int
    abilities: list[PokemonAbilityRestModel]
    types: list[PokemonTypeRestModel]
    stats: list[PokemonStatRestModel]
    moves: list[PokemonMoveRestModel]
    sprites: PokemonSpritesRestModel


class PokemonClient(RestModelClient[PokemonRestModel]):
    base_url = 'https://pokeapi.co/api/v2'
    base_path = 'pokemon'

    def fetch_one(self, id_or_name: str) -> PokemonRestModel:
        response = self.get(path=id_or_name)
        return PokemonRestModel(**response.json())

    def fetch_many(self, **request_params) -> list[PokemonRestModel]:
        response = self.get(params=request_params)
        data = response.json()

        return [self.fetch_one(id_or_name=result['name']) for result in data['results']]
