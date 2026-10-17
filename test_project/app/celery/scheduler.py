from django_spire.celery.scheduler import CeleryScheduler, SchedulerTask

from test_project.app.celery.celery.managers import (
    NinjaAttackCeleryTaskManager,
    PirateSongCeleryTaskManager,
)


class TestProjectScheduler(CeleryScheduler):
    tasks = [
        SchedulerTask(PirateSongCeleryTaskManager, crontab='*/5 * * * *', kwargs={'length': 2}),
        SchedulerTask(NinjaAttackCeleryTaskManager, crontab='0 */6 * * *', kwargs={'length': 1}),
    ]
