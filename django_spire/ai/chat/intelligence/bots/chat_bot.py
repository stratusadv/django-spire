from dandy import Bot

from django_spire.ai.chat.intelligence.prompts import organization_prompt


class ChatBot(Bot):
    llm_config = 'ADVANCED'
    llm_guidelines = organization_prompt()
    llm_task = (
        'Use the following information to the answer the user\'s question or concern.'
    )
