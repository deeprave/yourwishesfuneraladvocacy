# noinspection PyUnresolvedReferences

from ..base import *
from ..base import env
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


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

TEMPLATE_LOADERS = [
    ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS)
]

# email handling

if env.is_all_set('EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
    EMAIL_PORT = env.int('EMAIL_PORT', 587)
    EMAIL_HOST_USER = env['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = env['EMAIL_HOST_PASSWORD']

# media files handling

if env.is_all_set('AWS_S3_ACCESS_KEY_ID', 'AWS_S3_SECRET_ACCESS_KEY', 'AWS_STORAGE_BUCKET_NAME', 'AWS_API_ENDPOINT'):
    AWS_ACCESS_KEY_ID = env['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = env['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = env['AWS_STORAGE_BUCKET_NAME']
    AWS_API_ENDPOINT = env['AWS_API_ENDPOINT']
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.{AWS_API_ENDPOINT}"

    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    import logging
    for var in ('AWS_S3_ACCESS_KEY_ID', 'AWS_S3_SECRET_ACCESS_KEY', 'AWS_S3_CUSTOM_DOMAIN'):
        logging.warning(f'{var}={vars()[var]}')

BASE_URL = 'https://yourwishesfuneraladvocacy.com.au'

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
