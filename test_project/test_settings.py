import os

from test_project.postgres_settings import *


DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('TEST_DATABASE_NAME', 'django_spire_test'),
    'USER': os.getenv('TEST_DATABASE_USER', 'postgres'),
    'PASSWORD': os.getenv('TEST_DATABASE_PASSWORD', 'postgres'),
    'HOST': os.getenv('TEST_DATABASE_HOST', 'localhost'),
    'PORT': os.getenv('TEST_DATABASE_PORT', '5439'),
}
