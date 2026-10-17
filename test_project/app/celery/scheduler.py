from django_spire.celery.scheduler import CeleryScheduler, SchedulerTask

from test_project.app.celery.celery.managers import (
    ConvertFilesToModelObjectsCeleryTaskManager,
    NinjaAttackCeleryTaskManager,
    PirateSongCeleryTaskManager,
    ProcessReadyNotificationsCeleryTaskManager,
)


class TestProjectScheduler(CeleryScheduler):
    tasks = [
        SchedulerTask(PirateSongCeleryTaskManager, crontab='*/5 * * * *', kwargs={'length': 2}),
        SchedulerTask(NinjaAttackCeleryTaskManager, crontab='0 */6 * * *', kwargs={'length': 1}),
        SchedulerTask(ProcessReadyNotificationsCeleryTaskManager, crontab='0 0 * * 6'),
        SchedulerTask(ConvertFilesToModelObjectsCeleryTaskManager, crontab='0 0 * * 6'),
    ]
