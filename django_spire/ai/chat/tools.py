from importlib import import_module

from dandy.workflow import BaseWorkflow
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from pydantic import BaseModel

from django_spire.ai.decorators import log_ai_interaction_from_recorder
from django_spire.consts import AI_CHAT_WORKFLOW_CLASS_NAME


def chat_workflow_process(
        request: WSGIRequest,
        user_input: str | None = None
) -> BaseModel:
    if user_input is None:
        raise ValueError('user_input is required')

    chat_workflow_class = getattr(settings, AI_CHAT_WORKFLOW_CLASS_NAME)

    module_name = '.'.join(chat_workflow_class.split('.')[:-1])
    object_name = chat_workflow_class.split('.')[-1]

    try:
        workflow_module = import_module(module_name)
    except ImportError:
        raise ImportError(f'Could not import workflow module: {module_name}')

    ChatWorkFlow: BaseWorkflow = getattr(workflow_module, object_name)

    @log_ai_interaction_from_recorder(request.user)
    def run_workflow_process():
        return ChatWorkFlow.process(
            request=request,
            user_input=user_input,
        )

    return run_workflow_process()
