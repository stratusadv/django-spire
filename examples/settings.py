import os
import logging
import sys


logging.basicConfig(
    format='[%(asctime)-15s] Django Spire: "%(message)s"',
    datefmt='%d/%b/%Y %H:%M:%S'
)

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

WSGI_APPLICATION = 'examples.wsgi.application'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Email Settings
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_TEMPLATE_ID = False
DEFAULT_FROM_EMAIL = 'Stratus ADV <noreply@stratusadv.com>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_glue',
    'django_spire',
    'django_spire.authentication',
    'django_spire.breadcrumb',
    'django_spire.comment',
    'django_spire.core',
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
    'django_spire.user_account',
    'examples',
    'examples.component',
]

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

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
    }
}

ROOT_URLCONF = 'examples.urls'

SECRET_KEY = 'django_spire_secret_key_of_secrets'

USE_TZ = True
TIME_ZONE = 'America/Edmonton'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'examples/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_glue.context_processors.glue',
                'django_spire.context_processors.spire'
            ],
            'builtins': [
            ],
            'debug': DEBUG,
        },
    },
]

STATIC_URL = '/static/'
