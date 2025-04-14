import json
import traceback
import uuid

from dandy.recorder import Recorder
from django.contrib.auth.models import AbstractBaseUser
from django.utils.timezone import now
from typing_extensions import Any

from django_spire.ai.models import AiInteraction, AiUsage


def log_ai_interaction_from_recorder(
        user: AbstractBaseUser | None = None,
        actor: str | None = None,
):
    if user is None and actor is None:
        raise ValueError('user or actor must be provided')

    def decorator(func):
        def wrapper(*args, **kwargs):
            recording_uuid = f'Recording-{uuid.uuid4()}'

            ai_usage, _ = AiUsage.objects.get_or_create(
                recorded_date=now()
            )

            ai_interaction = AiInteraction(
                user=user,
                actor=actor,
                module_name=func.__module__,
                callable_name=func.__qualname__,
            )

            try:
                Recorder.start_recording(recording_uuid)
                return func(*args, **kwargs)

            except Exception as e:
                ai_usage.was_successful = False

                ai_interaction.was_successful = False
                ai_interaction.exception = str(e)

                stack_trace = '\n'.join([
                    ''.join(traceback.format_exception(None, e, e.__traceback__)).strip()
                ])

                ai_interaction.stack_trace = stack_trace

                raise e

            finally:
                Recorder.stop_recording(recording_uuid)

                recording = Recorder.get_recording(recording_uuid)

                ai_interaction.interaction = json.loads(Recorder.to_json_str(recording_uuid))

                ai_usage.event_count += recording.event_count
                ai_usage.token_usage += recording.token_usage
                ai_usage.run_time_seconds += recording.run_time_seconds

                ai_usage.save()

                ai_interaction.ai_usage = ai_usage
                ai_interaction.event_count = recording.event_count
                ai_interaction.token_usage = recording.token_usage
                ai_interaction.run_time_seconds = recording.run_time_seconds

                ai_interaction.save()

        return wrapper

    return decorator
