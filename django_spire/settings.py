DJANGO_SPIRE_AUTH_CONTROLLERS = {
    'ai_chat': 'django_spire.ai.chat.auth.controller.BaseAiChatAuthController',
    'help_desk': 'django_spire.help_desk.auth.controller.BaseHelpDeskAuthController',
    'knowledge': 'django_spire.knowledge.auth.controller.BaseKnowledgeAuthController',
}

# AI Settings
DJANGO_SPIRE_AI_PERSONA_NAME = 'AI Assistant'
DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER = 'SPIRE'

DJANGO_SPIRE_AI_CHAT_ROUTERS = {
    'SPIRE': 'django_spire.ai.chat.router.SpireChatRouter',
}

DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS = {
    'KNOWLEDGE_SEARCH': {
        'INTENT_DESCRIPTION': 'The user is asking about information in the knowledge base.',
        'REQUIRED_PERMISSION': 'django_spire_knowledge.view_collection',
        'CHAT_ROUTER': 'django_spire.knowledge.intelligence.router.KnowledgeSearchRouter',
    },
}

# Theme Settings
DJANGO_SPIRE_DEFAULT_THEME = 'default-light'
DJANGO_SPIRE_THEME_PATH = '/static/django_spire/css/themes/{family}/app-{mode}.css'
