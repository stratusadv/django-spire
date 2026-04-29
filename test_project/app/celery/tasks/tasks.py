from time import sleep

from celery import shared_task


@shared_task()
def pirate_noise_task(length: int):
    sleep(length)
    return f'The pirate says YA' + 'R' * length


@shared_task()
def pirate_cannon_task(length: int):
    sleep(length)
    return f'The cannon goes' + ' BOOM' * length


@shared_task()
def pirate_song_task(length: int):
    sleep(length)
    return f'The song sounds like' + ' YO HO' * length


@shared_task()
def ninja_move_task(length: int):
    sleep(length)
    return f'The ninja moves like ' + '.' * length


@shared_task()
def ninja_attack_task(length: int):
    sleep(length)
    return f'The sword goes' + ' SWOOSH' * length


@shared_task()
def ninja_hide_task(length: int):
    sleep(length)
    return f'The sound is' + ' Z' * length
