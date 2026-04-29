from django_spire.celery.manager import BaseCeleryTaskManager


class PirateSongCeleryTaskManager(BaseCeleryTaskManager):
    task_name = "test_project.app.celery.tasks.pirate_noise_task"
    display_name = "Pirate Song"
    estimated_completion_seconds = 120


class NinjaAttackCeleryTaskManager(BaseCeleryTaskManager):
    task_name = "test_project.app.celery.tasks.ninja_attack_task"
    display_name = "Ninja Attack"
    estimated_completion_seconds = 500
