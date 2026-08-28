from __future__ import annotations


DJANGO_SPIRE_AUTH_CONTROLLERS = {
    'ai_chat': 'django_spire.ai.chat.auth.controller.BaseAiChatAuthController',
    'api': 'django_spire.api.auth.controller.BaseApiAuthController',
    'help_desk': 'django_spire.help_desk.auth.controller.BaseHelpDeskAuthController',
    'knowledge': 'django_spire.knowledge.auth.controller.BaseKnowledgeAuthController',
    'metric': 'django_spire.metric.auth.controller.BaseMetricAuthController',
    'report': 'django_spire.metric.report.auth.controller.BaseReportAuthController',
}

DJANGO_SPIRE_CHANGELOG_MODULE = 'changelog.changelog'

# AI Settings
DJANGO_SPIRE_AI_PERSONA_NAME = 'AI Assistant'
DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER = 'SPIRE'

DJANGO_SPIRE_AI_CHAT_ROUTERS = {'SPIRE': 'django_spire.ai.chat.router.SpireChatRouter'}

DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS = {
    'KNOWLEDGE_SEARCH': {
        'INTENT_DESCRIPTION': 'The user is asking about information, help or support that could be found in knowledge base.',
        'REQUIRED_PERMISSION': 'django_spire_knowledge.view_collection',
        'CHAT_ROUTER': 'django_spire.knowledge.intelligence.router.KnowledgeSearchRouter',
    }
}

DJANGO_SPIRE_AI_SMS_BODY_LENGTH_MAX = 1000

# Auth SMS Settings
DJANGO_SPIRE_AUTH_SMS_CODE_ATTEMPT_COUNT_MAX = 5
DJANGO_SPIRE_AUTH_SMS_CODE_EXPIRY_MINUTES = 10
DJANGO_SPIRE_AUTH_SMS_SESSION_DURATION_MINUTES_MAX = 480
DJANGO_SPIRE_AUTH_SMS_SESSION_IDLE_MINUTES_MAX = 30
DJANGO_SPIRE_AUTH_SMS_THROTTLE_RATE_PER_DAY = 200
DJANGO_SPIRE_AUTH_SMS_THROTTLE_RATE_PER_MINUTE = 5

DJANGO_SPIRE_NAVIGATION_HOME_URL = None

DJANGO_SPIRE_REPORT_REGISTRIES = []

# Theme Settings
DJANGO_SPIRE_DEFAULT_THEME_MODE = 'light'

DJANGO_SPIRE_NOTIFICATION_THROTTLE_RATE_PER_MINUTE = 100

# Metric Settings

DJANGO_SPIRE_METRIC_TRACKING_END_POINT = ''
DJANGO_SPIRE_METRIC_TRACKING_KEY = ''

DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX = 1000

DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY = ''
DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY = ''
