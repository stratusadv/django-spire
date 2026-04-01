from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Optional, ClassVar

from pydantic import BaseModel

from django_spire.contrib.rest_client.client import BaseRestApiClient, TDefaultResponseSchema


class BasePokemonClient(BaseRestApiClient[TDefaultResponseSchema], ABC):
    _base_url = 'https://pokeapi.co/api/v2'


class PokemonClient(BasePokemonClient['Pokemon']):
    _base_url_path = 'pokemon'

    def by_id(self, id_or_name: str) -> 'Pokemon':
        return self._get(id_or_name).to_single_obj()

    def location_area_encounters_by_pokemon_id(self, id_or_name: str) -> list['LocationAreaEncounter']:
        return self._get(f'{id_or_name}/encounters').to_obj_list(LocationAreaEncounter)


class PokemonSprites(BaseModel):
    front_default: Optional[str] = None
    front_shiny: Optional[str] = None
    front_female: Optional[str] = None
    front_shiny_female: Optional[str] = None
    back_default: Optional[str] = None
    back_shiny: Optional[str] = None
    back_female: Optional[str] = None
    back_shiny_female: Optional[str] = None


class NamedAPIResource(BaseModel):
    name: str
    url: str


class PokemonAbility(BaseModel):
    ability: NamedAPIResource
    is_hidden: bool
    slot: int


class PokemonType(BaseModel):
    slot: int
    type: NamedAPIResource


class PokemonStat(BaseModel):
    base_stat: int
    effort: int
    stat: NamedAPIResource


class PokemonMove(BaseModel):
    move: NamedAPIResource


class EncounterDetail(BaseModel):
    chance: int
    method: NamedAPIResource


class VersionEncounterDetail(BaseModel):
    version: NamedAPIResource
    max_chance: int
    encounter_details: list['EncounterDetail']


class LocationAreaEncounter(BaseModel):
    location_area: NamedAPIResource
    version_details: list['VersionEncounterDetail']


class Pokemon(BaseModel):
    id: int
    name: str
    base_experience: Optional[int] = None
    height: int
    weight: int
    is_default: bool
    order: int
    abilities: list[PokemonAbility]
    types: list[PokemonType]
    stats: list[PokemonStat]
    moves: list[PokemonMove]
    sprites: PokemonSprites

    api: ClassVar = PokemonClient()

    def location_area_encounters(self) -> list['LocationAreaEncounter']:
        return self.api.location_area_encounters_by_pokemon_id(f'{self.id}')