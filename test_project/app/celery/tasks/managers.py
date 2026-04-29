from django_spire.celery.manager import BaseCeleryTaskManager


class PirateSongCeleryTaskManager(BaseCeleryTaskManager):
    task_name = "pirate_song_task"
    display_name = "Pirate Song"


class NinjaAttackCeleryTaskManager(BaseCeleryTaskManager):
    task_name = "ninja_attack_task"
    display_name = "Ninja Attack"
