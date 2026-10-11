from time import sleep

from pydantic import BaseModel

from django_spire.celery.runner import CeleryTaskRunner, celery_task
from django_spire.celery.tracker import CeleryTaskTracker


class TaskData(BaseModel):
    counted_seconds: int | None = None
    more: dict | None = None


def _count(tracker: CeleryTaskTracker, length: int) -> None:
    tracker.meta.data['bananas'] = 'The #&A$ is the key!'

    if length <= 5:
        tracker.set_started_and_completing_soon()
    else:
        tracker.set_started()
        tracker.set_cumulative_progress_target_value(length)

    for i in range(length):
        sleep(1)
        tracker.set_data(counted_seconds=i + 1)

        if length > 5:
            tracker.update_cumulative_progress(added_value=1)
            tracker.update_state('MAKING NOISES')

    tracker.set_data(more={'has_noises': True})


@celery_task(display_name='Pirate Noise', data_model=TaskData)
def pirate_noise_task(self: CeleryTaskRunner, length: int) -> str:
    _count(self.tracker, length)
    return 'The pirate says YA' + 'R' * length


@celery_task(display_name='Pirate Cannon', data_model=TaskData)
def pirate_cannon_task(self: CeleryTaskRunner, length: int) -> str:
    _count(self.tracker, length)
    return 'The cannon goes' + ' BOOM' * length


@celery_task(display_name='Pirate Song', data_model=TaskData)
def pirate_song_task(self: CeleryTaskRunner, length: int) -> str:
    _count(self.tracker, length)
    return 'The song sounds like' + ' YO HO' * length


@celery_task(display_name='Ninja Move', data_model=TaskData)
def ninja_move_task(self: CeleryTaskRunner, length: int) -> str:
    _count(self.tracker, length)
    return 'The ninja moves like ' + '.' * length


@celery_task(display_name='Ninja Attack', data_model=TaskData)
def ninja_attack_task(self: CeleryTaskRunner, length: int) -> str:
    _count(self.tracker, length)
    return 'The sword goes' + ' SWOOSH' * length


@celery_task(display_name='Ninja Hide', data_model=TaskData)
def ninja_hide_task(self: CeleryTaskRunner, length: int) -> str:
    _count(self.tracker, length)
    return 'The sound is' + ' Z' * length
