from importlib import import_module

from dandy.llm import MessageHistory
from dandy.workflow import BaseWorkflow
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.handlers.wsgi import WSGIRequest

from django_spire.ai.decorators import log_ai_interaction_from_recorder
from django_spire.ai.sms.intel import SmsIntel
from django_spire.consts import AI_SMS_WORKFLOW_CLASS_SETTINGS_NAME


def sms_workflow_process(
        request: WSGIRequest,
        user_input: str | None = None,
        message_history: MessageHistory | None = None,
        user: AbstractBaseUser | None = None,
        actor: str | None = None,
) -> SmsIntel:

    if user_input is None:
        raise ValueError('sms user_input is required')

    sms_workflow_class = getattr(settings, AI_SMS_WORKFLOW_CLASS_SETTINGS_NAME)
    
    if sms_workflow_class is None:
        raise ValueError(f'"{AI_SMS_WORKFLOW_CLASS_SETTINGS_NAME}" must be set in the django settings.')

    module_name = '.'.join(sms_workflow_class.split('.')[:-1])
    object_name = sms_workflow_class.split('.')[-1]

    try:
        workflow_module = import_module(module_name)
    except ImportError:
        raise ImportError(f'Could not import workflow module: {module_name}')

    SmsWorkFlow: BaseWorkflow = getattr(workflow_module, object_name)

    @log_ai_interaction_from_recorder(user=user, actor=actor)
    def run_workflow_process() -> SmsIntel:
        return SmsWorkFlow.process(
            request=request,
            user_input=user_input,
            message_history=message_history,
        )

    output_intel = run_workflow_process()

    if not issubclass(output_intel.__class__, SmsIntel):
        raise ValueError(
            f'{SmsWorkFlow.__class__.__module__}.{SmsWorkFlow.__class__.__qualname__}.process must return an instance of a {SmsIntel.__name__}.'
        )

    return output_intel
