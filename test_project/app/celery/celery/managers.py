from django_spire.celery.manager import BaseCeleryTaskManager


class PirateSongCeleryTaskManager(BaseCeleryTaskManager):
    task_name = "test_project.app.celery.celery.tasks.pirate_noise_task"
    display_name = "Pirate Song"


class NinjaAttackCeleryTaskManager(BaseCeleryTaskManager):
    task_name = "test_project.app.celery.celery.tasks.ninja_attack_task"
    display_name = "Ninja Attack"
