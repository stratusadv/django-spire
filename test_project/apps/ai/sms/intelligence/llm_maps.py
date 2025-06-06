from dandy.llm import BaseLlmMap
from dandy.map import Map


class IntentLlmMap(BaseLlmMap):
    map_keys_description = 'User Chat Intents'
    map = Map({
        'the user wants to talk about a clown or clowns': 'clowns',
        'the user wants to talk about business': 'business',
        'the user wants to talk about a pirate or pirates': 'pirates',
        'the user does not want to talk about clowns, business or pirates': 'general',
    })
