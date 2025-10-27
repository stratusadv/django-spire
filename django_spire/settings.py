DJANGO_SPIRE_AUTH_CONTROLLERS = {
    'ai_chat': 'django_spire.ai.chat.auth.controller.BaseAiChatAuthController',
    'help_desk': 'django_spire.help_desk.auth.controller.BaseHelpDeskAuthController',
    'knowledge': 'django_spire.knowledge.auth.controller.BaseKnowledgeAuthController',
}

# AI Settings
AI_PERSONA_NAME = 'AI Assistant'
AI_CHAT_DEFAULT_CALLABLE = None
AI_SMS_CONVERSATION_DEFAULT_CALLABLE = None

ORGANIZATION_NAME = 'No Organization Provided'
ORGANIZATION_DESCRIPTION = 'No Description Provided'

# Theme Settings
DJANGO_SPIRE_DEFAULT_THEME = 'default-light'
DJANGO_SPIRE_THEME_PATH = '/static/django_spire/css/themes/{family}/app-{mode}.css'
