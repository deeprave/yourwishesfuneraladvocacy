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


try:
    from .local import *
except ImportError:
    pass
