from typing import Type

from dandy.llm import BaseLlmMap
from dandy.map import Map

from django_spire.knowledge.collection.models import Collection


def get_collection_map_class() -> Type[BaseLlmMap]:
    class CollectionMap(BaseLlmMap):
        map_keys_description = 'Knowledge Collection Titles'
        map = Map({
            **{
                collection.name: collection
                for collection in Collection.objects.all()
            },
            **{'No Matching Knowledge Collection Titles': None}
        })

    return CollectionMap