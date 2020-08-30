# noinspection PyUnresolvedReferences
from .base import *

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

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://02681a846266431889b46a7515f035c7@o440352.ingest.sentry.io/5409078",
    integrations=[DjangoIntegration()],
    send_default_pii=True
)

env = os.environ
if env.get('EMAIL_HOST_USER') and env.get('EMAIL_HOST_PASSWORD'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_USE_TLS = env.get('EMAIL_USE_TLS', True) not in (False, 0, '0', 'f', 'F', 'false', 'FALSE', 'off', 'disabled')
    EMAIL_PORT = env.get('EMAIL_PORT', 587)
    EMAIL_HOST_USER = env['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = env['EMAIL_HOST_PASSWORD']


try:
    from .local import *
except ImportError:
    pass
