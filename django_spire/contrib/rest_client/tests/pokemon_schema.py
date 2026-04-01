from typing import Optional, ClassVar

from pydantic import BaseModel

from django_spire.contrib.rest_client.tests.pokemon_client import PokemonClient


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
    #
    # def location_area_encounters(self) -> list['LocationAreaEncounter']:
    #     return self.api.location_area_encounters_by_pokemon_id(f'{self.id}')