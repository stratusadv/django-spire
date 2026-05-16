from time import sleep

from celery import shared_task, Task

from django_spire.celery.tracker import CeleryTaskTracker


def _sleep(task: Task, length: int) -> None:
    tracker = CeleryTaskTracker(task)
    tracker.update_state('MAKING NOISES')
    for i in range(length):
        tracker.update_cumulative_progress(1, length)
        sleep(1)

    tracker.set_completed()

@shared_task(bind=True)
def pirate_noise_task(self, length: int) -> str:
    _sleep(self, length)
    return 'The pirate says YA' + 'R' * length


@shared_task(bind=True)
def pirate_cannon_task(self, length: int) -> str:
    _sleep(self, length)
    return 'The cannon goes' + ' BOOM' * length


@shared_task(bind=True)
def pirate_song_task(self, length: int) -> str:
    _sleep(self, length)
    return 'The song sounds like' + ' YO HO' * length


@shared_task(bind=True)
def ninja_move_task(self, length: int) -> str:
    _sleep(self, length)
    return 'The ninja moves like ' + '.' * length


@shared_task(bind=True)
def ninja_attack_task(self, length: int) -> str:
    _sleep(self, length)
    return 'The sword goes' + ' SWOOSH' * length


@shared_task(bind=True)
def ninja_hide_task(self, length: int) -> str:
    _sleep(self, length)
    return 'The sound is' + ' Z' * length
