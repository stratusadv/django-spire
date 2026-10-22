import os

# Celery

_CELERY_AMQP_HOST = os.getenv('CELERY_AMQP_HOST')
_CELERY_PGSQL_HOST = os.getenv('CELERY_PGSQL_HOST')

if _CELERY_AMQP_HOST:
    CELERY_BROKER_URL = 'amqp://{user}:{password}@{host}:5672//'.format(
        user=os.getenv('CELERY_AMQP_USER'),
        password=os.getenv('CELERY_AMQP_PASSWORD'),
        host=_CELERY_AMQP_HOST,
    )
else:
    CELERY_BROKER_URL = 'memory://'

if _CELERY_PGSQL_HOST:
    CELERY_RESULT_BACKEND = 'db+postgresql://{user}:{password}@{host}:{port}/{database}'.format(
        user=os.getenv('CELERY_PGSQL_USER'),
        password=os.getenv('CELERY_PGSQL_PASSWORD'),
        host=_CELERY_PGSQL_HOST,
        port=os.getenv('CELERY_PGSQL_PORT', '5432'),
        database=os.getenv('CELERY_PGSQL_DATABASE'),
    )
else:
    CELERY_RESULT_BACKEND = 'cache+memory://'

# Celery Scheduler
DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES = ['test_project.app.celery.scheduler.TestProjectScheduler']
DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED = True

# Celery Task Sweep
DJANGO_SPIRE_CELERY_SWEEP_ENABLED = True
