from time import sleep

from celery import shared_task


@shared_task()
def pirate_noise_task(length: int):
    sleep(length)
    return f'The pirate says YA' + 'R' * length