DJANGO_SPIRE_AUTH_CONTROLLERS = {
    'ai_chat': 'django_spire.ai.chat.auth.controller.BaseAiChatAuthController',
    'knowledge': 'django_spire.knowledge.auth.controller.BaseKnowledgeAuthController'
}


# AI Settings
AI_CHAT_WORKFLOW_NAME = 'AI Assistant'
AI_CHAT_WORKFLOW_CLASS = 'django_spire.ai.chat.intelligence.workflows.chat_workflow.ChatWorkflow'
AI_SMS_CONVERSATION_WORKFLOW_CLASS = 'django_spire.ai.sms.intelligence.workflows.sms_conversation_workflow.SmsConversationWorkflow'

ORGANIZATION_NAME = 'No Organization Provided'
ORGANIZATION_DESCRIPTION = 'No Description Provided'
