from test_project.base_settings import *

from test_project.apps.sync.config import TABLET_COUNT_MAX


TEST_PROJECT = BASE_DIR / 'test_project'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'django_spire_test_project.db',
    }
}

for _i in range(1, TABLET_COUNT_MAX + 1):
    DATABASES[f'tablet_{_i}'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': TEST_PROJECT / f'db_sync_tablet_{_i}.sqlite3',
    }

DATABASES['cloud'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': TEST_PROJECT / 'db_sync_cloud.sqlite3',
}

DATABASE_ROUTERS = [
    'test_project.apps.sync.router.SyncDemoRouter',
]
