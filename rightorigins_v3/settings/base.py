"""
Django settings for rightorigins_v3 project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path
from configparser import RawConfigParser
from datetime import timedelta
from neomodel import config as neo_config
from pymongo import MongoClient

PROJECT_NAME = 'rightorigins_v3'

SECRETS_DIR = Path('/etc/secret') / PROJECT_NAME
SECRET_FILE = SECRETS_DIR / 'secret.ini'

config = RawConfigParser(allow_no_value=True)
config.read(SECRET_FILE)

ENVIRONMENT = config.get('app', 'ENVIRONMENT')
DEPLOYMENT = config.get('app', 'DEPLOYMENT')
ENTERPRISE_MODE = False

ROOT_URL = config.get('app', 'ROOT_URL')
FRONT_ROOT_URL = config.get('app', 'FRONT_ROOT_URL')
TRACKER_ROOT_URL = config.get('app', 'TRACKER_ROOT_URL')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get('django', 'SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]


# Application definition

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    # External Core Libraries
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework_simplejwt',
    # 'fcm_django',
    'django_neomodel',

    # External utility libraries
    'django_extensions',
    'modeltranslation',
    'phonenumber_field',
    'admin_extra_buttons',
    'django_celery_beat',

    # Internal Apps (V1)
    'v1.accounts',
    'v1.apiauth',
    'v1.blockchain',
    'v1.bulk_templates',
    'v1.claims',
    'v1.dashboard',
    'v1.dynamic_forms',
    'v1.nodes',
    'v1.notifications',
    'v1.products',
    'v1.supply_chains',
    'v1.tenants',
    'v1.transactions',
    'v1.tracker',
    'v1.risk',
    'v1.consumer_interface',
    'v1.questionnaire',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # CORS header middlewares
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',

]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'base.authentication.CustomAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/min'
    },
    'EXCEPTION_HANDLER':
        'base.exception_handler.custom_exception_handler',
    'DATETIME_FORMAT': '%s',
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': (
        'base.response.ApiRenderer',),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}


REST_USE_JWT = True
JWT_AUTH_COOKIE = 'rightorigins-v3-auth'
JWT_AUTH_REFRESH_COOKIE = 'rightorigins-v3-refresh-token'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

ROOT_URLCONF = 'rightorigins_v3.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rightorigins_v3.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config.get('database', 'DB_NAME'),
        'USER': config.get('database', 'DB_USER'),
        'PASSWORD': config.get('database', 'DB_PASSWORD'),
        'PORT': '5432',
        'HOST': config.get('database', 'HOST')
    }
}

NEO4J_USERNAME = 'neo4j'
NEO4J_PASSWORD = 'rightorigins_v3_pass'
NEOMODEL_NEO4J_BOLT_URL = f'bolt://{NEO4J_USERNAME}:{NEO4J_PASSWORD}@localhost:7687'
NEOMODEL_ENCRYPTED_CONNECTION = False
neo_config.DATABASE_URL = NEOMODEL_NEO4J_BOLT_URL
# you are free to add this configurations
NEOMODEL_SIGNALS = True
NEOMODEL_FORCE_TIMEZONE = False
NEOMODEL_ENCRYPTED_CONNECTION = True
NEOMODEL_MAX_POOL_SIZE = 50

REDIS_URL = config.get('database', 'REDIS_URL', fallback='redis://127.0.0.1')
REDIS_PORT = config.get('database', 'REDIS_PORT', fallback=6379)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}:{REDIS_PORT}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "rightorigins_v3_django"
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = "accounts.CustomUser"

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_THOUSAND_SEPARATOR = True
USE_I18N = True
USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    BASE_DIR / 'locale',
)
LANGUAGES = [
    ('en-us', 'English US'),
    ('en-uk', 'English UK'),
    ('fr', 'French'), 
    ('nl', 'Dutch')
]

MODELTRANSLATION_DEFAULT_LANGUAGE = 'en-us'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Hash id encoding.

HASHID_SALT = config.get('django', 'HASHID_SALT')
HASHID_MIN_LENGTH = 10
HASHID_ALPHABETS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
ACCESS_TOKEN_LENGTH = 90
OTP_LENGTH = 6

# Cors setup

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
)
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-disposition',
    'content-type',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'user-id', 
    'node-id', 
    'tenant-id', 
    'token',
    'language',
    'timezone',
]

CORS_PREFLIGHT_MAX_AGE = 86400
CORS_ALLOW_CREDENTIALS = True


# Email setup

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config.get('email', 'EMAIL_HOST')
EMAIL_PORT = config.get('email', 'EMAIL_PORT')
EMAIL_HOST_USER = config.get('email', 'EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config.get('email', 'EMAIL_HOST_PASSWORD')
FROM_EMAIL = EMAIL_HOST_USER
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False


# celery setup

CELERY_BROKER_URL = f'{REDIS_URL}:{REDIS_PORT}'
CELERY_TIMEZONE = 'UTC'
CELERY_DEFAULT_QUEUE = 'low'
CELERY_ROUTES = {
    'send_email': {'queue': 'high'},
    'send_sms': {'queue': 'high'},
}
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# hedera settings
HEDERA_NETWORK = 1  # For testnet
BLOCKCHAIN_CLIENT_ID = "4AemO8oBMlKx3ElL6Y09"
BLOCKCHAIN_PRIVATE_KEY_PATH = SECRETS_DIR / 'hedera'
BLOCKCHAIN_ENCRYPTION_KEY = config.get('blockchain', 'BLOCKCHAIN_ENCRYPTION_KEY')
BC_MIDDLEWARE_BASE_URL = "https://v1.api.bcmiddleware.cied.in/v1/registry/requests/"

TREASURY_ACCOUNT_ID = config.get('blockchain', 'TREASURY_ACCOUNT_ID')
TREASURY_ENCRYPED_PRIVATE = config.get('blockchain', 'TREASURY_ENCRYPED_PRIVATE')
HUB_TOPIC_ID = "0.0.47654162"
IP_API_URL = "https://ipapi.co/{ip}/json/"


# RO-AI Secrets
ROAI_BASE_URL = config.get('roai', 'ROAI_BASE_URL', fallback="")
ROAI_BEARER_TOKEN = config.get('roai', 'ROAI_BEARER_TOKEN', fallback="")
ROAI_CLIENT_ID = config.get('roai', 'ROAI_CLIENT_ID', fallback="")

#Mongodb setup
""""
mongo         : to open mongodb cli in terminal
use <db_name> : to create database / select the database.

below command used to create user under the selected db.
db.createUser({
  user: <username>,
  pwd: <password>,
  roles: ["readWrite"]
}) 
"""

# Database varibales for mongodb connection.

MONGO_HOST = config.get('database', 'HOST')
MONGO_PORT = 27017
MONGO_DB_NAME = config.get('database', 'DB_NAME')
MONGO_USERNAME= config.get('database', 'DB_USER')
MONGO_USER_PASSWORD = config.get('database', 'DB_PASSWORD')

# Creating client connection with mongodb.
client = MongoClient(f"mongodb://{MONGO_USERNAME}:{MONGO_USER_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}")

# Geting database.

MONGO_DB = client[MONGO_DB_NAME]


#Version info
VERSION = 1.2

# celerybeat tasks
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'update_country_score': {
        'task': 'update_country_score',
        'schedule': crontab(minute=0, hour=0)
    }, 
    'update_sc_risk_score': {
        'task': 'update_sc_risk_score',
        'schedule': crontab(minute=0, hour=1)
    }, 
    'sync_roai_standards': {
        'task': 'sync_roai_standards',
        'schedule': crontab(minute=0, hour=2)
    }, 
}

OPEN_AI_ASSISTANT_ID = config.get('openai', 'OPEN_AI_ASSISTANT_ID')
OPEN_AI_API_KEY = config.get('openai', 'OPEN_AI_API_KEY')
