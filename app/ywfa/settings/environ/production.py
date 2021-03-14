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

# add template caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS)
]

# email handling

if 'EMAIL_URL' in env:
   vars().update(env.email_url())
elif env.is_all_set('EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
    EMAIL_PORT = env.int('EMAIL_PORT', 587)
    EMAIL_HOST_USER = env['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = env['EMAIL_HOST_PASSWORD']

BASE_URL = 'https://yourwishesfuneraladvocacy.com.au'

# alerts & monitoring

if 'SENTRY_DSN' in env:
    sentry_sdk.init(
        dsn=env['SENTRY_DSN'],
        integrations=[DjangoIntegration()],
        send_default_pii=True
    )
