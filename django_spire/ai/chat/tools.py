from importlib import import_module

from dandy.llm import MessageHistory
from dandy.workflow import BaseWorkflow
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest

from django_spire.ai.chat.message_intel import BaseMessageIntel
from django_spire.ai.decorators import log_ai_interaction_from_recorder
from django_spire.consts import AI_CHAT_WORKFLOW_CLASS_SETTINGS_NAME


def chat_workflow_process(
        request: WSGIRequest,
        user_input: str | None = None,
        message_history: MessageHistory | None = None,
) -> BaseMessageIntel:

    if user_input is None:
        raise ValueError('user_input is required')

    chat_workflow_class = getattr(settings, AI_CHAT_WORKFLOW_CLASS_SETTINGS_NAME)
    
    if chat_workflow_class is None:
        raise ValueError(f'"{AI_CHAT_WORKFLOW_CLASS_SETTINGS_NAME}" must be set in the django settings.')

    module_name = '.'.join(chat_workflow_class.split('.')[:-1])
    object_name = chat_workflow_class.split('.')[-1]

    try:
        workflow_module = import_module(module_name)
    except ImportError:
        raise ImportError(f'Could not import workflow module: {module_name}')

    ChatWorkFlow: BaseWorkflow = getattr(workflow_module, object_name)

    @log_ai_interaction_from_recorder(request.user)
    def run_workflow_process() -> BaseMessageIntel:
        return ChatWorkFlow.process(
            request=request,
            user_input=user_input,
            message_history=message_history,
        )

    output_intel = run_workflow_process()

    if not issubclass(output_intel.__class__, BaseMessageIntel):
        raise ValueError(
            f'{ChatWorkFlow.__class__.__module__}.{ChatWorkFlow.__class__.__qualname__}.process must return an instance of a {BaseMessageIntel.__name__} sub class.'
        )

    return output_intel
