from dandy import Bot


class ChatBot(Bot):
    llm_config = 'ADVANCED'
    llm_task = (
        'Use the following information to the answer the user\'s question or concern.'
    )
