from .base import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

ENVIRONMENT = 'production'
DEBUG = False

REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon'] = '5/min'

HEDERA_NETWORK = 3  # For Mainnet

AWS_DEFAULT_REGION = 'eu-central-1'
AWS_ACCESS_KEY_ID = config.get('libs', 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config.get('libs', 'AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config.get('libs', 'AWS_STORAGE_BUCKET_NAME')
AWS_QUERYSTRING_AUTH = False
AWS_PRELOAD_METADATA = True
AWS_DEFAULT_ACL = 'public-read'
DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
DEFAULT_S3_PATH = 'media'
MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME

sentry_sdk.init(
    dsn=config.get('libs', 'SENTRY_DSN'),
    integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
    traces_sample_rate=1.0,
    environment=ENVIRONMENT,
)
sentry_sdk.set_tag('deployment', DEPLOYMENT)

#Version info
VERSION = 1.2
