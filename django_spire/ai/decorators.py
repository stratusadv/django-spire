import json
import traceback
import uuid

from dandy.recorder import Recorder
from django.contrib.auth.models import User

from django_spire.ai.models import AiInteraction


def log_ai_interaction_from_recorder(
        user: User,
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            recording_uuid = str(uuid.uuid4())

            ai_interaction = AiInteraction(
                user=user,
                module_name=func.__module__,
                callable_name=func.__qualname__,
            )

            try:
                Recorder.start_recording(recording_uuid)
                return func(*args, **kwargs)

            except Exception as e:
                ai_interaction.was_successful = False
                ai_interaction.exception = str(e)

                stack_trace = '\n'.join([
                    ''.join(traceback.format_exception(None, e, e.__traceback__)).strip()
                ])

                ai_interaction.stack_trace = stack_trace

                raise e

            finally:
                Recorder.stop_recording(recording_uuid)

                ai_interaction.interaction = json.loads(Recorder.to_json_str(recording_uuid))

                ai_interaction.save()

        return wrapper

    return decorator
