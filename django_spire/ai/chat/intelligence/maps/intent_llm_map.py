from dandy.llm import BaseLlmMap
from dandy.map import Map


class IntentLlmMap(BaseLlmMap):
    map_keys_description = 'The user\'s chat intent'
    map = Map({})
