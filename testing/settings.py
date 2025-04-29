from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = 'testing.urls'

# AI Chat Config
AI_CHAT_WORKFLOW_CLASS = 'example.ai.chat.intelligence.chat_workflow.ChatWorkflow'
AI_CHAT_WORKFLOW_NAME = 'Rubber Ducky'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'django_spire.ai',
    'django_spire.ai.chat',

    'django_spire.auth',
    'django_spire.auth.mfa',
    'django_spire.auth.group',
    'django_spire.auth.user',
    'django_spire.contrib.breadcrumb',
    'django_spire.comment',
    'django_spire.core',
    'django_spire.file',
    'django_spire.contrib.form',
    'django_spire.contrib.gamification',
    'django_spire.contrib.help',
    'django_spire.history',
    'django_spire.history.activity',
    'django_spire.history.viewed',

    'django_spire.notification',
    'django_spire.notification.app',
    'django_spire.notification.email',

    'django_spire.contrib.options',
    'django_spire.contrib.pagination',
    'django_spire.speech_to_text',

    'testing.dummy',
]

DEBUG = True

SECRET_KEY = 'Django-Spire-Super-Secret-Key-for-Testing'

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
    'django_glue.middleware.DjangoGlueMiddleware'
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
                'django_glue.context_processors.django_glue'
            ],
            'builtins': [
            ],
            'debug': DEBUG,
        },
    },
]
