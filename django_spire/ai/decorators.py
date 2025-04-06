import json
import uuid

from dandy.recorder import Recorder
from django.contrib.auth.models import User

from django_spire.ai.models import AiInteraction


def log_ai_interaction_from_recorder(
        user: User,
        app_name: str,
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            recording_uuid = str(uuid.uuid4())

            ai_interaction = AiInteraction(
                user=user,
                app_name=app_name,
            )

            try:
                Recorder.start_recording(recording_uuid)
                return func(*args, **kwargs)

            except Exception as e:
                ai_interaction.raised_exception = True
                ai_interaction.exception = str(e)
                ai_interaction.stack_trace = str(e.__traceback__)

                raise e

            finally:
                Recorder.stop_recording(recording_uuid)

                ai_interaction.interaction = json.loads(Recorder.to_json_str(recording_uuid))

                ai_interaction.save()

        return wrapper

    return decorator
