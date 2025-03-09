from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = 'testing.urls'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'django_spire.ai',
    'django_spire.core',
    'django_spire.authentication',
    'django_spire.authentication.mfa',
    'django_spire.breadcrumb',
    'django_spire.comment',
    'django_spire.file',
    'django_spire.form',
    'django_spire.gamification',
    'django_spire.help',
    'django_spire.history',
    'django_spire.maintenance',
    'django_spire.notification',
    'django_spire.options',
    'django_spire.pagination',
    'django_spire.permission',
    'django_spire.search',
    'django_spire.seeding',
    'django_spire.user_account',

    'testing.dummy'
]

DEBUG = True

SECRET_KEY = 's80FyoHWwOFTSQqsePJMKSAoUxZLkerXrU68v8LHfZDiuIOqXw'
SENDGRID_TEMPLATE_ID = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path(BASE_DIR, 'test.db')
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_glue.middleware.GlueMiddleware'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(BASE_DIR / 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_glue.context_processors.glue'
            ],
            'builtins': [
            ],
            'debug': DEBUG,
        },
    },
]
