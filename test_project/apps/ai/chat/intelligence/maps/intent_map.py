from dandy.llm import BaseLlmMap
from dandy.map import Map

from django_spire.ai.chat.intelligence.workflows.chat_workflow import SpireChatWorkflow


class IntentLlmMap(BaseLlmMap):
    map_keys_description = 'User Chat Intents'
    map = Map({
        'The user wants to talk about a clown or clowns.': 'clowns',
        'The user wants to talk about a pirate or pirates.': 'pirates',
        'The user does not want to talk about clowns or pirates': SpireChatWorkflow,
    })
