from __future__ import annotations

import os
import logging
import sys

from pathlib import Path


logging.basicConfig(
    format='[%(asctime)-15s] Django Spire: "%(message)s"',
    datefmt='%d/%b/%Y %H:%M:%S'
)

if os.getenv('DJANGO_DEBUG', 'False') == 'True':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '0.0.0.0').split(',')

ASGI_APPLICATION = 'example.asgi.application'
WSGI_APPLICATION = 'example.wsgi.application'

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(BASE_DIR))

# Email Settings
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_TEMPLATE_ID = False
DEFAULT_FROM_EMAIL = 'Stratus ADV <noreply@stratusadv.com>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'django_glue',

    'django_spire.ai',
    'django_spire.authentication',
    'django_spire.authentication.mfa',
    'django_spire.breadcrumb',
    'django_spire.comment',
    'django_spire.core',
    'django_spire.file',
    'django_spire.form',
    'django_spire.gamification',
    'django_spire.help',
    'django_spire.history',
    'django_spire.maintenance',
    'django_spire.modal',
    'django_spire.notification',
    'django_spire.options',
    'django_spire.pagination',
    'django_spire.permission',
    'django_spire.search',
    'django_spire.user_account',

    'example',
    'example.authentication',
    'example.authentication.mfa',
    'example.breadcrumb',
    'example.file',
    'example.form',
    'example.gamification',
    'example.help',
    'example.history',
    'example.maintenance',
    'example.modal',
    'example.notification',
    'example.options',
    'example.pagination',
    'example.permission',
    'example.search',
    'example.user_account',
    'example.user_account.profile',

    # Other
    'example.component',
    'example.cookbook',
    'example.cookbook.recipe',

    'debug_toolbar'
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_glue.middleware.GlueMiddleware',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}

ROOT_URLCONF = 'example.urls'

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'secret')

SITE_ID = 1

TIME_ZONE = 'America/Edmonton'
USE_TZ = True

DEBUG_TOOLBAR_CONFIG = {
    'INSERT_BEFORE': '</head>',
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(BASE_DIR / 'core/templates'),
            str(BASE_DIR / 'example/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_glue.context_processors.glue',
                'django_spire.core.context_processors.spire'
            ],
            'builtins': [
            ],
            'debug': DEBUG,
        },
    },
]

STATIC_URL = '/static/'
