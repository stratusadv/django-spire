import os

from test_project.base_settings import *

from test_project.apps.sync.config import TABLET_COUNT_MAX


TEST_PROJECT = BASE_DIR / 'test_project'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    },
}

_SYNC_BACKEND = os.getenv('SYNC_DB_BACKEND', 'sqlite')

_TABLET_PORTS = {1: '5433', 2: '5435', 3: '5436', 4: '5437', 5: '5438'}

if _SYNC_BACKEND == 'postgres':
    for _i in range(1, TABLET_COUNT_MAX + 1):
        _key = f'tablet_{_i}'
        _prefix = f'SYNC_TABLET_{_i}'
        DATABASES[_key] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv(f'{_prefix}_DB_NAME', f'sync_tablet_{_i}'),
            'USER': os.getenv(f'{_prefix}_DB_USER', 'sync'),
            'PASSWORD': os.getenv(f'{_prefix}_DB_PASSWORD', 'sync'),
            'HOST': os.getenv(f'{_prefix}_DB_HOST', 'localhost'),
            'PORT': os.getenv(f'{_prefix}_DB_PORT', _TABLET_PORTS[_i]),
        }
    DATABASES['cloud'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('SYNC_CLOUD_DB_NAME', 'sync_cloud'),
        'USER': os.getenv('SYNC_CLOUD_DB_USER', 'sync'),
        'PASSWORD': os.getenv('SYNC_CLOUD_DB_PASSWORD', 'sync'),
        'HOST': os.getenv('SYNC_CLOUD_DB_HOST', 'localhost'),
        'PORT': os.getenv('SYNC_CLOUD_DB_PORT', '5434'),
    }
else:
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
