# noinspection PyUnresolvedReferences

from ..base import *
from ..base import env
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

def _var_is_set(_var: str):
    return _var in env


def _vars_are_set(*_vars):
    return all(v in env for v in _vars)


DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '::1',
    '172.105.169.83',
    'ywfa.com.au',
    'www.ywfa.com.au',
    'yourwishesfuneraladvocacy.com.au',
    'www.yourwishesfuneraladvocacy.com.au',
]


# email handling

if _vars_are_set('EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
    EMAIL_PORT = env.int('EMAIL_PORT', 587)
    EMAIL_HOST_USER = env['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = env['EMAIL_HOST_PASSWORD']

# media files handling

if _vars_are_set('S3_API_KEY', 'S3_API_SECRET', 'S3_API_ENDPOINT', 'S3_API_BUCKET'):
    AWS_STORAGE_BUCKET_NAME = env['S3_API_BUCKET']
    AWS_S3_ACCESS_KEY_ID = env['S3_API_KEY']
    AWS_S3_SECRET_ACCESS_KEY = env['S3_API_SECRET']
    AWS_API_ENDPOINT = env['S3_API_ENDPOINT']
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.{AWS_API_ENDPOINT}"

    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# alerts & monitoring

sentry_sdk.init(
    dsn="https://02681a846266431889b46a7515f035c7@o440352.ingest.sentry.io/5409078",
    integrations=[DjangoIntegration()],
    send_default_pii=True
)


try:
    from .local import *
except ImportError:
    pass
