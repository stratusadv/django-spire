import os

from test_project.postgres_settings import *


DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('TEST_DATABASE_NAME', 'django_spire_test'),
    'USER': os.getenv('TEST_DATABASE_USER', 'postgres'),
    'PASSWORD': os.getenv('TEST_DATABASE_PASSWORD', 'postgres'),
    'HOST': os.getenv('TEST_DATABASE_HOST', 'localhost'),
    'PORT': os.getenv('TEST_DATABASE_PORT', '5439'),
    'ATOMIC_REQUESTS': os.getenv('TEST_ATOMIC_REQUESTS', False),
}

CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

# Keep metric click tracking off during tests (no background threads / DB writes).
DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY = ''
DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY = ''
