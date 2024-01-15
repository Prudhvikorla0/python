from .base import *

DEBUG = True

ALLOWED_HOSTS += [
    '0.0.0.0',
    'localhost',
    '127.0.0.1'
]

INSTALLED_APPS += [
    'drf_yasg',
]

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'scheme': "bearer",
        }
    }
}

REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon'] = '500/min'

# NEOMODEL_NEO4J_BOLT_URL = f'bolt://{NEO4J_USERNAME}:{NEO4J_PASSWORD}@graphdb:7687'
# neo_config.DATABASE_URL = NEOMODEL_NEO4J_BOLT_URL

SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(days=14)
SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] = timedelta(days=14)

HUB_TOPIC_ID = "0.0.47654162"

PYINSTRUMENT_PROFILE_DIR = 'profiles'
ENABLE_PROFILING = False
if ENABLE_PROFILING:
    MIDDLEWARE += ['pyinstrument.middleware.ProfilerMiddleware']

AWS_DEFAULT_REGION = 'eu-central-1'
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""


#Version info
VERSION = 1.2
