from __future__ import annotations

import os
import logging
import sys

from pathlib import Path

logging.basicConfig(
    format='[%(asctime)-15s] Django Spire: "%(message)s"',
    datefmt='%d/%b/%Y %H:%M:%S'
)

ADMINS = [
    ('Stratus', 'stratus@stratusadv.com')
]

if os.getenv('DJANGO_DEBUG', 'False') == 'True':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '0.0.0.0,127.0.0.1,localhost').split(',')

ASGI_APPLICATION = 'test_project.asgi.application'
WSGI_APPLICATION = 'test_project.wsgi.application'

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Notification Settings
NOTIFICATION_THROTTLE_RATE_PER_MINUTE = 100

# Email Settings
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_TEMPLATE_ID = os.getenv('SENDGRID_TEMPLATE_ID')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# SMS Notification Settings
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
TWILIO_SMS_BATCH_SIZE = 100

# AI Chat Config
AI_PERSONA_NAME = 'Rubber Ducky'
AI_CHAT_DEFAULT_CALLABLE = 'test_project.apps.ai.chat.intelligence.workflows.chat_workflow.chat_workflow'
AI_SMS_CONVERSATION_DEFAULT_CALLABLE = 'test_project.apps.ai.sms.intelligence.workflows.sms_conversation_workflow.sms_conversation_workflow'

# Maintenance Mode
MAINTENANCE_MODE = True

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

INSTALLED_APPS = [
    'django_browser_reload',
    'django_watchfiles',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'storages',
]

INSTALLED_APPS += [
    'django_spire.ai',
    'django_spire.ai.chat',
    'django_spire.ai.context',
    'django_spire.ai.sms',

    'django_spire.auth',
    'django_spire.auth.mfa',
    'django_spire.auth.group',
    'django_spire.auth.user',
    'django_spire.contrib.breadcrumb',
    'django_spire.comment',
    'django_spire.core',
    'django_spire.contrib.session',
    'django_spire.file',
    'django_spire.contrib.form',
    'django_spire.contrib.gamification',
    'django_spire.contrib.help',
    'django_spire.help_desk',
    'django_spire.history',
    'django_spire.history.activity',
    'django_spire.history.viewed',

    'django_spire.knowledge',

    'django_spire.notification',
    'django_spire.notification.app',
    'django_spire.notification.email',
    'django_spire.notification.sms',
    'django_spire.notification.push',

    'django_spire.contrib.options',
    'django_spire.contrib.ordering',
    'django_spire.contrib.pagination',

    'django_spire.theme',
]

DJANGO_SPIRE_AUTH_CONTROLLERS = {
    'ai_chat': 'django_spire.ai.chat.auth.controller.BaseAiChatAuthController',
    'help_desk': 'django_spire.help_desk.auth.controller.BaseHelpDeskAuthController',
    'knowledge': 'test_project.apps.knowledge.auth.controller.KnowledgeAuthController',
}

INSTALLED_APPS += [
    'test_project.apps.ai',
    'test_project.apps.comment',
    'test_project.apps.file',
    'test_project.apps.help_desk',
    'test_project.apps.home',
    'test_project.apps.landing',
    'test_project.apps.ordering',
    'test_project.apps.history',
    'test_project.apps.notification',
    'test_project.apps.model_and_service',
    'test_project.apps.queryset_filtering',
]

INSTALLED_APPS += [
    'django_glue',
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django_glue.middleware.DjangoGlueMiddleware',
    'django_spire.core.middleware.MaintenanceMiddleware',
    'django_spire.profiling.middleware.ProfilingMiddleware',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

ROOT_URLCONF = 'test_project.urls'

LOGIN_URL = 'django_spire:auth:admin:login'
LOGIN_REDIRECT_SUCCESS_URL = 'home:page:home'
LOGIN_REDIRECT_URL = 'django_spire:auth:redirect:login'
LOGOUT_REDIRECT_URL = 'django_spire:auth:admin:login'

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
            str(BASE_DIR / 'test_project/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_glue.context_processors.django_glue',
                'django_spire.core.context_processors.django_spire',
                'django_spire.core.context_processors.theme_context',
                'test_project.apps.core.context_processors.test_project',
                'test_project.apps.core.context_processors.django_spire',
            ],
            'builtins': [
            ],
            'debug': DEBUG,
        },
    },
]

# Storages - We are using Digital Ocean, which uses AWS S3 service
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.getenv('AWS_REGION_NAME')

AWS_S3_FILE_OVERWRITE = False
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

BASE_FOLDER_NAME = 'django-spire'

# 25MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [str(BASE_DIR / 'test_project/static')]
STATIC_ROOT = str(BASE_DIR / 'static')
